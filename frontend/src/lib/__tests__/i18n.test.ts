import { describe, expect, it } from "vitest";
import { t } from "../i18n";

describe("t", () => {
  it("문구를 찾아 준다", () => {
    expect(t("an.left")).toBe("왼발");
  });

  it("{param} 을 치환한다", () => {
    expect(t("list.title", { name: "이수민" })).toBe("안녕하세요, 이수민님");
  });

  it("없는 키는 키 그대로 돌려준다", () => {
    expect(t("no.such.key")).toBe("no.such.key");
  });
});
