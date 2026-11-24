import { t } from "../../lib/i18n";
import type { Analysis, Metric } from "../../types";

// 전문가 자료의 측정 항목 묶음. 보행검사 묶음은 인솔로 잴 수 없어 별도 측정값을 쓴다.
const GROUPS: { key: string; ids: string[] }[] = [
  { key: "load", ids: ["M01", "M02"] },
  { key: "time", ids: ["M03", "M04", "M05"] },
  { key: "rhythm", ids: ["M06", "M07", "M08"] },
  { key: "walk", ids: ["M09", "M10"] },
];
const SHARE = new Set(["M01", "M02"]);
const SINGLE = new Set(["M06", "M10"]);
const MARKER: Record<string, number> = { M01: 50, M02: 50, M08: 50 };
const FULL_SCALE: Record<string, number> = { M01: 100, M02: 100, M08: 100 };

export function MetricGrid({ analysis }: { analysis: Analysis }) {
  const status = new Map(analysis.observations.map((o) => [o.metric, o]));
  let index = 0;
  return (
    <div className="metric-groups">
      {GROUPS.map((group) => (
        <section key={group.key} className="metric-group">
          <header>
            <h3>{t(`m.group.${group.key}`)}</h3>
            <small>{t(`m.group.${group.key}.sub`)}</small>
          </header>
          <div className="metrics">
            {group.ids.map((id) => (
              <MetricTile key={id} id={id} metric={analysis.metrics[id]} observation={status.get(id)} index={index++} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

interface TileProps {
  id: string;
  metric: Metric | undefined;
  observation: { hit: boolean; status: string } | undefined;
  index: number;
}

function MetricTile({ id, metric, observation, index }: TileProps) {
  if (!metric || !metric.ok) {
    return (
      <div className="metric metric--na" style={{ "--i": index } as React.CSSProperties}>
        <div className="m-top"><span className="m-name">{t(`m.${id}.name`)}</span></div>
        <div className="m-na">{t("an.na")}</div>
        {metric?.reason && <div className="m-sub">{t(`reason.${metric.reason}`)}</div>}
      </div>
    );
  }

  const unit = t(`unit.${metric.unit}`);
  return (
    <div className="metric" data-hit={observation?.hit ? 1 : 0} style={{ "--i": index } as React.CSSProperties}>
      <div className="m-top">
        <span className="m-name">{t(`m.${id}.name`)}</span>
        {observation && (
          <span className={`ui-tag m-status ${observation.hit ? "ui-tag--hit" : "ui-tag--ok"}`}>
            {observation.status}
          </span>
        )}
      </div>
      {SINGLE.has(id) ? <SingleValue metric={metric} unit={unit} /> : <PairedValues id={id} metric={metric} unit={unit} />}
      <div className="m-sub">{t(`m.${id}.hint`)}</div>
    </div>
  );
}

function SingleValue({ metric, unit }: { metric: Metric; unit: string }) {
  return (
    <div className="m-nums m-nums--single">
      <div className="num">
        <b>{metric.value ?? "-"}<small>{unit}</small></b>
      </div>
    </div>
  );
}

function PairedValues({ id, metric, unit }: { id: string; metric: Metric; unit: string }) {
  const left = metric.left ?? 0;
  const right = metric.right ?? 0;
  const scale = FULL_SCALE[id] ?? (Math.max(left, right) || 1);
  const marker = MARKER[id] ?? null;
  const diff = metric.diffPct === null ? null : t(SHARE.has(id) ? "m.diffPp" : "m.diffPct", { v: metric.diffPct });
  return (
    <>
      <div className="m-nums">
        <Num cls="l" label={t("an.left")} value={String(metric.left ?? "-")} unit={unit} />
        <Num cls="r" label={t("an.right")} value={String(metric.right ?? "-")} unit={unit} />
      </div>
      <div className="m-bars">
        <Bar cls="l" value={left} scale={scale} marker={marker} />
        <Bar cls="r" value={right} scale={scale} marker={marker} />
      </div>
      {diff && <div className="m-diff">{diff}</div>}
    </>
  );
}

function Num({ cls, label, value, unit }: { cls: string; label: string; value: string; unit: string }) {
  return (
    <div className={`num ${cls}`}>
      <b className={value.length > 5 ? "long" : ""}>{value}<small>{unit}</small></b>
      <span>{label}</span>
    </div>
  );
}

function Bar({ cls, value, scale, marker }: { cls: string; value: number; scale: number; marker: number | null }) {
  const width = Math.max(2, Math.min(100, (value / scale) * 100));
  return (
    <div className={`bar ${cls}`}>
      <span className="track">
        <i style={{ width: `${width.toFixed(1)}%` }} />
        {marker !== null && <em style={{ left: `${((marker / scale) * 100).toFixed(1)}%` }} />}
      </span>
    </div>
  );
}
