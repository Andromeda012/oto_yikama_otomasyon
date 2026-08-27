import { api } from './api';

export const getCompanyProfile = () => api('/company-profile');
export const updateCompanyProfile = (data) => api('/company-profile', { method: 'PUT', body: JSON.stringify(data) });
