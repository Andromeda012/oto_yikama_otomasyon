import { apiFetch } from "./api";

async function parseResponse(response, fallback) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || fallback);
  return data;
}

export async function getAppointments(date, status = "") {
  const params = new URLSearchParams();
  if (date) params.set("date", date);
  if (status) params.set("status", status);
  return parseResponse(
    await apiFetch(`/api/appointments?${params.toString()}`),
    "Randevular alınamadı."
  );
}

export async function getAppointmentLookups() {
  return parseResponse(
    await apiFetch("/api/appointments/lookups"),
    "Tanımlar alınamadı."
  );
}

export async function createAppointment(payload) {
  return parseResponse(
    await apiFetch("/api/appointments", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
    "Randevu oluşturulamadı."
  );
}

export async function updateAppointment(id, payload) {
  return parseResponse(
    await apiFetch(`/api/appointments/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
    "Randevu güncellenemedi."
  );
}

export async function updateAppointmentStatus(id, status) {
  return parseResponse(
    await apiFetch(`/api/appointments/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
    "Randevu durumu güncellenemedi."
  );
}

export async function cancelAppointment(id) {
  return parseResponse(
    await apiFetch(`/api/appointments/${id}`, { method: "DELETE" }),
    "Randevu iptal edilemedi."
  );
}
