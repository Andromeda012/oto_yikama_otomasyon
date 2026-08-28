import { apiFetch } from "./api";

async function parseResponse(response, fallback) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || fallback);
  return data;
}

export async function getMarketProducts(search = "") {
  const params = new URLSearchParams();
  if (search.trim()) params.set("search", search.trim());
  return parseResponse(await apiFetch(`/api/market/products?${params}`), "Ürünler alınamadı.");
}

export async function getMarketLookups() {
  return parseResponse(await apiFetch("/api/market/lookups"), "Market bilgileri alınamadı.");
}

export async function getMarketSummary() {
  return parseResponse(await apiFetch("/api/market/summary"), "Market özeti alınamadı.");
}

export async function getRecentSales() {
  return parseResponse(await apiFetch("/api/market/sales?limit=8"), "Son satışlar alınamadı.");
}

export async function createMarketSale(payload) {
  return parseResponse(
    await apiFetch("/api/market/sales", { method: "POST", body: JSON.stringify(payload) }),
    "Satış kaydedilemedi."
  );
}

export async function getStockMovements(limit = 50) {
  return parseResponse(await apiFetch(`/api/market/stock-movements?limit=${limit}`), "Stok hareketleri alınamadı.");
}
