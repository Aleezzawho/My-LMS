import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, readCookie, request } from "./api";

function jsonResponse(status: number, body: unknown) {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("readCookie", () => {
  it("finds a cookie among many", () => {
    expect(readCookie("lms_csrf", "a=1; lms_csrf=abc%3D; b=2")).toBe("abc=");
  });
  it("returns null when missing", () => {
    expect(readCookie("lms_csrf", "a=1")).toBeNull();
  });
});

describe("request", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    vi.stubGlobal("document", { cookie: "lms_csrf=token123" });
  });

  afterEach(() => {
    fetchMock.mockReset();
    vi.unstubAllGlobals();
  });

  it("sends the CSRF header on mutations only", async () => {
    fetchMock.mockImplementation(async () => jsonResponse(200, { ok: true }));
    await request("POST", "/x", {});
    await request("GET", "/y");
    expect(fetchMock.mock.calls[0][1].headers["X-CSRF-Token"]).toBe("token123");
    expect(fetchMock.mock.calls[1][1].headers["X-CSRF-Token"]).toBeUndefined();
  });

  it("raises the backend error envelope", async () => {
    fetchMock.mockResolvedValue(jsonResponse(400, { code: "otp_invalid", message: "bad" }));
    await expect(request("POST", "/auth/otp/verify", {})).rejects.toMatchObject({
      status: 400,
      code: "otp_invalid",
    });
  });

  it("refreshes once on 401 then retries", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(401, { code: "token_expired", message: "x" }))
      .mockResolvedValueOnce(jsonResponse(200, { access_token: "new" }))
      .mockResolvedValueOnce(jsonResponse(200, { id: "u1" }));
    const result = await request<{ id: string }>("GET", "/auth/me");
    expect(result.id).toBe("u1");
    expect(fetchMock.mock.calls.map((call) => call[0])).toEqual([
      "/api/v1/auth/me",
      "/api/v1/auth/refresh",
      "/api/v1/auth/me",
    ]);
  });

  it("does not loop when refresh fails", async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(401, { code: "token_expired", message: "x" }))
      .mockResolvedValueOnce(jsonResponse(401, { code: "refresh_expired", message: "x" }));
    await expect(request("GET", "/auth/me")).rejects.toBeInstanceOf(ApiError);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("never refreshes for auth endpoints", async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { code: "invalid_credentials", message: "x" }));
    await expect(request("POST", "/auth/login", {})).rejects.toMatchObject({ code: "invalid_credentials" });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("maps network failures", async () => {
    fetchMock.mockRejectedValueOnce(new TypeError("fail"));
    await expect(request("GET", "/auth/me")).rejects.toMatchObject({ code: "network", status: 0 });
  });

  it("returns undefined for 204", async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
    await expect(request("POST", "/auth/otp/request", {})).resolves.toBeUndefined();
  });
});
