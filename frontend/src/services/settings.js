import { api } from './api';
export const getSettings = () => api('/settings');
export const updateSettings = (data) => api('/settings', { method: 'PUT', body: JSON.stringify(data) });
