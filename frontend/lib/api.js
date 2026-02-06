const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      Authorization: "Bearer dev-admin-token",
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
