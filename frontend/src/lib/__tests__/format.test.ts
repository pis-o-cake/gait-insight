import { describe, expect, it } from "vitest";
import { formatMeasuredAt, formatNumber, formatTime } from "../format";

describe("formatTime", () => {
  it("분:초로 적고 초는 두 자리를 채운다", () => {
    expect(formatTime(0)).toBe("0:00");
    expect(formatTime(65)).toBe("1:05");
    expect(formatTime(600)).toBe("10:00");
  });

  it("소수 첫째 자리까지 보여줄 수 있다", () => {
    expect(formatTime(3.4, true)).toBe("0:03.4");
  });
});

describe("formatNumber", () => {
  it("천 단위를 구분한다", () => {
    expect(formatNumber(190684.7)).toBe("190,685");
  });
});

describe("formatMeasuredAt", () => {
  it("값이 없으면 빈 문자열", () => {
    expect(formatMeasuredAt(null)).toBe("");
  });

  it("요일과 오전·오후를 붙인다", () => {
    const text = formatMeasuredAt("2026-09-21T08:40:00+09:00");
    expect(text).toMatch(/9월 21일 \([일월화수목금토]\) (오전|오후) \d{1,2}:\d{2}/);
  });
});
