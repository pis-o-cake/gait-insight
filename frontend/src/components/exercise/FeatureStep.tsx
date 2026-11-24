import { useState } from "react";
import { useReveal } from "../../hooks/useReveal";
import { t } from "../../lib/i18n";
import type { Exercise, Link } from "../../types";

export function FeatureStep({ link, index, exercises }: { link: Link; index: number; exercises: Exercise[] }) {
  const flowRef = useReveal<HTMLOListElement>();
  return (
    <section className="ex-match" style={{ "--i": index + 1 } as React.CSSProperties}>
      <header className="ex-match-head">
        <span className="ui-tag ui-tag--hit">{t(`type.${link.target}.tag`)}</span>
        <h3>{link.head}</h3>
      </header>
      <ol className="flow" ref={flowRef}>
        <Step n={1} step={0} label={t("ex.step1")}>
          <div className="card body card--obs">
            <p><b>{link.observation}</b></p>
            <ul className="ex-evidence">{link.evidence.map((e, i) => <li key={i}>{e}</li>)}</ul>
          </div>
        </Step>
        <Step n={2} step={1} label={t("ex.step2")}>
          <div className="card body card--why"><p>{link.reason}</p></div>
        </Step>
        <Step n={3} step={2} label={t("ex.step3", { n: link.exerciseIds.length })}>
          <div className="card ex-list">
            {link.exerciseIds.map((id) => {
              const exercise = exercises.find((e) => e.id === id);
              return exercise ? <ExerciseCard key={id} exercise={exercise} /> : null;
            })}
          </div>
        </Step>
        <Step n={4} step={3} label={t("ex.step4")}>
          <div className="card body card--why">
            <ul className="ex-recheck">{link.recheck.map((r, i) => <li key={i}>{r}</li>)}</ul>
            <p className="ref">{t("ex.recheckNote")}</p>
          </div>
        </Step>
      </ol>
    </section>
  );
}

function Step({ n, step, label, children }: { n: number; step: number; label: string; children: React.ReactNode }) {
  return (
    <li className="step" style={{ "--s": step } as React.CSSProperties}>
      <div className="node"><i>{n}</i></div>
      <div>
        <div className="lab">{label}</div>
        {children}
      </div>
    </li>
  );
}

export function ExerciseCard({ exercise }: { exercise: Exercise }) {
  const [open, setOpen] = useState(false);
  return (
    <article className="ex-card card--ex">
      <h4>{exercise.name}</h4>
      <p className="ex-purpose">{exercise.purpose}</p>
      {exercise.dosage && <p className="ex-dosage"><b>{t("ex.dosage")}</b> {exercise.dosage}</p>}
      <button type="button" className="ui-btn ui-btn--ghost ui-btn--small" aria-expanded={open}
        onClick={() => setOpen((v) => !v)}>
        {t(open ? "ex.close" : "ex.detail")}
      </button>
      <div className="ex-detail" data-open={open ? 1 : 0}>
        <div>
          <h5>{t("ex.steps")}</h5>
          <ol>{exercise.steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
          {exercise.caution.length > 0 && (
            <>
              <h5>{t("ex.caution")}</h5>
              <ul>{exercise.caution.map((c, i) => <li key={i}>{c}</li>)}</ul>
            </>
          )}
          <p className="ex-src">{t("ex.source")}: {exercise.source}</p>
          <p className="ex-review">{t(`ex.review.${exercise.reviewStatus}`)}</p>
        </div>
      </div>
    </article>
  );
}
