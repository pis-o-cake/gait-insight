/** 발 마스크와 센서 보간. 목업 §7 의 이식이며 좌표계·상수를 그대로 쓴다. */
export const FOOT_PATH =
  "M0,-940 C200,-940 260,-700 250,-450 C240,-250 200,-100 190,100 C180,350 230,600 200,800 " +
  "C170,930 -170,930 -200,800 C-230,600 -180,350 -190,100 C-200,-100 -240,-250 -250,-450 " +
  "C-260,-700 -200,-940 0,-940 Z";
export const FOOT_BOX = { x: -330, y: -1000, w: 660, h: 2000 };

const GRID_W = 88;
const GRID_H = 240;
const IDW_POWER = 2;
const IDW_EPS = 0.02;

export interface FootGrid {
  width: number;
  height: number;
  inside: Uint8Array;
  weights: Float32Array;
  /** 격자 좌표로 옮긴 센서 위치 (0~1) */
  sensorUv: { x: number; y: number }[];
}

/**
 * 한쪽 발의 보간 격자를 만든다. 발 안쪽 픽셀마다 센서 8개의 가중치를 미리 계산한다.
 * 센서 좌표는 발 중심(x≈±500)을 0 으로 옮겨 쓰고, Y 는 화면 위가 발 앞쪽이 되도록 뒤집는다.
 */
export function makeFootGrid(side: "left" | "right", sensors: { x: number; y: number }[]): FootGrid {
  const canvas = document.createElement("canvas");
  canvas.width = GRID_W;
  canvas.height = GRID_H;
  const ctx = canvas.getContext("2d", { willReadFrequently: true })!;
  ctx.save();
  ctx.scale(GRID_W / FOOT_BOX.w, GRID_H / FOOT_BOX.h);
  ctx.translate(-FOOT_BOX.x, -FOOT_BOX.y);
  if (side === "left") ctx.scale(-1, 1);
  ctx.fillStyle = "#000";
  ctx.fill(new Path2D(FOOT_PATH));
  ctx.restore();

  const mask = ctx.getImageData(0, 0, GRID_W, GRID_H).data;
  const inside = new Uint8Array(GRID_W * GRID_H);
  for (let i = 0; i < inside.length; i++) inside[i] = mask[i * 4 + 3] > 0 ? 1 : 0;

  const offset = side === "left" ? 500 : -500;
  const sx = sensors.map((s) => s.x + offset);
  const sy = sensors.map((s) => -s.y);

  const weights = new Float32Array(GRID_W * GRID_H * 8);
  const scale = 1 / 1000;
  for (let y = 0; y < GRID_H; y++) {
    for (let x = 0; x < GRID_W; x++) {
      const idx = y * GRID_W + x;
      if (!inside[idx]) continue;
      const dx0 = FOOT_BOX.x + ((x + 0.5) / GRID_W) * FOOT_BOX.w;
      const dy0 = FOOT_BOX.y + ((y + 0.5) / GRID_H) * FOOT_BOX.h;
      let sum = 0;
      const raw = new Float64Array(8);
      for (let k = 0; k < 8; k++) {
        const d2 = ((dx0 - sx[k]) * scale) ** 2 + ((dy0 - sy[k]) * scale) ** 2;
        const w = 1 / (Math.pow(d2, IDW_POWER / 2) + IDW_EPS);
        raw[k] = w;
        sum += w;
      }
      for (let k = 0; k < 8; k++) weights[idx * 8 + k] = raw[k] / sum;
    }
  }

  const sensorUv = sensors.map((_, k) => ({
    x: (sx[k] - FOOT_BOX.x) / FOOT_BOX.w,
    y: (sy[k] - FOOT_BOX.y) / FOOT_BOX.h,
  }));

  return { width: GRID_W, height: GRID_H, inside, weights, sensorUv };
}

export { GRID_W, GRID_H };
