const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";

export function getApiBaseUrl() { return apiBaseUrl; }

export async function api(path, options = {}) {
  const response = await apiFetch(`/api${path.startsWith('/') ? path : `/${path}`}`, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "İşlem tamamlanamadı.");
  return data;
}

export function apiFetch(path, options = {}) {
  const url = `${apiBaseUrl}${path}`;
  return fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
}
