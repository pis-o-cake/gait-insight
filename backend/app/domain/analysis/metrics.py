"""보행 지표 M01~M10 계산.

지표 정의는 전문가 자료(docs/analysis 의 스마트인솔 상세판 3종)의 측정 항목을 따른다.
M01~M08 은 인솔 압력 신호에서, M09·M10 은 인솔로 잴 수 없어 자료가 병행 측정을 요구한
보행검사 입력값에서 나온다. 임계값은 코드에 두지 않고 활성 규칙 세트에서 받는다.
"""
from dataclasses import dataclass, field

import numpy as np

# 앞쪽 센서군. PhysioNet 센서 좌표에서 Y >= 400 인 묶음이다(0-based 인덱스).
FRONT_IDX = (5, 6, 7)
# 정적 구간 끝의 체중 이동(첫 발 떼기 직전)을 빼는 여유.
STATIC_TAIL_SEC = 0.5

SIGNAL_METRICS = ("M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08")
WALK_TEST_METRICS = ("M09", "M10")


@dataclass(frozen=True)
class Thresholds:
    """판정 기준. rule_set.thresholds 에서 읽어 만든다."""

    contact_threshold_n: float = 25.0
    analysis_trim_sec: float = 1.0
    static_min_sec: float = 5.0
    static_share_diff_pp: float = 10.0
    dynamic_share_diff_pp: float = 10.0
    stance_diff_pct: float = 8.0
    single_support_diff_pct: float = 10.0
    step_time_diff_pct: float = 8.0
    step_length_diff_pct: float = 10.0
    cycle_cv_pct: float = 6.0
    front_high_pct: float = 50.0
    front_low_pct: float = 28.0
    speed_low_mps: float = 1.0

    @classmethod
    def from_mapping(cls, raw: dict) -> "Thresholds":
        known = {f: raw[f] for f in cls.__dataclass_fields__ if f in raw}
        return cls(**{k: float(v) for k, v in known.items()})


@dataclass
class Metric:
    left: float | None
    right: float | None
    unit: str
    ok: bool
    value: float | None = None
    diff_pct: float | None = None
    reason: str | None = None
    extra: dict = field(default_factory=dict)


@dataclass
class Window:
    from_sec: float
    to_sec: float


@dataclass
class MetricSet:
    window: Window
    static_window: Window | None
    metrics: dict[str, Metric]


def _contact_intervals(total: np.ndarray, time: np.ndarray, start: int, stop: int, threshold: float) -> np.ndarray:
    """발이 바닥에 닿아 있는 구간을 (시작, 끝) 시각 배열로 돌려준다.

    구간 시작 시점에 이미 닿아 있던 부분 접촉(정적 측정 포함)은 세지 않는다(상승 엣지부터).
    구간 밖으로 걸친 마지막 접촉도 제외한다.
    """
    start = max(0, start)
    stop = min(stop, total.size)
    if stop - start < 2:
        return np.empty((0, 2), dtype=np.float64)
    on = total[start:stop] >= threshold
    t = time[start:stop]
    edges = np.flatnonzero(np.diff(on.astype(np.int8)))
    rises = edges[on[edges + 1]] + 1
    falls = edges[~on[edges + 1]] + 1
    if rises.size == 0 or falls.size == 0:
        return np.empty((0, 2), dtype=np.float64)
    falls = falls[falls > rises[0]]
    count = min(rises.size, falls.size)
    if count == 0:
        return np.empty((0, 2), dtype=np.float64)
    return np.column_stack((t[rises[:count]], t[falls[:count]]))


def _cv_pct(values: np.ndarray) -> float:
    if values.size < 2:
        return float("nan")
    mean = float(values.mean())
    if mean == 0:
        return float("nan")
    return float(values.std(ddof=1) / mean * 100)


def _pct_diff(a: float, b: float) -> float:
    base = max(a, b)
    return abs(a - b) / base * 100 if base > 0 else 0.0


def _nan_to_none(value: float, digits: int) -> float | None:
    return None if np.isnan(value) else round(float(value), digits)


def _paired(left: float, right: float, unit: str, digits: int, reason: str, extra: dict | None = None) -> Metric:
    """좌우 한 쌍 지표. 한쪽이라도 계산되지 않으면 ok=False."""
    missing = np.isnan(left) or np.isnan(right)
    return Metric(
        left=_nan_to_none(left, digits), right=_nan_to_none(right, digits), unit=unit,
        ok=not missing,
        diff_pct=None if missing else round(_pct_diff(left, right), 1),
        reason=reason if missing else None,
        extra=extra or {},
    )


def _static_window(left_sum: np.ndarray, right_sum: np.ndarray, time: np.ndarray, dt: float, th: Thresholds) -> Window | None:
    """기록 앞쪽의 양발 선 자세 구간. 첫 발 떼기 전까지가 static_min_sec 보다 짧으면 None."""
    both_on = (left_sum >= th.contact_threshold_n) & (right_sum >= th.contact_threshold_n)
    off = np.flatnonzero(~both_on)
    lift_idx = int(off[0]) if off.size else both_on.size
    start = th.analysis_trim_sec
    end = float(time[lift_idx - 1]) - STATIC_TAIL_SEC if lift_idx > 0 else 0.0
    if end - start < th.static_min_sec:
        return None
    return Window(from_sec=round(start, 2), to_sec=round(end, 2))


def _m01_static(left_sum, right_sum, window: Window | None, dt: float) -> Metric:
    if window is None:
        return Metric(left=None, right=None, unit="%", ok=False, reason="analysis.no_static")
    lo, hi = round(window.from_sec / dt), round(window.to_sec / dt)
    l, r = float(left_sum[lo:hi].mean()), float(right_sum[lo:hi].mean())
    total = l + r
    if total <= 0:
        return Metric(left=None, right=None, unit="%", ok=False, reason="analysis.no_contact")
    share_l = l / total * 100
    return Metric(
        left=round(share_l, 1), right=round(100 - share_l, 1), unit="%", ok=True,
        diff_pct=round(abs(2 * share_l - 100), 1),
        extra={"meanLeftN": round(l, 1), "meanRightN": round(r, 1)},
    )


def _m02_dynamic(left_sum, right_sum, start: int, stop: int, dt: float) -> Metric:
    l = float(left_sum[start:stop].sum() * dt)
    r = float(right_sum[start:stop].sum() * dt)
    if l <= 0 or r <= 0:
        return Metric(left=None, right=None, unit="%", ok=False, reason="analysis.no_contact")
    share_l = l / (l + r) * 100
    return Metric(
        left=round(share_l, 1), right=round(100 - share_l, 1), unit="%", ok=True,
        diff_pct=round(abs(2 * share_l - 100), 1),
        extra={"impulseLeft": round(l, 1), "impulseRight": round(r, 1)},
    )


def _single_support(own: np.ndarray, other_on: np.ndarray, time: np.ndarray, dt: float) -> float:
    """한 걸음 동안 이 발만 바닥에 닿아 있던 평균 시간."""
    if own.shape[0] == 0:
        return float("nan")
    total = 0.0
    for begin, end in own:
        lo, hi = np.searchsorted(time, (begin, end))
        total += float((~other_on[lo:hi]).sum()) * dt
    return total / own.shape[0]


def _step_times(own_starts: np.ndarray, other_starts: np.ndarray) -> np.ndarray:
    """반대 발 접촉에서 이 발 접촉까지의 시간(걸음 시간)."""
    if own_starts.size == 0 or other_starts.size == 0:
        return np.empty(0)
    idx = np.searchsorted(other_starts, own_starts, side="right") - 1
    valid = idx >= 0
    return own_starts[valid] - other_starts[idx[valid]]


def _mean(values: np.ndarray) -> float:
    return float(values.mean()) if values.size else float("nan")


def compute(
    time: np.ndarray,
    left: np.ndarray,
    right: np.ndarray,
    left_sum: np.ndarray,
    right_sum: np.ndarray,
    dt: float,
    thresholds: Thresholds,
) -> MetricSet | None:
    """인솔 신호 지표 M01~M08 을 계산한다. 완전한 걸음 주기를 못 찾으면 None."""
    th = thresholds
    duration = float(time[-1]) if time.size else 0.0
    trim_from = round(th.analysis_trim_sec / dt)
    trim_to = round((duration - th.analysis_trim_sec) / dt)
    threshold = th.contact_threshold_n

    left_full = _contact_intervals(left_sum, time, trim_from, trim_to, threshold)
    right_full = _contact_intervals(right_sum, time, trim_from, trim_to, threshold)
    if left_full.shape[0] < 2:
        return None

    window = Window(from_sec=round(float(left_full[0, 0]), 2), to_sec=round(float(left_full[-1, 0]), 2))
    start = round(window.from_sec / dt)
    stop = round(window.to_sec / dt)
    static = _static_window(left_sum, right_sum, time, dt, th)

    contacts_l = _contact_intervals(left_sum, time, start, stop + 1, threshold)
    contacts_r = _contact_intervals(right_sum, time, start, stop + 1, threshold)
    stance_l = _mean(contacts_l[:, 1] - contacts_l[:, 0])
    stance_r = _mean(contacts_r[:, 1] - contacts_r[:, 0])

    cycle_l = np.diff(left_full[:, 0])
    cycle_r = np.diff(right_full[:, 0]) if right_full.shape[0] >= 2 else np.empty(0)
    cycle_mean = _mean(np.concatenate((cycle_l, cycle_r)))

    on_l = left_sum >= threshold
    on_r = right_sum >= threshold
    single_l = _single_support(contacts_l, on_r, time, dt)
    single_r = _single_support(contacts_r, on_l, time, dt)

    step_l = _step_times(contacts_l[:, 0], contacts_r[:, 0])
    step_r = _step_times(contacts_r[:, 0], contacts_l[:, 0])

    def front_share(rows: np.ndarray) -> float:
        window_rows = rows[start:stop]
        total = float(window_rows.sum())
        if total <= 0:
            return float("nan")
        return float(window_rows[:, FRONT_IDX].sum()) / total * 100

    steps_extra = {"stepsLeft": int(contacts_l.shape[0]), "stepsRight": int(contacts_r.shape[0])}
    cycle_ok = not np.isnan(cycle_mean)
    metrics = {
        "M01": _m01_static(left_sum, right_sum, static, dt),
        "M02": _m02_dynamic(left_sum, right_sum, start, stop, dt),
        "M03": _paired(
            stance_l, stance_r, "s", 2, "analysis.too_few_steps",
            steps_extra | {
                "stancePctLeft": round(stance_l / cycle_mean * 100) if cycle_ok and not np.isnan(stance_l) else None,
                "stancePctRight": round(stance_r / cycle_mean * 100) if cycle_ok and not np.isnan(stance_r) else None,
                "swingLeft": _nan_to_none(cycle_mean - stance_l, 2) if cycle_ok else None,
                "swingRight": _nan_to_none(cycle_mean - stance_r, 2) if cycle_ok else None,
            },
        ),
        "M04": _paired(single_l, single_r, "s", 2, "analysis.too_few_steps"),
        "M05": _paired(_mean(step_l), _mean(step_r), "s", 2, "analysis.too_few_steps"),
        "M06": Metric(
            left=_nan_to_none(_mean(cycle_l), 2), right=_nan_to_none(_mean(cycle_r), 2), unit="steps/min",
            ok=cycle_ok, value=round(120 / cycle_mean) if cycle_ok else None,
            reason=None if cycle_ok else "analysis.too_few_steps",
            extra={"cycleMean": _nan_to_none(cycle_mean, 2)},
        ),
        "M07": _m07(cycle_l, cycle_r),
        "M08": _paired(front_share(left), front_share(right), "%", 1, "analysis.no_contact"),
    }
    return MetricSet(window=window, static_window=static, metrics=metrics)


def _m07(cycle_l: np.ndarray, cycle_r: np.ndarray) -> Metric:
    cv_l, cv_r = _cv_pct(cycle_l), _cv_pct(cycle_r)
    ok = cycle_l.size >= 2 and cycle_r.size >= 2 and not (np.isnan(cv_l) or np.isnan(cv_r))
    return Metric(
        left=_nan_to_none(cv_l, 1), right=_nan_to_none(cv_r, 1), unit="%", ok=ok,
        reason=None if ok else "analysis.too_few_steps",
        extra={
            "meanLeft": round(float(cycle_l.mean()), 2) if cycle_l.size else None,
            "meanRight": round(float(cycle_r.mean()), 2) if cycle_r.size else None,
        },
    )


def walk_test_metrics(walk_test: dict | None) -> dict[str, Metric]:
    """보행검사 입력값으로 M09(보장)·M10(보행 속도)를 만든다.

    압력 인솔만으로는 걸음 길이와 속도를 정확히 잴 수 없어, 전문가 자료가 요구한 대로
    영상·보행 매트·10m 보행검사 결과를 기록에 함께 넣어 둔 값을 쓴다.
    """
    if not walk_test:
        return {
            metric_id: Metric(left=None, right=None, unit=unit, ok=False, reason="analysis.no_walk_test")
            for metric_id, unit in (("M09", "cm"), ("M10", "m/s"))
        }

    step_l = float(walk_test.get("stepLengthLeftCm") or "nan")
    step_r = float(walk_test.get("stepLengthRightCm") or "nan")
    m09 = _paired(step_l, step_r, "cm", 0, "analysis.no_walk_test", {
        "diffCm": None if np.isnan(step_l) or np.isnan(step_r) else round(abs(step_l - step_r)),
        "strideCm": None if np.isnan(step_l) or np.isnan(step_r) else round(step_l + step_r),
        "method": walk_test.get("method", ""),
    })

    distance = float(walk_test.get("distanceM") or 0)
    seconds = float(walk_test.get("timeSec") or 0)
    speed_ok = distance > 0 and seconds > 0
    m10 = Metric(
        left=None, right=None, unit="m/s", ok=speed_ok,
        value=round(distance / seconds, 2) if speed_ok else None,
        reason=None if speed_ok else "analysis.no_walk_test",
        extra={"distanceM": distance, "timeSec": seconds},
    )
    return {"M09": m09, "M10": m10}
