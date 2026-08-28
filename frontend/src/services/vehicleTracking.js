import { apiFetch } from "./api";

async function parseResponse(response, fallback) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || fallback);
  return data;
}

export async function getVehicleJobs(date, status = "") {
  const params = new URLSearchParams();
  if (date) params.set("date", date);
  if (status) params.set("status", status);
  return parseResponse(await apiFetch(`/api/vehicle-tracking?${params}`), "Araç takip kayıtları alınamadı.");
}

export async function getAvailableAppointments(date) {
  const params = new URLSearchParams({ date });
  return parseResponse(await apiFetch(`/api/vehicle-tracking/available-appointments?${params}`), "Randevular alınamadı.");
}

export async function getVehicleTrackingLookups() {
  return parseResponse(await apiFetch("/api/vehicle-tracking/lookups"), "Tanımlar alınamadı.");
}

export async function createVehicleJob(payload) {
  return parseResponse(await apiFetch("/api/vehicle-tracking", { method: "POST", body: JSON.stringify(payload) }), "İş emri oluşturulamadı.");
}

export async function createVehicleJobFromAppointment(appointmentId) {
  return parseResponse(await apiFetch(`/api/vehicle-tracking/from-appointment/${appointmentId}`, { method: "POST" }), "Randevu işleme alınamadı.");
}

export async function updateVehicleJobStatus(id, status, staffId = null, note = "") {
  return parseResponse(await apiFetch(`/api/vehicle-tracking/${id}/status`, { method: "PATCH", body: JSON.stringify({ status, staff_id: staffId, note }) }), "Durum güncellenemedi.");
}

export async function updateVehicleJob(id, payload) {
  return parseResponse(await apiFetch(`/api/vehicle-tracking/${id}`, { method: "PUT", body: JSON.stringify(payload) }), "İş emri güncellenemedi.");
}

export async function getVehicleJobHistory(id) {
  return parseResponse(await apiFetch(`/api/vehicle-tracking/${id}/history`), "Durum geçmişi alınamadı.");
}

export async function getVehicleJobFinancial(id) {
  return parseResponse(await apiFetch(`/api/vehicle-tracking/${id}/financial`), "Finansal bilgiler alınamadı.");
}

export async function markVehicleJobPaid(id, paymentMethod = "cash") {
  return parseResponse(
    await apiFetch(`/api/vehicle-tracking/${id}/payment`, {
      method: "PATCH",
      body: JSON.stringify({ payment_method: paymentMethod }),
    }),
    "Ödeme kaydedilemedi."
  );
}
