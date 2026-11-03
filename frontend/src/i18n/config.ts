export const locales = ["fa", "en"] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = "fa";

export const localeDirection: Record<Locale, "rtl" | "ltr"> = {
  fa: "rtl",
  en: "ltr",
};
