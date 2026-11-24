import { useEffect, useState } from "react";
import { api } from "../data/client";
import { navigate } from "../hooks/useRoute";
import { formatMeasuredAt } from "../lib/format";
import { t } from "../lib/i18n";
import { ErrorCard } from "../components/ui";
import { ExerciseCard, FeatureStep } from "../components/exercise/FeatureStep";
import type { Analysis, Exercise, RecordSummary } from "../types";

export function ExercisePage({ recordId }: { recordId: string }) {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [record, setRecord] = useState<RecordSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    Promise.all([api.getAnalysis(recordId), api.listExercises(), api.listRecords()])
      .then(([result, list, records]) => {
        if (!alive) return;
        setAnalysis(result);
        setExercises(list);
        setRecord(records.find((r) => r.id === recordId) ?? null);
      })
      .catch((e) => alive && setError(e?.message ?? t("err.network")));
    return () => { alive = false; };
  }, [recordId]);

  if (error) return <ErrorCard message={error} onBack={() => navigate("list")} />;
  if (!analysis) return <div className="ui-loading" />;

  const general = exercises.filter((e) => e.isGeneral);

  return (
    <>
      <div className="ex-head" style={{ "--i": 0 } as React.CSSProperties}>
        <div>
          <h2>{t("ex.title")}</h2>
          {record && <small>{record.name} · {formatMeasuredAt(record.measuredAt)}</small>}
        </div>
        <button type="button" className="ui-linkbtn" onClick={() => navigate("analysis", recordId)}>
          {t("ex.back")}
        </button>
      </div>
      <p className="ui-lede" style={{ "--i": 1 } as React.CSSProperties}>{t("ex.lede")}</p>

      {analysis.links.map((link, i) => (
        <FeatureStep key={link.target} link={link} index={i} exercises={exercises} />
      ))}

      {analysis.watch.length > 0 && (
        <section className="ex-ok">
          <h4>{t("ex.watch.title")}</h4>
          <p>{t("ex.watch.desc")}</p>
          <ul>
            {analysis.watch.map((w) => (
              <li key={w.metric}><b>{w.head}</b><span>{w.text}</span></li>
            ))}
          </ul>
        </section>
      )}

      {general.length > 0 && (
        <section className="ex-group">
          <h3>{t("ex.general.title")}</h3>
          <p className="ui-lede">{t("ex.general.desc")}</p>
          <div className="ex-list">
            {general.map((exercise) => <ExerciseCard key={exercise.id} exercise={exercise} />)}
          </div>
        </section>
      )}

      <p className="ui-note">{t("ex.disclaimer")}</p>

      <div className="ui-actions">
        <button type="button" className="ui-btn ui-btn--block ui-btn--ghost"
          onClick={() => navigate("analysis", recordId)}>{t("ex.back")}</button>
      </div>
    </>
  );
}
