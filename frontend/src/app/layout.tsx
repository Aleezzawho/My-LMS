import type { Metadata, Viewport } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages, getTranslations } from "next-intl/server";
import { SessionProvider } from "@/components/session-provider";
import { SiteHeader } from "@/components/site-header";
import { ThemeScript } from "@/components/theme-script";
import { localeDirection, type Locale } from "@/i18n/config";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("meta");
  return {
    title: { default: t("title"), template: `%s | ${t("title")}` },
    description: t("description"),
    manifest: "/manifest.json",
    openGraph: { type: "website", locale: "fa_IR", title: t("title"), description: t("description") },
  };
}

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fafaf9" },
    { media: "(prefers-color-scheme: dark)", color: "#111113" },
  ],
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = (await getLocale()) as Locale;
  const messages = await getMessages();
  const t = await getTranslations("nav");

  return (
    <html lang={locale} dir={localeDirection[locale]} suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:start-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-elevated focus:px-4 focus:py-2"
        >
          {t("skipToContent")}
        </a>
        <NextIntlClientProvider locale={locale} messages={messages} timeZone="Asia/Tehran">
          <SessionProvider>
            <SiteHeader />
            <main id="main" className="mx-auto max-w-6xl px-4 py-10">
              {children}
            </main>
          </SessionProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
