const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩";

export function toLatinDigits(value: string): string {
  return value.replace(/[۰-۹٠-٩]/g, (char) => {
    const persian = PERSIAN_DIGITS.indexOf(char);
    if (persian >= 0) return String(persian);
    return String(ARABIC_DIGITS.indexOf(char));
  });
}

export function toPersianDigits(value: string): string {
  return value.replace(/\d/g, (digit) => PERSIAN_DIGITS[Number(digit)]);
}

/** Mirrors backend `normalize_phone`; returns null for anything invalid. */
export function normalizePhone(raw: string): string | null {
  let candidate = toLatinDigits(raw).replace(/[\s\-()]/g, "");
  if (candidate.startsWith("00")) candidate = `+${candidate.slice(2)}`;
  const match = /^(?:\+98|98|0)?(9\d{9})$/.exec(candidate);
  return match ? `+98${match[1]}` : null;
}

export function maskPhone(phone: string): string {
  const local = phone.startsWith("+98") ? `0${phone.slice(3)}` : phone;
  return local.length >= 8 ? `${local.slice(0, 4)}***${local.slice(-4)}` : local;
}

export function sanitizeOtp(raw: string): string {
  return toLatinDigits(raw).replace(/\D/g, "").slice(0, 6);
}
