/** 기록 목록의 6초 미리보기. 왼발·오른발 두 선만 그린다. */
export function Sparkline({ left, right }: { left: number[]; right: number[] }) {
  const width = 480;
  const height = 64;
  const max = Math.max(1, ...left, ...right);
  const path = (values: number[]) =>
    values
      .map((v, i) => `${i ? "L" : "M"}${((i / (values.length - 1)) * width).toFixed(1)},${(height - 4 - (v / max) * (height - 8)).toFixed(1)}`)
      .join("");
  return (
    <svg className="rec-spark" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" aria-hidden="true">
      <path className="l" d={path(left)} />
      <path className="r" d={path(right)} />
    </svg>
  );
}
