import { useEffect, useState } from "react";
import { api } from "../data/client";
import { t } from "../lib/i18n";
import { ApiError, type DemoAccount, type User } from "../types";

export function LoginPage({ onDone }: { onDone: (user: User) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [shake, setShake] = useState(0);
  const [demo, setDemo] = useState<DemoAccount | null>(null);

  useEffect(() => { api.demoAccount().then(setDemo).catch(() => undefined); }, []);

  const isRegister = mode === "register";

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const user = isRegister
        ? await api.register(loginId.trim(), password, displayName.trim())
        : await api.login(loginId.trim(), password);
      onDone(user);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : t("err.network"));
      setShake((n) => n + 1);
      setPassword("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login" style={{ "--i": 0 } as React.CSSProperties}>
      <div className="login-card">
        <div className="mark" aria-hidden="true"><i /></div>
        <div>
          <h2>{t(isRegister ? "login.registerTitle" : "login.title")}</h2>
          <p className="ui-lede">{t(isRegister ? "login.registerDesc" : "login.desc")}</p>
        </div>
        <form className={`form${shake ? " is-error" : ""}`} key={shake} onSubmit={submit} noValidate>
          <div className="field">
            <label htmlFor="loginId">{t("login.id")}</label>
            <input className="input" id="loginId" value={loginId} autoComplete="username"
              autoCapitalize="off" spellCheck={false} onChange={(e) => setLoginId(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="loginPw">{t("login.pw")}</label>
            <input className="input" id="loginPw" type="password" value={password}
              autoComplete={isRegister ? "new-password" : "current-password"}
              onChange={(e) => setPassword(e.target.value)} />
          </div>
          {isRegister && (
            <div className="field">
              <label htmlFor="displayName">{t("login.name")}</label>
              <input className="input" id="displayName" value={displayName}
                onChange={(e) => setDisplayName(e.target.value)} />
            </div>
          )}
          <div className="form-error" role="alert" aria-live="polite">{error}</div>
          <button type="submit" className="ui-btn ui-btn--accent ui-btn--block" disabled={busy}>
            {t(isRegister ? "login.registerSubmit" : "login.submit")}
          </button>
        </form>
        <button type="button" className="ui-linkbtn"
          onClick={() => { setMode(isRegister ? "login" : "register"); setError(""); }}>
          {t(isRegister ? "login.toLogin" : "login.toRegister")}
        </button>
        {!isRegister && demo && (
          <div className="login-hint">
            <b>{t("login.demo.title")}</b>
            <dl>
              <dt>{t("login.id")}</dt><dd><code>{demo.loginId}</code></dd>
              <dt>{t("login.pw")}</dt><dd><code>{demo.password}</code></dd>
            </dl>
            <button type="button" className="ui-btn ui-btn--ghost ui-btn--small"
              onClick={() => { setLoginId(demo.loginId); setPassword(demo.password); setError(""); }}>
              {t("login.demo.fill")}
            </button>
            <span>{t("login.demo.note")}</span>
          </div>
        )}
      </div>
    </div>
  );
}
