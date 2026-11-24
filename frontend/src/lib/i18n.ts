import messages from "../locales/ko.json";

type Params = Record<string, string | number>;

/** 문구를 가져온다. 사용자에게 보이는 문장은 모두 이 함수를 거친다. */
export function t(key: string, params?: Params): string {
  const template = (messages as Record<string, string>)[key] ?? key;
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (_, name: string) =>
    name in params ? String(params[name]) : `{${name}}`,
  );
}
