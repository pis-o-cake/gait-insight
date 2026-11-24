import { useEffect, useState } from "react";
import { api } from "./data/client";
import { navigate, useRoute } from "./hooks/useRoute";
import { t } from "./lib/i18n";
import { Banner, Steps } from "./components/ui";
import { LoginPage } from "./pages/LoginPage";
import { ListPage } from "./pages/ListPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import { ExercisePage } from "./pages/ExercisePage";
import type { User } from "./types";

export function App() {
  const route = useRoute();
  const [user, setUser] = useState<User | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    api.me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecked(true));
  }, []);

  useEffect(() => {
    if (!checked) return;
    if (!user && route.screen !== "login") navigate("login");
    if (user && route.screen === "login") navigate("list");
  }, [checked, user, route.screen]);

  async function logout() {
    await api.logout().catch(() => undefined);
    setUser(null);
    navigate("login");
  }

  if (!checked) return <div className="ui-loading" />;

  const showChrome = Boolean(user) && route.screen !== "login";

  return (
    <>
      <nav className="ui-nav">
        <div className="in">
          <div className="brand"><h1>{t("app.name")}</h1></div>
          <div className="right">
            {showChrome && (
              <>
                <button type="button" className="ui-btn ui-btn--ghost ui-btn--small" onClick={logout}>
                  {t("nav.logout")}
                </button>
                <Steps current={route.screen} />
              </>
            )}
          </div>
        </div>
      </nav>

      <div className="ui-app">
        <Banner />
        <main>
          {!user || route.screen === "login" ? (
            <LoginPage onDone={(u) => { setUser(u); navigate("list"); }} />
          ) : route.screen === "analysis" ? (
            <AnalysisPage key={route.id} recordId={route.id} />
          ) : route.screen === "exercise" ? (
            <ExercisePage key={route.id} recordId={route.id} />
          ) : (
            <ListPage user={user} />
          )}
        </main>
      </div>
    </>
  );
}
