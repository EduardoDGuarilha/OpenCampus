const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

export const AUTH_TOKEN_STORAGE_KEY = "opencampus.authToken";

export class ApiError extends Error {
  public readonly status: number;

  public readonly detail: string | null;

  public readonly payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
    this.detail = ApiError.extractDetail(payload);
  }

  private static extractDetail(payload: unknown): string | null {
    if (payload && typeof payload === "object" && "detail" in payload) {
      const value = (payload as { detail?: unknown }).detail;
      if (typeof value === "string") {
        return value;
      }
      if (Array.isArray(value)) {
        const first = value[0];
        if (typeof first === "string") {
          return first;
        }
        if (first && typeof first === "object" && "msg" in first) {
          const message = (first as { msg?: unknown }).msg;
          if (typeof message === "string") {
            return message;
          }
        }
      }
    }
    return null;
  }
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
  } catch (error) {
    console.warn("Unable to read auth token from storage", error);
    return null;
  }
}

function resolveBaseUrl(): string {
  const envUrl = (import.meta as { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL;
  const baseUrl = envUrl && envUrl.trim().length > 0 ? envUrl : DEFAULT_API_BASE_URL;
  return baseUrl.replace(/\/$/, "");
}

const API_BASE_URL = resolveBaseUrl();

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const urlPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${API_BASE_URL}${urlPath}`;

  const headers = new Headers(options.headers);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  const token = getAuthToken();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url, { ...options, headers });

  if (response.status === 204) {
    return undefined as T;
  }

  let parsed: unknown = null;
  const contentType = response.headers.get("content-type");
  const isJson = contentType?.includes("application/json");

  if (isJson) {
    try {
      parsed = await response.json();
    } catch (error) {
      if (response.ok) {
        throw new ApiError("Invalid JSON response", response.status, null);
      }
      parsed = null;
    }
  } else {
    const text = await response.text();
    parsed = text.length > 0 ? text : null;
  }

  if (!response.ok) {
    throw new ApiError(
      `Request to ${url} failed with status ${response.status}`,
      response.status,
      parsed,
    );
  }

  return parsed as T;
}

export function buildQuery(params: Record<string, string | number | boolean | null | undefined>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined) {
      return;
    }
    query.append(key, String(value));
  });
  const queryString = query.toString();
  return queryString.length > 0 ? `?${queryString}` : "";
}
