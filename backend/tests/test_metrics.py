"""지표 계산과 보행 유형 판정 검증.

시연 기록 3개는 전문가 자료 3종의 가상 사례값에 맞춰 합성했다. 각 기록이 의도한 유형으로
판정되고, 지표가 자료의 예시값 근처에 오는지 확인한다.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.domain.analysis import explain  # noqa: E402
from app.domain.analysis.metrics import Thresholds, compute, walk_test_metrics  # noqa: E402
from tools.synth import Profile, generate  # noqa: E402

SEED = ROOT / "data" / "seed"
TH = Thresholds.from_mapping(json.loads((SEED / "rule_set.json").read_text(encoding="utf-8"))["thresholds"])
RECORDS = {r["id"]: r for r in json.loads((SEED / "records.json").read_text(encoding="utf-8"))}
# 계산 시간을 줄이려 기록 앞 2분만 합성한다. 정적 구간과 보행 지표는 길이와 무관하다.
DURATION = 120

EXPECTED = {
    # 유형 1 자료: 정적 42:58, 입각기 0.56/0.66초, 한발 지지 0.32/0.41초
    "demo-01": {"types": ["T1"], "watch": [], "M01": (42.0, 58.0), "M03": (0.56, 0.66), "M04": (0.32, 0.42)},
    # 유형 3 자료: 정적 49:51, 분당 110걸음, 입각기 0.63/0.64초
    "demo-02": {"types": ["T3"], "watch": [], "M01": (49.0, 51.0), "M03": (0.63, 0.64), "M06": 110},
    # 유형 2 자료: 보장 48/60 cm, 0.80 m/s. 왼발 걸음 시간이 짧다
    "demo-03": {"types": ["T2"], "watch": ["M10"], "M09": (48, 60), "M10": 0.80, "M05": (0.62, 0.73)},
}


def _analyze(record_id: str):
    record = RECORDS[record_id]
    synth = record["synth"]
    frame = generate(synth["seed"], Profile(**synth["profile"]), DURATION)
    left = frame[[f"l{i}" for i in range(1, 9)]].to_numpy()
    right = frame[[f"r{i}" for i in range(1, 9)]].to_numpy()
    result = compute(frame["time"].to_numpy(), left, right, frame["lsum"].to_numpy(), frame["rsum"].to_numpy(), 0.01, TH)
    assert result is not None
    return result, result.metrics | walk_test_metrics(record["walk_test"])


@pytest.mark.parametrize("record_id", list(EXPECTED))
def test_metrics_follow_expert_examples(record_id):
    expected = EXPECTED[record_id]
    _, metrics = _analyze(record_id)
    for key in ("M01", "M03", "M04", "M05", "M09"):
        if key not in expected:
            continue
        assert metrics[key].left == pytest.approx(expected[key][0], abs=0.02 if metrics[key].unit == "s" else 0.6), key
        assert metrics[key].right == pytest.approx(expected[key][1], abs=0.02 if metrics[key].unit == "s" else 0.6), key
    if "M06" in expected:
        assert metrics["M06"].value == expected["M06"]
    if "M10" in expected:
        assert metrics["M10"].value == pytest.approx(expected["M10"])


@pytest.mark.parametrize("record_id", list(EXPECTED))
def test_record_is_classified_as_intended_type(record_id):
    _, metrics = _analyze(record_id)
    observations = explain.observe(metrics, TH)
    types = explain.classify(observations)
    assert [t["code"] for t in types] == EXPECTED[record_id]["types"]
    assert all(t["evidence"] for t in types)
    assert [w["metric"] for w in explain.watch_points(observations)] == EXPECTED[record_id]["watch"]


def test_static_window_is_found_before_walking():
    result, _ = _analyze("demo-01")
    assert result.static_window is not None
    assert result.static_window.to_sec < result.window.from_sec


def test_record_without_standing_has_no_static_metric():
    frame = generate(11, Profile(period=1.09), DURATION)
    left = frame[[f"l{i}" for i in range(1, 9)]].to_numpy()
    right = frame[[f"r{i}" for i in range(1, 9)]].to_numpy()
    result = compute(frame["time"].to_numpy(), left, right, frame["lsum"].to_numpy(), frame["rsum"].to_numpy(), 0.01, TH)
    assert result.static_window is None
    assert result.metrics["M01"].ok is False
    assert result.metrics["M01"].reason == "analysis.no_static"


def test_missing_walk_test_marks_m09_m10_unavailable():
    metrics = walk_test_metrics(None)
    assert not metrics["M09"].ok and not metrics["M10"].ok
    assert metrics["M09"].reason == "analysis.no_walk_test"


def test_too_short_record_returns_none():
    """걸음이 두 번 안 되면 계산하지 않는다."""
    n = 300
    time = np.arange(n) / 100
    zeros = np.zeros((n, 8))
    assert compute(time, zeros, zeros, np.zeros(n), np.zeros(n), 0.01, TH) is None


def test_contact_below_threshold_is_not_a_step():
    """접촉 기준 아래의 잡음만 있으면 걸음으로 세지 않는다."""
    n = 60_000
    time = np.arange(n) / 100
    noise = np.full((n, 8), 1.0)
    total = noise.sum(axis=1)
    assert compute(time, noise, noise, total, total, 0.01, TH) is None
