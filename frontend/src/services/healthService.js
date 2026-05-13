import apiClient from './apiClient.js';

export async function healthCheck() {
  const { data } = await apiClient.get('/health');
  return data;
}
