import { useEffect, useState } from "react";

export type Route =
  | { screen: "login" }
  | { screen: "list" }
  | { screen: "analysis"; id: string }
  | { screen: "exercise"; id: string };

function parse(hash: string): Route {
  const parts = hash.replace(/^#\/?/, "").split("/");
  const [screen, id] = parts;
  if (screen === "analysis" && id) return { screen: "analysis", id };
  if (screen === "exercise" && id) return { screen: "exercise", id };
  if (screen === "login") return { screen: "login" };
  return { screen: "list" };
}

export function navigate(screen: string, id?: string): void {
  const next = `#/${screen}${id ? `/${id}` : ""}`;
  if (window.location.hash === next) window.dispatchEvent(new HashChangeEvent("hashchange"));
  else window.location.hash = next;
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parse(window.location.hash));
  useEffect(() => {
    const onChange = () => {
      setRoute(parse(window.location.hash));
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return route;
}
