import { getRequestConfig } from "next-intl/server";
import { defaultLocale } from "./config";

export default getRequestConfig(async () => {
  const locale = defaultLocale;
  return {
    locale,
    timeZone: "Asia/Tehran",
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
