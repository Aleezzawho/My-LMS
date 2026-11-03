"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useSession } from "./session-provider";

export function UserMenu() {
  const t = useTranslations("nav");
  const { user, status, signOut } = useSession();
  const router = useRouter();

  if (status === "loading") {
    return <span className="inline-block h-9 w-20 animate-pulse rounded-lg bg-line/60" aria-hidden />;
  }

  if (!user) {
    return (
      <Link href="/login" className="btn-primary">
        {t("login")}
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-1">
      <Link href="/dashboard" className="btn-ghost">
        {t("dashboard")}
      </Link>
      <button
        type="button"
        className="btn-outline"
        onClick={async () => {
          await signOut();
          router.push("/");
        }}
      >
        {t("logout")}
      </button>
    </div>
  );
}
