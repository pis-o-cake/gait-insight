import { describe, expect, it } from "vitest";
import { buildLut, DEFAULT_PALETTE, PALETTES } from "../palette";

describe("buildLut", () => {
  it("256단계 RGB 표를 만든다", () => {
    const lut = buildLut(DEFAULT_PALETTE);
    expect(lut.length).toBe(256 * 3);
  });

  it("양 끝이 팔레트의 첫 색과 끝 색이다", () => {
    const stops = PALETTES[DEFAULT_PALETTE];
    const lut = buildLut(DEFAULT_PALETTE);
    const first = parseInt(stops[0].slice(1), 16);
    const last = parseInt(stops[stops.length - 1].slice(1), 16);
    expect([lut[0], lut[1], lut[2]]).toEqual([(first >> 16) & 255, (first >> 8) & 255, first & 255]);
    expect([lut[255 * 3], lut[255 * 3 + 1], lut[255 * 3 + 2]]).toEqual([(last >> 16) & 255, (last >> 8) & 255, last & 255]);
  });

  it("모르는 이름이면 기본 팔레트로 되돌린다", () => {
    expect(buildLut("nope")).toEqual(buildLut(DEFAULT_PALETTE));
  });
});
