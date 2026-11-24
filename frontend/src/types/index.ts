export interface RecordSummary {
  id: string;
  name: string;
  condition: string;
  measuredAt: string | null;
  durationSec: number;
  sampleRate: number;
  source: string;
  license: string;
  isDemo: boolean;
  preview: { left: number[]; right: number[] } | null;
}

export interface SensorPosition { x: number; y: number }

export interface RecordData {
  id: string;
  unit: string;
  sampleRate: number;
  step: number;
  time: number[];
  left: number[][];
  right: number[][];
  leftSum: number[];
  rightSum: number[];
  sensorLeft: SensorPosition[];
  sensorRight: SensorPosition[];
}

export interface Metric {
  left: number | null;
  right: number | null;
  unit: string;
  ok: boolean;
  /** 좌우 구분이 없는 지표(분당 걸음 수, 보행 속도)의 값. */
  value: number | null;
  diffPct: number | null;
  reason: string | null;
  extra: Record<string, unknown>;
}

export interface Observation {
  metric: string;
  hit: boolean;
  status: string;
  head: string;
  text: string;
}

/** 해당된 보행 유형(T1~T3) 하나와 그 운동 프로그램. */
export interface Link {
  target: string;
  head: string;
  observation: string;
  evidence: string[];
  reason: string;
  exerciseIds: string[];
  recheck: string[];
}

export interface Analysis {
  recordId: string;
  window: { from: number; to: number };
  staticWindow: { from: number; to: number } | null;
  metrics: Record<string, Metric>;
  observations: Observation[];
  links: Link[];
  watch: Observation[];
  summary: string;
  ruleSetVersion: string;
  ruleSetStatus: string;
  computedAt: string | null;
}

export interface Exercise {
  id: string;
  name: string;
  purpose: string;
  steps: string[];
  caution: string[];
  dosage: string;
  source: string;
  reviewStatus: string;
  isGeneral: boolean;
}

export interface DemoAccount {
  loginId: string;
  password: string;
}

export interface User {
  id: number;
  loginId: string;
  displayName: string;
}

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
  }
}
