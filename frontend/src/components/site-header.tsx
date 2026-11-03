import Link from "next/link";
import { useTranslations } from "next-intl";
import { ThemeToggle } from "./theme-toggle";
import { UserMenu } from "./user-menu";

export function SiteHeader() {
  const t = useTranslations("nav");
  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface/85 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-6 px-4">
        <Link href="/" className="text-lg font-bold text-ink">
          {t("brand")}
        </Link>
        <nav aria-label={t("brand")} className="hidden items-center gap-1 sm:flex">
          <Link href="/courses" className="btn-ghost">
            {t("courses")}
          </Link>
          <Link href="/problems" className="btn-ghost">
            {t("problems")}
          </Link>
          <Link href="/contests" className="btn-ghost">
            {t("contests")}
          </Link>
        </nav>
        <div className="ms-auto flex items-center gap-2">
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
