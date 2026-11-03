import { describe, expect, it } from "vitest";
import { maskPhone, normalizePhone, sanitizeOtp, toLatinDigits, toPersianDigits } from "./phone";

describe("normalizePhone", () => {
  it.each([
    ["09121234567", "+989121234567"],
    ["+989121234567", "+989121234567"],
    ["00989121234567", "+989121234567"],
    ["9121234567", "+989121234567"],
    ["0912 123 4567", "+989121234567"],
    ["۰۹۱۲۱۲۳۴۵۶۷", "+989121234567"],
    ["٠٩١٢١٢٣٤٥٦٧", "+989121234567"],
  ])("accepts %s", (raw, expected) => {
    expect(normalizePhone(raw)).toBe(expected);
  });

  it.each(["", "12345", "08121234567", "+1234567890", "abcdefghijk"])("rejects %s", (raw) => {
    expect(normalizePhone(raw)).toBeNull();
  });
});

describe("digits", () => {
  it("round-trips Persian digits", () => {
    expect(toLatinDigits(toPersianDigits("0123456789"))).toBe("0123456789");
  });
});

describe("sanitizeOtp", () => {
  it("keeps six latin digits", () => {
    expect(sanitizeOtp("۱۲۳ ۴۵۶۷")).toBe("123456");
  });
});

describe("maskPhone", () => {
  it("masks the middle", () => {
    expect(maskPhone("+989121234567")).toBe("0912***4567");
  });
});
