/** 백엔드 호출 창구. 인증은 httpOnly 쿠키라 credentials 만 켜면 된다. */
import { ApiError } from "../types";
import type { Analysis, DemoAccount, Exercise, RecordData, RecordSummary, User } from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.code ?? "unknown", body.message ?? "요청을 처리하지 못했습니다.");
  }
  return (await response.json()) as T;
}

export const api = {
  me: () => request<User>("/auth/me"),
  login: (loginId: string, password: string) =>
    request<User>("/auth/login", { method: "POST", body: JSON.stringify({ loginId, password }) }),
  register: (loginId: string, password: string, displayName: string) =>
    request<User>("/auth/register", { method: "POST", body: JSON.stringify({ loginId, password, displayName }) }),
  logout: () => request<{ ok: boolean }>("/auth/logout", { method: "POST" }),
  demoAccount: () => request<DemoAccount | null>("/auth/demo-account"),

  listRecords: () => request<RecordSummary[]>("/record"),
  getRecord: (id: string, step = 1) => request<RecordData>(`/record/${id}?step=${step}`),
  getAnalysis: (id: string) => request<Analysis>(`/analysis/${id}`),
  listExercises: () => request<Exercise[]>("/exercise"),
  getExercise: (id: string) => request<Exercise>(`/exercise/${id}`),
};
