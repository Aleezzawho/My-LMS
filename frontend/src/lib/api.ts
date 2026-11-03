/**
 * Browser API client. Requests go same-origin through the Next rewrite, so the
 * httpOnly auth cookies are first-party. Mutations echo the `lms_csrf` cookie in
 * `X-CSRF-Token`, and a single 401 triggers one refresh attempt before giving up.
 */

export type ApiErrorBody = {
  code: string;
  message: string;
  details?: unknown;
  request_id?: string;
};

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.status = status;
    this.code = body.code;
    this.details = body.details;
  }
}

export type Profile = {
  display_name: string;
  handle: string | null;
  bio: string;
  theme: "system" | "light" | "dark";
  avatar_url: string | null;
};

export type User = {
  id: string;
  phone: string;
  email: string | null;
  roles: string[];
  profile: Profile;
  date_joined: string;
  has_password: boolean;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
};

// Must stay `/api/v1` so the refresh cookie (path `/api/v1/auth`) is sent by the browser.
const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";
const MUTATING = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const NO_REFRESH = new Set(["/auth/refresh", "/auth/login", "/auth/otp/request", "/auth/otp/verify", "/auth/logout"]);

export function readCookie(name: string, source?: string): string | null {
  const cookieString = source ?? (typeof document === "undefined" ? "" : document.cookie);
  for (const part of cookieString.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key === name) return decodeURIComponent(rest.join("="));
  }
  return null;
}

let refreshing: Promise<boolean> | null = null;

async function refreshSession(): Promise<boolean> {
  if (!refreshing) {
    refreshing = raw("POST", "/auth/refresh")
      .then((response) => response.ok)
      .catch(() => false)
      .finally(() => {
        refreshing = null;
      });
  }
  return refreshing;
}

function raw(method: string, path: string, body?: unknown): Promise<Response> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (MUTATING.has(method)) {
    const csrf = readCookie("lms_csrf");
    if (csrf) headers["X-CSRF-Token"] = csrf;
  }
  return fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: "include",
    cache: "no-store",
  });
}

async function parse<T>(response: Response): Promise<T> {
  if (response.status === 204) return undefined as T;
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const body: ApiErrorBody =
      data && typeof data === "object" && "code" in data
        ? (data as ApiErrorBody)
        : { code: "generic", message: response.statusText };
    throw new ApiError(response.status, body);
  }
  return data as T;
}

export async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await raw(method, path, body);
  } catch {
    throw new ApiError(0, { code: "network", message: "Network error" });
  }
  if (response.status === 401 && !NO_REFRESH.has(path) && (await refreshSession())) {
    response = await raw(method, path, body);
  }
  return parse<T>(response);
}

export const api = {
  requestOtp: (phone: string) => request<void>("POST", "/auth/otp/request", { phone }),
  verifyOtp: (phone: string, code: string) =>
    request<TokenResponse>("POST", "/auth/otp/verify", { phone, code }),
  login: (phone: string, password: string) =>
    request<TokenResponse>("POST", "/auth/login", { phone, password }),
  logout: () => request<void>("POST", "/auth/logout"),
  me: () => request<User>("GET", "/auth/me"),
  updateMe: (patch: Partial<Pick<Profile, "display_name" | "handle" | "bio" | "theme">>) =>
    request<User>("PATCH", "/auth/me", patch),
};
