"""관찰 판정, 보행 유형 판정과 설명 문장.

유형과 근거 지표는 전문가 자료 3종을 따른다.
- T1 좌·우 체중 부하 불균형: 정적·동적 족저압 비율(주), 입각기·한발 지지 시간(보조)
- T2 좌·우 보장 차이: 보장(주, 보행검사), 걸음 시간(인솔 대리 지표)·입각기·보행 속도(보조)
- T3 정상 보행 유지: T1·T2 어느 쪽에도 해당하지 않을 때
T3 자료의 '잠재적 문제'(리듬 불규칙·압력 패턴 변화·속도 저하)는 유형과 별개로 살펴볼 점으로 낸다.
문장은 locale 파일에서 온다. AI 호출은 하지 않는다.
"""
from dataclasses import dataclass

from app.core.locales import translate
from app.domain.analysis.metrics import Metric, Thresholds

ORDER = ("M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "M09", "M10")
WATCH = ("M07", "M08", "M10")


@dataclass(frozen=True)
class TypeRule:
    code: str
    primary: tuple[str, ...]
    support: tuple[str, ...]


TYPE_RULES = (
    TypeRule("T1", primary=("M01", "M02"), support=("M03", "M04")),
    TypeRule("T2", primary=("M09",), support=("M05", "M03", "M10")),
)
MAINTAIN = "T3"
# T3 는 좌우 차이가 기준 안쪽이라는 근거를 보여 준다.
MAINTAIN_EVIDENCE = ("M01", "M02", "M09", "M06")


def _fmt(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def _side(m: Metric) -> dict:
    """값이 큰 쪽·작은 쪽 문구."""
    big_is_right = (m.right or 0) > (m.left or 0)
    return {
        "big": translate("side.right" if big_is_right else "side.left"),
        "small": translate("side.left" if big_is_right else "side.right"),
    }


def _hit_text(metric_id: str, key: str, params: dict) -> dict:
    return {
        "head": translate(f"obs.{metric_id}.{key}.head", **params),
        "text": translate(f"obs.{metric_id}.{key}.text", **params),
    }


def _observe(metric_id: str, m: Metric, th: Thresholds) -> dict:
    params = {
        "left": _fmt(m.left, 2 if m.unit == "s" else (0 if m.unit == "cm" else 1)),
        "right": _fmt(m.right, 2 if m.unit == "s" else (0 if m.unit == "cm" else 1)),
        "pct": _fmt(m.diff_pct), "value": _fmt(m.value, 2 if m.unit == "m/s" else 0),
        **_side(m), **{k: ("-" if v is None else v) for k, v in m.extra.items()},
    }
    hit, status = _JUDGES[metric_id](m, th)
    if metric_id == "M08" and hit:
        params["foot"] = translate("side.left" if _front_hit(m.left, status, th) else "side.right")
    key = status if hit else "ok"
    return {
        "metric": metric_id, "hit": hit, "status": translate(f"status.{status}"),
        **_hit_text(metric_id, key, params),
    }


def _diff(threshold_name: str):
    def judge(m: Metric, th: Thresholds) -> tuple[bool, str]:
        hit = (m.diff_pct or 0) >= getattr(th, threshold_name)
        return hit, "diff" if hit else "even"
    return judge


def _judge_cadence(m: Metric, th: Thresholds) -> tuple[bool, str]:
    return False, "info"


def _judge_cv(m: Metric, th: Thresholds) -> tuple[bool, str]:
    hit = max(m.left or 0, m.right or 0) >= th.cycle_cv_pct
    return hit, "var" if hit else "steady"


def _front_hit(value: float | None, status: str, th: Thresholds) -> bool:
    if status == "front":
        return (value or 0) >= th.front_high_pct
    return (value or 0) <= th.front_low_pct


def _judge_front(m: Metric, th: Thresholds) -> tuple[bool, str]:
    for status in ("front", "back"):
        if _front_hit(m.left, status, th) or _front_hit(m.right, status, th):
            return True, status
    return False, "balanced"


def _judge_speed(m: Metric, th: Thresholds) -> tuple[bool, str]:
    hit = (m.value or 0) < th.speed_low_mps
    return hit, "slow" if hit else "ok"


_JUDGES = {
    "M01": _diff("static_share_diff_pp"),
    "M02": _diff("dynamic_share_diff_pp"),
    "M03": _diff("stance_diff_pct"),
    "M04": _diff("single_support_diff_pct"),
    "M05": _diff("step_time_diff_pct"),
    "M06": _judge_cadence,
    "M07": _judge_cv,
    "M08": _judge_front,
    "M09": _diff("step_length_diff_pct"),
    "M10": _judge_speed,
}


def observe(metrics: dict[str, Metric], th: Thresholds) -> list[dict]:
    """계산된 지표마다 (관찰 여부, 상태 칩, 제목, 설명)을 만든다."""
    return [
        _observe(metric_id, metrics[metric_id], th)
        for metric_id in ORDER
        if metric_id in metrics and metrics[metric_id].ok
    ]


def classify(observations: list[dict]) -> list[dict]:
    """해당하는 보행 유형과 근거 문장. 주 지표가 하나라도 걸리면 그 유형이다."""
    by_metric = {o["metric"]: o for o in observations}
    matched: list[dict] = []
    for rule in TYPE_RULES:
        if not any(by_metric.get(m, {}).get("hit") for m in rule.primary):
            continue
        evidence = [
            by_metric[m]["text"] for m in (*rule.primary, *rule.support)
            if by_metric.get(m, {}).get("hit")
        ]
        matched.append({"code": rule.code, "evidence": evidence})
    if matched:
        return matched
    evidence = [by_metric[m]["text"] for m in MAINTAIN_EVIDENCE if m in by_metric]
    return [{"code": MAINTAIN, "evidence": evidence}]


def type_head(code: str) -> str:
    return translate(f"type.{code}.head")


def type_lead(code: str) -> str:
    return translate(f"type.{code}.lead")


def watch_points(observations: list[dict]) -> list[dict]:
    """유형과 별개로 더 살펴볼 점(T3 자료의 잠재적 문제)."""
    return [o for o in observations if o["metric"] in WATCH and o["hit"]]


def summarize(types: list[dict], watch: list[dict]) -> str:
    heads = ", ".join(type_head(t["code"]) for t in types)
    if types and types[0]["code"] == MAINTAIN:
        return translate("summary.maintain", n=len(watch)) if watch else translate("summary.none")
    return translate("summary.hit", types=heads)
