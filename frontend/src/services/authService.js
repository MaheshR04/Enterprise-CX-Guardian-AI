import apiClient from './apiClient.js';

export async function signupRequest(payload) {
  const { data } = await apiClient.post('/auth/signup', payload);
  return data;
}

export async function loginRequest(payload) {
  const { data } = await apiClient.post('/auth/login', payload);
  return data;
}

export async function getCurrentUserRequest() {
  const { data } = await apiClient.get('/auth/me');
  return data;
}

export async function updateGuardianContactsRequest(guardianContacts) {
  const { data } = await apiClient.put('/auth/guardian-contacts', { guardianContacts });
  return data;
}

export async function logoutRequest() {
  const { data } = await apiClient.post('/auth/logout');
  return data;
}
