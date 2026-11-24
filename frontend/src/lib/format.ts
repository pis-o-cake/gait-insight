export function formatTime(sec: number, tenth = false): string {
  const m = Math.floor(sec / 60);
  const rest = sec - m * 60;
  const ss = tenth ? rest.toFixed(1) : String(Math.floor(rest));
  return `${m}:${parseFloat(ss) < 10 ? "0" : ""}${ss}`;
}

export function formatNumber(value: number): string {
  return Math.round(value).toLocaleString("ko-KR");
}

const WEEKDAY = ["일", "월", "화", "수", "목", "금", "토"];

export function formatMeasuredAt(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const hour = d.getHours();
  const ampm = hour < 12 ? "오전" : "오후";
  const h12 = hour % 12 === 0 ? 12 : hour % 12;
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `${d.getMonth() + 1}월 ${d.getDate()}일 (${WEEKDAY[d.getDay()]}) ${ampm} ${h12}:${mm}`;
}
