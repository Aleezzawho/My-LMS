import Link from "next/link";
import { useTranslations } from "next-intl";

export default function NotFound() {
  const t = useTranslations("notFound");
  return (
    <div className="mx-auto max-w-prose space-y-4 py-20 text-center">
      <h1 className="text-2xl font-bold">{t("title")}</h1>
      <Link href="/" className="btn-outline">
        {t("back")}
      </Link>
    </div>
  );
}
