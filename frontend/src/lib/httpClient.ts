import axios from "axios";

import { getApiBaseUrl, getAuthToken } from "./api";

export const httpClient = axios.create({
  baseURL: getApiBaseUrl(),
});

httpClient.defaults.headers.common["Accept"] = "application/json";

httpClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    const headers = config.headers ?? {};
    if (!("Authorization" in headers) || !headers.Authorization) {
      (headers as Record<string, string>).Authorization = `Bearer ${token}`;
    }
    config.headers = headers;
  }
  return config;
});
