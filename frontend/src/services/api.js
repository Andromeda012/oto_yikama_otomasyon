const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export function getApiBaseUrl() {
  return apiBaseUrl;
}

export function apiFetch(path, options = {}) {
  const url = `${apiBaseUrl}${path}`;
  return fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
}
