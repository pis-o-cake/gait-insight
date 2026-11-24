"""목업 §5 합성 신호 생성기의 Python 이식.

PhysioNet gaitpdb 형식(시간, 왼발 8, 오른발 8, 좌우 합계, 100 Hz)을 흉내 낸다.
전문가 자료(docs/analysis 상세판 3종)의 측정 절차대로 앞 구간은 양발로 선 정적 측정,
그 뒤는 자유 보행이다. 정상·질환 같은 이름을 붙이지 않는다.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

SAMPLE_RATE = 100
DURATION_SEC = 600
BODY_WEIGHT_N = 700.0
SENSOR_LEFT_Y = np.array([-800, -400, -400, 0, 0, 400, 400, 800], dtype=np.float64)
SENSOR_GAIN = np.array([1.0, 0.85, 0.75, 0.9, 0.85, 0.9, 1.0, 0.8], dtype=np.float64)


@dataclass(frozen=True)
class Profile:
    period: float = 1.10
    stance_l: float = 0.62
    stance_r: float = 0.62
    scale_l: float = 1.0
    scale_r: float = 1.0
    period_var: float = 0.008
    front_shift_l: float = 0.0
    front_shift_r: float = 0.0
    # 오른발 접촉이 보행 주기 안에서 시작하는 위치. 0.5 가 아니면 좌우 걸음 시간이 달라진다.
    step_offset: float = 0.5
    # 정적 측정 구간 길이와 그동안 왼발에 실리는 체중 비율.
    static_sec: float = 0.0
    static_share_l: float = 0.5


class _Rng:
    """목업과 같은 선형 합동 생성기. 같은 seed 에 같은 신호가 나온다."""

    def __init__(self, seed: int) -> None:
        self._x = seed & 0xFFFFFFFF

    def next(self) -> float:
        self._x = (self._x * 1664525 + 1013904223) & 0xFFFFFFFF
        return self._x / 4294967296

    def array(self, size: int) -> np.ndarray:
        out = np.empty(size, dtype=np.float64)
        x = self._x
        for i in range(size):
            x = (x * 1664525 + 1013904223) & 0xFFFFFFFF
            out[i] = x / 4294967296
        self._x = x
        return out


def _build_strides(profile: Profile, rng: _Rng, duration: float) -> list[tuple[float, float]]:
    strides: list[tuple[float, float]] = []
    start, k = profile.static_sec + 0.25, 0
    while start < duration + 1:
        v = profile.period_var
        period = profile.period * (1 + v * (1 if k % 2 == 0 else -1) * 0.7 + v * (rng.next() - 0.5) * 0.8)
        strides.append((start, period))
        start += period
        k += 1
    return strides


def _stance_phase(time: np.ndarray, strides: list[tuple[float, float]], offset: float, stance: float) -> np.ndarray:
    """각 표본의 디딤 단계 진행도(0~1). 디딤이 아니면 -1."""
    phase = np.full(time.size, -1.0)
    for start, period in strides:
        begin = start + offset * period
        length = stance * period
        if length <= 0:
            continue
        lo = np.searchsorted(time, begin, side="left")
        hi = np.searchsorted(time, begin + length, side="left")
        if hi > lo:
            phase[lo:hi] = (time[lo:hi] - begin) / length
    return phase


def _force_profile(p: np.ndarray) -> np.ndarray:
    sn = np.sin(np.pi * p)
    return np.power(sn, 0.7) * (1 - 0.3 * np.power(sn, 4))


def _sensor_weights(p: np.ndarray, shift: float) -> np.ndarray:
    """(n, 8) 센서 가중치. 디딤 진행에 따라 뒤꿈치 → 앞발로 옮겨간다."""
    centre = 0.15 + 0.7 * ((SENSOR_LEFT_Y + 800) / 1600) - shift
    g = np.exp(-(((p[:, None] - centre[None, :]) / 0.22) ** 2)) * SENSOR_GAIN[None, :]
    total = g.sum(axis=1, keepdims=True)
    return np.divide(g, total, out=np.zeros_like(g), where=total > 0)


def _one_foot(time: np.ndarray, strides, offset: float, stance: float, scale: float, shift: float, rng: _Rng):
    phase = _stance_phase(time, strides, offset, stance)
    on = phase >= 0
    sensors = np.zeros((time.size, 8), dtype=np.float64)

    if on.any():
        p = phase[on]
        force = BODY_WEIGHT_N * 1.4 * scale * _force_profile(p)
        weights = _sensor_weights(p, shift)
        jitter = 1 + 0.04 * (rng.array(p.size * 8).reshape(p.size, 8) - 0.5)
        sensors[on] = np.maximum(0, np.round(force[:, None] * weights * jitter, 1))

    off_count = int((~on).sum())
    if off_count:
        # 접촉하지 않은 구간의 바닥 잡음. 접촉 기준(25 N)보다 훨씬 작다.
        sensors[~on] = np.round(rng.array(off_count * 8).reshape(off_count, 8) * 15, 0) / 10

    return sensors, np.round(sensors.sum(axis=1), 1)


def _standing(time: np.ndarray, profile: Profile, rng: _Rng) -> tuple[np.ndarray, np.ndarray]:
    """정적 측정 구간의 (n, 8) 센서값. 양발이 계속 닿아 있고 몸이 조금씩 흔들린다."""
    mask = time < profile.static_sec
    count = int(mask.sum())
    left = np.zeros((time.size, 8), dtype=np.float64)
    right = np.zeros((time.size, 8), dtype=np.float64)
    if count == 0:
        return left, right
    t = time[mask]
    sway = 1 + 0.03 * np.sin(2 * np.pi * 0.35 * t)
    # 선 자세는 뒤꿈치~중족부에 힘이 더 실린다.
    weights = _sensor_weights(np.full(count, 0.38), 0.0)
    for out, share, sign in ((left, profile.static_share_l, 1), (right, 1 - profile.static_share_l, -1)):
        force = BODY_WEIGHT_N * share * (1 + (sway - 1) * sign)
        jitter = 1 + 0.03 * (rng.array(count * 8).reshape(count, 8) - 0.5)
        out[mask] = np.maximum(0, np.round(force[:, None] * weights * jitter, 1))
    return left, right


def generate(seed: int, profile: Profile, duration: float = DURATION_SEC, sample_rate: int = SAMPLE_RATE) -> pd.DataFrame:
    rng = _Rng(seed)
    n = round(duration * sample_rate)
    time = np.arange(n, dtype=np.float64) / sample_rate
    strides = _build_strides(profile, rng, duration)

    left, _ = _one_foot(time, strides, 0.0, profile.stance_l, profile.scale_l, profile.front_shift_l, rng)
    right, _ = _one_foot(time, strides, profile.step_offset, profile.stance_r, profile.scale_r, profile.front_shift_r, rng)

    if profile.static_sec > 0:
        stand_l, stand_r = _standing(time, profile, rng)
        standing = time < profile.static_sec
        left[standing] = stand_l[standing]
        right[standing] = stand_r[standing]
    left_sum = np.round(left.sum(axis=1), 1)
    right_sum = np.round(right.sum(axis=1), 1)

    data = {"time": np.round(time, 3)}
    for i in range(8):
        data[f"l{i + 1}"] = left[:, i].astype(np.float32)
    for i in range(8):
        data[f"r{i + 1}"] = right[:, i].astype(np.float32)
    data["lsum"] = left_sum.astype(np.float32)
    data["rsum"] = right_sum.astype(np.float32)
    return pd.DataFrame(data)
