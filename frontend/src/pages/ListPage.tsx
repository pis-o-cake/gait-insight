import { useEffect, useState } from "react";
import { api } from "../data/client";
import { formatMeasuredAt } from "../lib/format";
import { t } from "../lib/i18n";
import { navigate } from "../hooks/useRoute";
import { ErrorCard } from "../components/ui";
import { Sparkline } from "../components/chart/Sparkline";
import type { RecordSummary, User } from "../types";

export function ListPage({ user }: { user: User }) {
  const [records, setRecords] = useState<RecordSummary[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    api.listRecords()
      .then((rows) => alive && setRecords(rows))
      .catch(() => alive && setError(t("err.network")));
    return () => { alive = false; };
  }, []);

  if (error) return <ErrorCard message={error} onRetry={() => window.location.reload()} />;
  if (!records) return <div className="ui-loading" />;

  return (
    <>
      <header className="hello" style={{ "--i": 0 } as React.CSSProperties}>
        <div>
          <h2>{t("list.title", { name: user.displayName })}</h2>
          <p className="ui-lede">{t("list.desc", { n: records.length })}</p>
        </div>
      </header>

      <div className="demo-note" role="note" style={{ "--i": 1 } as React.CSSProperties}>
        <b>{t("list.noticeTitle")}</b>
        <span>{t("list.notice")}</span>
      </div>

      {records.length === 0 && <p className="ui-lede">{t("list.empty")}</p>}

      <div className="rec-list">
        {records.map((record, i) => (
          <button key={record.id} type="button" className="rec-row"
            style={{ "--i": i + 2 } as React.CSSProperties}
            onClick={() => navigate("analysis", record.id)}>
            <span className="rec-main">
              <span className="rec-name">{record.name}</span>
              <span className="rec-when">{formatMeasuredAt(record.measuredAt)}</span>
              <span className="rec-meta">
                {t("list.meta", {
                  min: Math.round(record.durationSec / 60),
                  condition: record.condition,
                  hz: record.sampleRate,
                })}
              </span>
            </span>
            {record.preview && <Sparkline left={record.preview.left} right={record.preview.right} />}
            <span className="rec-go">{t("list.go")}<Arrow /></span>
          </button>
        ))}
      </div>
    </>
  );
}

function Arrow() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true" className="ic-arrow">
      <path d="M3 8h9M8.5 4.5 12 8l-3.5 3.5" fill="none" stroke="currentColor"
        strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
