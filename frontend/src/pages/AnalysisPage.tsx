import { useEffect, useMemo, useState } from "react";
import { api } from "../data/client";
import { usePlayback } from "../hooks/usePlayback";
import { navigate } from "../hooks/useRoute";
import { formatMeasuredAt, formatTime } from "../lib/format";
import { t } from "../lib/i18n";
import { DEFAULT_PALETTE, lutGradientCss } from "../lib/palette";
import { ErrorCard } from "../components/ui";
import { HeatmapCanvas, type DisplayOptions } from "../components/stage/HeatmapCanvas";
import { SettingsPopover } from "../components/stage/SettingsPopover";
import { PlaybackDock } from "../components/dock/PlaybackDock";
import { LoadChart } from "../components/chart/LoadChart";
import { MetricGrid } from "../components/metric/MetricGrid";
import type { Analysis, RecordData, RecordSummary } from "../types";

const STORAGE_KEY = "gait-display";
// 표시용 해상도. 10분 × 100 Hz 원본을 그대로 내려받으면 휴대폰에서 느리다.
const DISPLAY_STEP = 5;

function loadOptions(): DisplayOptions {
  const fallback: DisplayOptions = { palette: DEFAULT_PALETTE, cutoff: 0, outline: true, sensors: true, cop: true };
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? { ...fallback, ...JSON.parse(raw) } : fallback;
  } catch {
    return fallback;
  }
}

export function AnalysisPage({ recordId }: { recordId: string }) {
  const [records, setRecords] = useState<RecordSummary[]>([]);
  const [data, setData] = useState<RecordData | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState("");
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [options, setOptions] = useState<DisplayOptions>(loadOptions);

  const record = records.find((r) => r.id === recordId);
  const duration = record?.durationSec ?? data?.time.at(-1) ?? 0;
  const playback = usePlayback(duration);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(options)); } catch { /* 저장 실패는 무시한다 */ }
  }, [options]);

  useEffect(() => { api.listRecords().then(setRecords).catch(() => undefined); }, []);

  useEffect(() => {
    let alive = true;
    setData(null);
    setAnalysis(null);
    setError("");
    playback.reset();
    Promise.all([api.getRecord(recordId, DISPLAY_STEP), api.getAnalysis(recordId)])
      .then(([body, result]) => {
        if (!alive) return;
        setData(body);
        setAnalysis(result);
      })
      .catch((e) => alive && setError(e?.message ?? t("err.network")));
    return () => { alive = false; };
    // playback 은 의도적으로 의존성에서 뺀다. 기록이 바뀔 때만 초기화한다.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recordId]);

  const index = useMemo(() => {
    if (!data) return 0;
    const dt = data.time.length > 1 ? data.time[1] - data.time[0] : 0.01;
    return Math.max(0, Math.min(data.time.length - 1, Math.round(playback.t / dt)));
  }, [data, playback.t]);

  if (error) return <ErrorCard message={error} onBack={() => navigate("list")} />;
  if (!data || !analysis || !record) return <div className="ui-loading" />;

  const nowLeft = data.leftSum[index] ?? 0;
  const nowRight = data.rightSum[index] ?? 0;

  return (
    <>
      <div className="an-top" style={{ "--i": 0 } as React.CSSProperties}>
        <div className="rec-tabs" role="tablist" aria-label="기록 전환">
          {records.map((r) => (
            <button key={r.id} type="button" role="tab" aria-selected={r.id === recordId}
              onClick={() => navigate("analysis", r.id)}>{r.name}</button>
          ))}
        </div>
        <button type="button" className="ui-linkbtn" onClick={() => navigate("list")}>{t("an.back")}</button>
      </div>

      <div className="an-head" style={{ "--i": 1 } as React.CSSProperties}>
        <h2>{record.name}</h2>
        <p className="an-meta">
          <b>{formatMeasuredAt(record.measuredAt)}</b>
          <span>{t("list.meta", { min: Math.round(record.durationSec / 60), condition: record.condition, hz: record.sampleRate })}</span>
          {record.isDemo && <span className="an-demo">{t("an.demoTag")}</span>}
        </p>
      </div>

      <section className="stage-card" style={{ "--i": 2 } as React.CSSProperties}>
        <div className="stage">
          <HeatmapCanvas data={data} index={index} options={options} />
          <div className="stage-time">
            <b>{formatTime(playback.t, true)}</b>
            <span>프레임 {index} / {data.time.length - 1}</span>
          </div>
          <div className="stage-tools">
            <button type="button" className="chip" aria-expanded={settingsOpen}
              onClick={() => setSettingsOpen((v) => !v)}>{t("an.settings")}</button>
          </div>
          <SettingsPopover open={settingsOpen} options={options}
            onChange={setOptions} onClose={() => setSettingsOpen(false)} />
          <div className="stage-foot">
            <span className="l"><b>{Math.round(nowLeft)}</b> {t("an.left")} N</span>
            <span className="r"><b>{Math.round(nowRight)}</b> {t("an.right")} N</span>
          </div>
        </div>
        <div className="stage-legend">
          <span>{t("an.heat.lo")}</span>
          <i style={{ background: lutGradientCss(options.palette) }} />
          <span>{t("an.heat.hi")}</span>
          <span className="legend-feet"><em className="l">{t("an.left")}</em><em className="r">{t("an.right")}</em></span>
        </div>
      </section>

      <MetricGrid analysis={analysis} />
      <LoadChart data={data} t={playback.t} duration={duration} />

      <div className="ui-card summary" style={{ "--i": 4 } as React.CSSProperties}>
        <div className="title">
          <h3>{t("an.summary.title")}</h3>
          <small>{t("an.summary.sub")}</small>
        </div>
        <p className="sum-lead">{analysis.summary}</p>
        <ul className="sum-list">
          {analysis.links.map((link) => (
            <li key={link.target}>
              <span className="ui-tag ui-tag--hit">{t(`type.${link.target}.tag`)}</span>
              <b>{link.head}</b>
            </li>
          ))}
          {analysis.watch.map((w) => (
            <li key={w.metric}>
              <span className="ui-tag ui-tag--note">{t("an.watchTag")}</span>
              <b>{w.head}</b>
            </li>
          ))}
        </ul>
        <p className="an-window">
          {analysis.staticWindow && t("an.staticWindow", { from: formatTime(analysis.staticWindow.from), to: formatTime(analysis.staticWindow.to) })}
          {t("an.window", { from: formatTime(analysis.window.from), to: formatTime(analysis.window.to) })}
        </p>
        <div className="ui-actions">
          <button type="button" className="ui-btn ui-btn--accent" onClick={() => navigate("exercise", recordId)}>
            {t("an.summary.go")}
          </button>
        </div>
      </div>

      <PlaybackDock playback={playback} duration={duration} />
    </>
  );
}
