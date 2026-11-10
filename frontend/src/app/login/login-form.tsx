"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useEffect, useState, type FormEvent } from "react";
import { useSession } from "@/components/session-provider";
import { api, ApiError } from "@/lib/api";
import { maskPhone, normalizePhone, sanitizeOtp, toPersianDigits } from "@/lib/phone";

type Mode = "otp" | "password";
type Step = "phone" | "code";

const RESEND_SECONDS = 60;

export function LoginForm() {
  const t = useTranslations("auth");
  const te = useTranslations("errors");
  const router = useRouter();
  const { setUser } = useSession();

  const [mode, setMode] = useState<Mode>("otp");
  const [step, setStep] = useState<Step>("phone");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = window.setTimeout(() => setCooldown((value) => value - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [cooldown]);

  function describe(err: unknown): string {
    const code = err instanceof ApiError ? err.code : "generic";
    return te.has(code) ? te(code) : te("generic");
  }

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await action();
    } catch (err) {
      setError(describe(err));
    } finally {
      setBusy(false);
    }
  }

  function normalizedOrFail(): string | null {
    const normalized = normalizePhone(phone);
    if (!normalized) setError(te("invalid_phone"));
    return normalized;
  }

  async function sendCode(event?: FormEvent) {
    event?.preventDefault();
    const normalized = normalizedOrFail();
    if (!normalized) return;
    await run(async () => {
      await api.requestOtp(normalized);
      setStep("code");
      setCode("");
      setCooldown(RESEND_SECONDS);
    });
  }

  async function verifyCode(event: FormEvent) {
    event.preventDefault();
    const normalized = normalizedOrFail();
    if (!normalized) return;
    if (code.length !== 6) {
      setError(te("invalid_code_format"));
      return;
    }
    await run(async () => {
      const result = await api.verifyOtp(normalized, code);
      setUser(result.user);
      router.push("/dashboard");
    });
  }

  async function passwordLogin(event: FormEvent) {
    event.preventDefault();
    const normalized = normalizedOrFail();
    if (!normalized) return;
    await run(async () => {
      const result = await api.login(normalized, password);
      setUser(result.user);
      router.push("/dashboard");
    });
  }

  const normalizedPhone = normalizePhone(phone);

  return (
    <div className="space-y-5">
      <div role="tablist" aria-label={t("title")} className="grid grid-cols-2 rounded-lg bg-line/50 p-1">
        {(["otp", "password"] as const).map((value) => (
          <button
            key={value}
            type="button"
            role="tab"
            aria-selected={mode === value}
            className={`rounded-md py-2 text-sm font-medium transition-colors ${
              mode === value ? "bg-elevated text-ink shadow-sm" : "text-muted hover:text-ink"
            }`}
            onClick={() => {
              setMode(value);
              setStep("phone");
              setError(null);
            }}
          >
            {value === "otp" ? t("tabOtp") : t("tabPassword")}
          </button>
        ))}
      </div>

      {mode === "otp" && step === "phone" && (
        <form className="space-y-4" onSubmit={sendCode} noValidate>
          <PhoneField value={phone} onChange={setPhone} label={t("phoneLabel")} placeholder={t("phonePlaceholder")} />
          <button type="submit" className="btn-primary w-full" disabled={busy}>
            {busy ? t("sending") : t("sendCode")}
          </button>
        </form>
      )}

      {mode === "otp" && step === "code" && (
        <form className="space-y-4" onSubmit={verifyCode} noValidate>
          <p className="text-sm text-muted">
            {t("codeHint", { phone: toPersianDigits(normalizedPhone ? maskPhone(normalizedPhone) : phone) })}
          </p>
          <div className="space-y-1.5">
            <label htmlFor="otp-code" className="text-sm font-medium">
              {t("codeLabel")}
            </label>
            <input
              id="otp-code"
              className="field text-center font-mono text-xl tracking-[0.5em]"
              inputMode="numeric"
              autoComplete="one-time-code"
              autoFocus
              maxLength={12}
              value={code}
              onChange={(event) => setCode(sanitizeOtp(event.target.value))}
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={busy || code.length !== 6}>
            {busy ? t("verifying") : t("verify")}
          </button>
          <div className="flex items-center justify-between text-sm">
            <button type="button" className="text-brand hover:underline" onClick={() => setStep("phone")}>
              {t("changePhone")}
            </button>
            <button
              type="button"
              className="text-brand hover:underline disabled:text-muted disabled:no-underline"
              disabled={cooldown > 0 || busy}
              onClick={() => void sendCode()}
            >
              {cooldown > 0 ? t("resendIn", { seconds: toPersianDigits(String(cooldown)) }) : t("resend")}
            </button>
          </div>
        </form>
      )}

      {mode === "password" && (
        <form className="space-y-4" onSubmit={passwordLogin} noValidate>
          <PhoneField value={phone} onChange={setPhone} label={t("phoneLabel")} placeholder={t("phonePlaceholder")} />
          <div className="space-y-1.5">
            <label htmlFor="password" className="text-sm font-medium">
              {t("passwordLabel")}
            </label>
            <input
              id="password"
              type="password"
              className="field"
              dir="ltr"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={busy || !password}>
            {busy ? t("verifying") : t("login")}
          </button>
        </form>
      )}

      <p role="alert" aria-live="polite" className="min-h-6 text-sm text-danger">
        {error}
      </p>
    </div>
  );
}

function PhoneField(props: { value: string; onChange: (value: string) => void; label: string; placeholder: string }) {
  return (
    <div className="space-y-1.5">
      <label htmlFor="phone" className="text-sm font-medium">
        {props.label}
      </label>
      <input
        id="phone"
        type="tel"
        className="field"
        inputMode="numeric"
        autoComplete="tel"
        autoFocus
        placeholder={props.placeholder}
        value={props.value}
        onChange={(event) => props.onChange(event.target.value)}
      />
    </div>
  );
}
