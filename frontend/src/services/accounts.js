import { apiFetch } from "./api";

async function request(path, options = {}) {
  const response = await apiFetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Cari işlemi tamamlanamadı.");
  return data;
}

export function getAccountSummary() { return request("/api/accounts/summary"); }
export function getAccountCustomers(search = "") {
  const params = new URLSearchParams();
  if (search.trim()) params.set("search", search.trim());
  return request(`/api/accounts/customers?${params}`);
}
export function getAccountCustomer(id) { return request(`/api/accounts/customers/${id}`); }
export function quickSearchAccounts(query = "") {
  const params = new URLSearchParams({ q: query });
  return request(`/api/accounts/quick-search?${params}`);
}
export function getAccountTransactions(customerId = "") {
  const params = new URLSearchParams({ limit: "100" });
  if (customerId) params.set("customer_id", customerId);
  return request(`/api/accounts/transactions?${params}`);
}
export function receivePayment(customerId, payload) {
  return request(`/api/accounts/customers/${customerId}/payments`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
