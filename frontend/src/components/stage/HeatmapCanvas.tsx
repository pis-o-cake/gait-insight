import { useEffect, useMemo, useRef } from "react";
import { FOOT_BOX, FOOT_PATH, GRID_H, GRID_W, makeFootGrid, type FootGrid } from "../../lib/idw";
import { buildLut, PALETTES, vizInk } from "../../lib/palette";
import type { RecordData } from "../../types";

export interface DisplayOptions {
  palette: string;
  cutoff: number;
  outline: boolean;
  sensors: boolean;
  cop: boolean;
}

interface Props {
  data: RecordData;
  index: number;
  options: DisplayOptions;
}

export function HeatmapCanvas({ data, index, options }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const grids = useMemo(
    () => ({ left: makeFootGrid("left", data.sensorLeft), right: makeFootGrid("right", data.sensorRight) }),
    [data.sensorLeft, data.sensorRight],
  );
  const lut = useMemo(() => buildLut(options.palette), [options.palette]);
  const baseColor = useMemo(() => {
    const stops = PALETTES[options.palette] ?? PALETTES.moss;
    const v = parseInt(stops[0].slice(1), 16);
    return [(v >> 16) & 255, (v >> 8) & 255, v & 255] as const;
  }, [options.palette]);

  // 발 하나에 실리는 최대 센서값. 색 범위를 기록 전체에 고정해 재생 중 색이 요동치지 않게 한다.
  const peak = useMemo(() => {
    let max = 1;
    for (const row of data.left) for (const v of row) if (v > max) max = v;
    for (const row of data.right) for (const v of row) if (v > max) max = v;
    return max;
  }, [data]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const stage = canvas?.parentElement;
    if (!canvas || !stage) return;

    const draw = () => {
      const rect = stage.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      canvas.width = Math.round(rect.width * dpr);
      canvas.height = Math.round(rect.height * dpr);
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      const ctx = canvas.getContext("2d")!;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, rect.width, rect.height);

      const footH = Math.min(rect.height * 0.94, rect.width * 0.7);
      const footW = (footH * FOOT_BOX.w) / FOOT_BOX.h;
      const gap = footW * 0.42;
      const top = (rect.height - footH) / 2;
      const leftX = rect.width / 2 - gap / 2 - footW;
      const rightX = rect.width / 2 + gap / 2;

      paint(ctx, "left", grids.left, data.left[index], leftX, top, footW, footH);
      paint(ctx, "right", grids.right, data.right[index], rightX, top, footW, footH);
    };

    const paint = (
      ctx: CanvasRenderingContext2D, side: "left" | "right", grid: FootGrid,
      values: number[] | undefined, x: number, y: number, w: number, h: number,
    ) => {
      if (!values) return;
      const image = ctx.createImageData(GRID_W, GRID_H);
      const px = image.data;
      for (let i = 0; i < GRID_W * GRID_H; i++) {
        const o = i * 4;
        if (!grid.inside[i]) { px[o + 3] = 0; continue; }
        let v = 0;
        for (let k = 0; k < 8; k++) v += grid.weights[i * 8 + k] * values[k];
        px[o + 3] = 255;
        if (v <= options.cutoff) {
          px[o] = baseColor[0]; px[o + 1] = baseColor[1]; px[o + 2] = baseColor[2];
          continue;
        }
        const level = Math.max(0, Math.min(255, Math.round((v / peak) * 255)));
        px[o] = lut[level * 3];
        px[o + 1] = lut[level * 3 + 1];
        px[o + 2] = lut[level * 3 + 2];
      }
      const off = document.createElement("canvas");
      off.width = GRID_W; off.height = GRID_H;
      off.getContext("2d")!.putImageData(image, 0, 0);

      ctx.save();
      ctx.translate(x, y);
      ctx.imageSmoothingEnabled = true;
      ctx.drawImage(off, 0, 0, w, h);

      const toCanvas = (uv: { x: number; y: number }) => ({ x: uv.x * w, y: uv.y * h });

      if (options.outline) {
        ctx.save();
        ctx.scale(w / FOOT_BOX.w, h / FOOT_BOX.h);
        ctx.translate(-FOOT_BOX.x, -FOOT_BOX.y);
        if (side === "left") ctx.scale(-1, 1);
        ctx.strokeStyle = vizInk("--viz-outline", "rgba(0,0,0,.16)");
        ctx.lineWidth = (2.2 * FOOT_BOX.w) / w;
        ctx.stroke(new Path2D(FOOT_PATH));
        ctx.restore();
      }

      if (options.sensors) {
        ctx.fillStyle = vizInk("--viz-sensor-fill", "#ffffff");
        ctx.strokeStyle = vizInk("--viz-sensor-line", "rgba(0,0,0,.4)");
        ctx.lineWidth = 1;
        for (const uv of grid.sensorUv) {
          const p = toCanvas(uv);
          ctx.beginPath();
          ctx.arc(p.x, p.y, Math.max(3, w * 0.035), 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
        }
      }

      if (options.cop) {
        const total = values.reduce((a, b) => a + b, 0);
        if (total > 30) {
          let cx = 0, cy = 0;
          grid.sensorUv.forEach((uv, k) => { cx += uv.x * values[k]; cy += uv.y * values[k]; });
          const p = toCanvas({ x: cx / total, y: cy / total });
          ctx.beginPath();
          ctx.arc(p.x, p.y, Math.max(5, w * 0.06), 0, Math.PI * 2);
          ctx.fillStyle = vizInk("--viz-cop-fill", "#ff6b3d");
          ctx.strokeStyle = vizInk("--viz-cop-line", "#ffffff");
          ctx.lineWidth = 2;
          ctx.fill();
          ctx.stroke();
        }
      }
      ctx.restore();
    };

    draw();
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [data, index, options, grids, lut, peak, baseColor]);

  return <canvas ref={canvasRef} aria-label="양발 하중 히트맵" />;
}
