import { useMemo } from "react";
import { formatTime } from "../../lib/format";
import { t } from "../../lib/i18n";
import type { RecordData } from "../../types";

const OVERVIEW_H = 110;
const DETAIL_H = 230;
const ML = 44, MR = 12, MT = 12, MB = 28;
const WIDTH = 900;
const DETAIL_WINDOW = 10;

interface Props { data: RecordData; t: number; duration: number }

/** 전체 개요 + 현재 시점 ±5초 확대. 구간 최대값으로 다운샘플한다. */
export function LoadChart({ data, t: cursor, duration }: Props) {
  const overview = useMemo(() => downsample(data, 420), [data]);
  const detail = useMemo(() => slice(data, cursor, DETAIL_WINDOW), [data, cursor]);

  return (
    <div className="ui-card" style={{ "--i": 3, marginTop: 10 } as React.CSSProperties}>
      <div className="title">
        <h3>{t2("an.chart.title")}</h3>
        <small>{t2("an.chart.sub")}</small>
      </div>

      <p className="chart-label">{t2("an.chart.overview", { min: Math.round(duration / 60) })}</p>
      <Plot
        height={OVERVIEW_H}
        maxY={overview.maxY}
        left={overview.left}
        right={overview.right}
        xTicks={tickLabels(duration, 10, (v) => String(Math.round(v / 60)))}
        cursorRatio={cursor / duration}
        windowRatio={[Math.max(0, (cursor - DETAIL_WINDOW / 2) / duration), Math.min(1, (cursor + DETAIL_WINDOW / 2) / duration)]}
      />

      <p className="chart-label">{t2("an.chart.detail")}</p>
      <Plot
        height={DETAIL_H}
        maxY={detail.maxY}
        left={detail.left}
        right={detail.right}
        xTicks={detail.ticks}
        cursorRatio={detail.cursorRatio}
        dashedCursor
      />

      <div className="chart-legend">
        <span className="l">{t2("an.left")}</span>
        <span className="r">{t2("an.right")}</span>
      </div>
    </div>
  );
}

function t2(key: string, params?: Record<string, string | number>) { return t(key, params); }

interface PlotProps {
  height: number; maxY: number; left: number[]; right: number[];
  xTicks: { at: number; label: string }[];
  cursorRatio: number; windowRatio?: [number, number]; dashedCursor?: boolean;
}

function Plot({ height, maxY, left, right, xTicks, cursorRatio, windowRatio, dashedCursor }: PlotProps) {
  const innerW = WIDTH - ML - MR;
  const innerH = height - MT - MB;
  const toPath = (values: number[]) =>
    values
      .map((v, i) => `${i ? "L" : "M"}${(ML + (i / (values.length - 1)) * innerW).toFixed(1)},${(MT + innerH - (v / maxY) * innerH).toFixed(1)}`)
      .join("");
  const yTicks = [0, maxY / 2, maxY].map((v) => ({ v, y: MT + innerH - (v / maxY) * innerH }));

  return (
    <div className="chart">
      <svg viewBox={`0 0 ${WIDTH} ${height}`} preserveAspectRatio="none" role="img">
        {yTicks.map((tick) => (
          <g key={tick.v}>
            <line x1={ML} x2={WIDTH - MR} y1={tick.y} y2={tick.y} className="grid" />
            <text x={ML - 8} y={tick.y + 4} className="axis" textAnchor="end">{Math.round(tick.v)}</text>
          </g>
        ))}
        {windowRatio && (
          <rect x={ML + windowRatio[0] * innerW} y={MT}
            width={Math.max(2, (windowRatio[1] - windowRatio[0]) * innerW)} height={innerH}
            className="chart-window" />
        )}
        <path d={toPath(left)} className="line-l" fill="none" vectorEffect="non-scaling-stroke" />
        <path d={toPath(right)} className="line-r" fill="none" vectorEffect="non-scaling-stroke" />
        <line x1={ML + cursorRatio * innerW} x2={ML + cursorRatio * innerW} y1={MT} y2={MT + innerH}
          className={dashedCursor ? "cursor dashed" : "cursor"} />
        {xTicks.map((tick) => (
          <text key={tick.label + tick.at} x={ML + tick.at * innerW} y={height - 8}
            className="axis" textAnchor="middle">{tick.label}</text>
        ))}
      </svg>
    </div>
  );
}

function downsample(data: RecordData, points: number) {
  const n = data.leftSum.length;
  const bucket = Math.max(1, Math.floor(n / points));
  const left: number[] = [], right: number[] = [];
  let maxY = 1;
  for (let i = 0; i < n; i += bucket) {
    let l = 0, r = 0;
    for (let j = i; j < Math.min(i + bucket, n); j++) {
      if (data.leftSum[j] > l) l = data.leftSum[j];
      if (data.rightSum[j] > r) r = data.rightSum[j];
    }
    left.push(l); right.push(r);
    if (l > maxY) maxY = l;
    if (r > maxY) maxY = r;
  }
  return { left, right, maxY };
}

function slice(data: RecordData, centre: number, windowSec: number) {
  const dt = data.time.length > 1 ? data.time[1] - data.time[0] : 0.01;
  const total = data.time.at(-1) ?? windowSec;
  // 창 폭을 항상 windowSec 으로 유지한다. 양 끝에서는 안쪽으로 밀어 눈금 간격이 흔들리지 않게 한다.
  let start = centre - windowSec / 2;
  if (start < 0) start = 0;
  if (start + windowSec > total) start = Math.max(0, total - windowSec);
  const from = Math.round(start / dt);
  const to = Math.min(data.time.length, from + Math.round(windowSec / dt));
  const left = data.leftSum.slice(from, to);
  const right = data.rightSum.slice(from, to);
  const maxY = Math.max(1, ...left, ...right);
  const startSec = data.time[from] ?? 0;
  const endSec = data.time[to - 1] ?? startSec + windowSec;
  const span = Math.max(0.001, endSec - startSec);
  const ticks = tickLabels(span, 5, (v) => formatTime(Math.round(startSec + v)));
  return { left, right, maxY, ticks, cursorRatio: Math.max(0, Math.min(1, (centre - startSec) / span)) };
}

function tickLabels(span: number, count: number, label: (v: number) => string) {
  return Array.from({ length: count + 1 }, (_, i) => ({
    at: i / count,
    label: label((span * i) / count),
  }));
}
