import type { ReactNode } from "react";
import { t } from "../../lib/i18n";

export function Steps({ current }: { current: "list" | "analysis" | "exercise" }) {
  const order = ["list", "analysis", "exercise"] as const;
  const index = order.indexOf(current);
  return (
    <div className="ui-steps" aria-label="진행 단계">
      <i className="ind" style={{ transform: `translateX(${index * 100}%)` }} />
      {order.map((s, i) => (
        <span key={s} data-on={i === index ? 1 : 0}>{t(`step.${s}`)}</span>
      ))}
    </div>
  );
}

export function Banner() {
  return <p className="ui-banner">{t("app.banner")}</p>;
}

export function ErrorCard({ message, onRetry, onBack }: { message: string; onRetry?: () => void; onBack?: () => void }) {
  return (
    <div className="ui-card" style={{ marginTop: 24 }}>
      <p>{message}</p>
      <div className="ui-actions">
        {onRetry && <button type="button" className="ui-btn ui-btn--accent" onClick={onRetry}>{t("err.retry")}</button>}
        {onBack && <button type="button" className="ui-btn ui-btn--ghost" onClick={onBack}>{t("err.toList")}</button>}
      </div>
    </div>
  );
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="field">
      <label>{label}</label>
      {children}
    </div>
  );
}
