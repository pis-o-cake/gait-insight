/** 히트맵 팔레트와 색 보간. 목업 §2·§7 의 이식이다. */
export const PALETTES: Record<string, string[]> = {
  moss: ["#dfe6df", "#b9ccc2", "#6fa89a", "#2f8375", "#0f6e63", "#0a3d38"],
  sunset: ["#dfe6df", "#ffd9c2", "#ff9e7a", "#ff6b3d", "#c23f2a", "#6b1f18"],
  mono: ["#dfe6df", "#c2cac4", "#94a099", "#5f6d66", "#33403a", "#12201c"],
};

export const DEFAULT_PALETTE = "moss";

function hexToRgb(hex: string): [number, number, number] {
  const v = parseInt(hex.slice(1), 16);
  return [(v >> 16) & 255, (v >> 8) & 255, v & 255];
}

/** 팔레트를 256단계 LUT 로 펼친다. 캔버스가 픽셀마다 이 표를 읽는다. */
export function buildLut(name: string): Uint8ClampedArray {
  const stops = (PALETTES[name] ?? PALETTES[DEFAULT_PALETTE]).map(hexToRgb);
  const lut = new Uint8ClampedArray(256 * 3);
  const span = stops.length - 1;
  for (let i = 0; i < 256; i++) {
    const p = (i / 255) * span;
    const lo = Math.min(Math.floor(p), span - 1);
    const f = p - lo;
    for (let c = 0; c < 3; c++) {
      lut[i * 3 + c] = stops[lo][c] + (stops[lo + 1][c] - stops[lo][c]) * f;
    }
  }
  return lut;
}

export function lutGradientCss(name: string): string {
  const stops = PALETTES[name] ?? PALETTES[DEFAULT_PALETTE];
  return `linear-gradient(90deg, ${stops.join(", ")})`;
}

/** CSS 변수에서 캔버스 오버레이 색을 읽는다. 스킨만 바꿔도 JS 수정이 필요 없다. */
export function vizInk(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return value || fallback;
}
