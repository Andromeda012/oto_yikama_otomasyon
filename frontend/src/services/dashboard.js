import { api } from "./api";

export function getDashboard(date) {
  const query = date ? `?date=${encodeURIComponent(date)}` : "";
  return api(`/dashboard${query}`);
}
