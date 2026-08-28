import { api } from './api';

export async function getStatistics(params = {}) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      query.set(key, value);
    }
  });

  const queryString = query.toString();

  return api(`/statistics${queryString ? `?${queryString}` : ''}`);
}
