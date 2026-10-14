const rawBaseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const env = {
  apiBaseUrl: `${rawBaseUrl.replace(/\/$/, "")}/api/v1`,
};
