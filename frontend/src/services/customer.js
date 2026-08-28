import { apiFetch } from "./api";

async function parse(response, fallback) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || fallback);
  return data;
}

export async function getCompanyPublic() {
  return parse(await apiFetch("/api/public/company"), "İşletme bilgileri alınamadı.");
}

export async function getPublicServices() {
  return parse(await apiFetch("/api/public/services"), "Hizmetler alınamadı.");
}

export async function getAvailability(date, serviceId = "") {
  const params = new URLSearchParams({ date });
  if (serviceId) params.set("service_id", serviceId);
  return parse(await apiFetch(`/api/public/availability?${params}`), "Müsait saatler alınamadı.");
}

export async function createCustomerAppointment(payload) {
  return parse(await apiFetch("/api/public/appointments", { method: "POST", body: JSON.stringify(payload) }), "Randevu oluşturulamadı.");
}

export async function getCustomerAppointments(phone, plate) {
  const params = new URLSearchParams({ phone, plate });
  return parse(await apiFetch(`/api/public/appointments?${params}`), "Randevular alınamadı.");
}

export async function updateCustomerAppointment(id, payload) {
  return parse(await apiFetch(`/api/public/appointments/${id}`, { method: "PUT", body: JSON.stringify(payload) }), "Randevu güncellenemedi.");
}

export async function getCustomerProfile(phone) {
  const params = new URLSearchParams({ phone });
  return parse(await apiFetch(`/api/public/account?${params}`), "Hesap bilgileri alınamadı.");
}

export async function saveCustomerProfile(payload) {
  return parse(await apiFetch("/api/public/account", { method: "POST", body: JSON.stringify(payload) }), "Hesap bilgileri kaydedilemedi.");
}
