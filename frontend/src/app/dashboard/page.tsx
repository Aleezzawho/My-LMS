"use client";

import { useRouter } from "next/navigation";
import { useFormatter, useTranslations } from "next-intl";
import { useEffect } from "react";
import { useSession } from "@/components/session-provider";
import { maskPhone, toPersianDigits } from "@/lib/phone";

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const tr = useTranslations("roles");
  const format = useFormatter();
  const router = useRouter();
  const { user, status } = useSession();

  useEffect(() => {
    if (status === "anonymous") router.replace("/login");
  }, [status, router]);

  if (!user) {
    return <p className="text-muted">{t("loading")}</p>;
  }

  const name = user.profile.display_name || toPersianDigits(maskPhone(user.phone));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t("welcome", { name })}</h1>
      <dl className="card grid gap-4 p-6 sm:grid-cols-3">
        <div>
          <dt className="text-sm text-muted">{t("phone")}</dt>
          <dd className="ltr text-start font-mono">{maskPhone(user.phone)}</dd>
        </div>
        <div>
          <dt className="text-sm text-muted">{t("roles")}</dt>
          <dd>{user.roles.map((role) => (tr.has(role) ? tr(role) : role)).join(t("listSeparator"))}</dd>
        </div>
        <div>
          <dt className="text-sm text-muted">{t("joined")}</dt>
          <dd>{format.dateTime(new Date(user.date_joined), { dateStyle: "long" })}</dd>
        </div>
      </dl>
      <p className="text-muted">{t("comingSoon")}</p>
    </div>
  );
}
