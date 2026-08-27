import { apiFetch } from "./api";

async function request(path, options = {}) {
  const response = await apiFetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "İşlem tamamlanamadı.");
  return data;
}

export function getDefinitions() { return request("/api/definitions"); }
export function createDefinition(type, payload) { return request(`/api/definitions/${type}`, { method: "POST", body: JSON.stringify(payload) }); }
export function updateDefinition(type, id, payload) { return request(`/api/definitions/${type}/${id}`, { method: "PUT", body: JSON.stringify(payload) }); }
export function deleteDefinition(type, id) { return request(`/api/definitions/${type}/${id}`, { method: "DELETE" }); }
