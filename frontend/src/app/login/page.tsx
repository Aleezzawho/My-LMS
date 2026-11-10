import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { LoginForm } from "./login-form";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("auth");
  return { title: t("title"), robots: { index: false } };
}

export default async function LoginPage() {
  const t = await getTranslations("auth");
  return (
    <div className="mx-auto max-w-md">
      <div className="card space-y-6 p-6 sm:p-8">
        <header className="space-y-1">
          <h1 className="text-2xl font-bold">{t("title")}</h1>
          <p className="text-sm text-muted">{t("subtitle")}</p>
        </header>
        <LoginForm />
      </div>
    </div>
  );
}
