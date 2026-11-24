"""분석 파이프라인: parquet 로드 → 지표 계산 → 관찰 판정 → 보행 유형 판정 → 운동 연결 → 캐시."""
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import io
from app.core.errors import ConflictError, NotFoundError, UnprocessableError
from app.domain.analysis import crud, explain, metrics
from app.domain.analysis.schemas import Analysis, LinkOut, MetricOut, Observation, WindowOut
from app.domain.record import crud as record_crud


async def analyze(session: AsyncSession, record_id: str) -> Analysis:
    record = await record_crud.get(session, record_id)
    if record is None:
        raise NotFoundError("record.not_found")

    rule_set = await crud.active_rule_set(session)
    if rule_set is None:
        raise ConflictError("analysis.no_active_rule_set")

    cached = await crud.get_cached(session, record_id, rule_set.id)
    if cached is not None:
        return Analysis.model_validate(cached.payload | {"computed_at": cached.computed_at})

    thresholds = metrics.Thresholds.from_mapping(rule_set.thresholds)
    arrays = io.load(record.file_path, record.sample_rate)
    result = metrics.compute(
        arrays.time, arrays.left, arrays.right, arrays.left_sum, arrays.right_sum,
        arrays.dt, thresholds,
    )
    if result is None:
        logger.info("analysis rejected: too short record_id={}", record_id)
        raise UnprocessableError("analysis.too_short")

    all_metrics = result.metrics | metrics.walk_test_metrics(record.walk_test)
    observations = explain.observe(all_metrics, thresholds)
    types = explain.classify(observations)
    watch = explain.watch_points(observations)
    static = result.static_window
    analysis = Analysis(
        record_id=record_id,
        window=WindowOut(from_sec=result.window.from_sec, to_sec=result.window.to_sec),
        static_window=WindowOut(from_sec=static.from_sec, to_sec=static.to_sec) if static else None,
        metrics={k: MetricOut(**vars(v)) for k, v in all_metrics.items()},
        observations=[Observation(**o) for o in observations],
        links=_build_links(types, rule_set),
        watch=[Observation(**o) for o in watch],
        summary=explain.summarize(types, watch),
        rule_set_version=rule_set.version,
        rule_set_status=rule_set.status,
    )
    await _cache(session, record_id, rule_set.id, analysis)
    return analysis


def _build_links(types: list[dict], rule_set) -> list[LinkOut]:
    matched = {t["code"]: t for t in types}
    links: list[LinkOut] = []
    for rule in sorted(rule_set.links, key=lambda r: (r.sort_order, r.id)):
        found = matched.get(rule.target)
        if found is None:
            continue
        links.append(
            LinkOut(
                target=rule.target, head=explain.type_head(rule.target),
                observation=explain.type_lead(rule.target), evidence=found["evidence"],
                reason=rule.reason, exercise_ids=list(rule.exercise_ids), recheck=list(rule.recheck),
            )
        )
    if len(links) != len(matched):
        logger.warning("rule set {} has no link for some matched types: {}", rule_set.version, sorted(matched))
    return links


async def _cache(session: AsyncSession, record_id: str, rule_set_id: int, analysis: Analysis) -> None:
    payload = analysis.model_dump(mode="json", exclude={"computed_at"})
    try:
        await crud.save(session, record_id, rule_set_id, payload)
    except IntegrityError:
        # 동시에 같은 기록을 분석하면 한쪽이 진다. 값이 같으므로 무시한다.
        await session.rollback()
        logger.debug("analysis cache race ignored record_id={}", record_id)
