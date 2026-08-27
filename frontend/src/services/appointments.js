import { apiFetch } from "./api";

export async function getAppointments(date) {
  const response = await apiFetch(`/api/appointments?date=${encodeURIComponent(date)}`);
  if (!response.ok) throw new Error("Randevular alınamadı.");
  return response.json();
}

export async function getAppointmentLookups() {
  const response = await apiFetch("/api/appointments/lookups");
  if (!response.ok) throw new Error("Tanımlar alınamadı.");
  return response.json();
}

export async function createAppointment(payload) {
  const response = await apiFetch("/api/appointments", { method: "POST", body: JSON.stringify(payload) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Randevu oluşturulamadı.");
  return data;
}

export async function updateAppointment(id, payload) {
  const response = await apiFetch(`/api/appointments/${id}`, { method: "PUT", body: JSON.stringify(payload) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Randevu güncellenemedi.");
  return data;
}

export async function cancelAppointment(id) {
  const response = await apiFetch(`/api/appointments/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Randevu iptal edilemedi.");
}
