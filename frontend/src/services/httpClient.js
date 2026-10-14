import { env } from "@/config/env";
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}
export function buildUrl(path, params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "")
      search.set(key, String(value));
  });
  const query = search.toString();
  return `${env.apiBaseUrl}${path}${query ? `?${query}` : ""}`;
}
/** Turns FastAPI error bodies (string or validation list) into one readable sentence. */
export function extractErrorMessage(body, status) {
  if (status === 429)
    return "Too many requests. Please wait a minute and try again.";
  const detail = body?.detail;
  if (typeof detail === "string")
    return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => (d.msg ?? "Invalid value").replace(/^Value error, /, "")).join("; ");
  }
  return `Request failed (${status})`;
}
export async function getJson(path, params, signal) {
  const response = await fetch(buildUrl(path, params), { signal });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(extractErrorMessage(body, response.status), response.status);
  }
  return response.json();
}
