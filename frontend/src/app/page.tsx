import Link from "next/link";
import { BookOpen, Gavel, Trophy } from "lucide-react";
import { useTranslations } from "next-intl";

export default function HomePage() {
  const t = useTranslations("home");
  const features = [
    { icon: BookOpen, title: t("featureCourses"), body: t("featureCoursesBody") },
    { icon: Gavel, title: t("featureJudge"), body: t("featureJudgeBody") },
    { icon: Trophy, title: t("featureContests"), body: t("featureContestsBody") },
  ];

  return (
    <div className="space-y-16">
      <section className="mx-auto max-w-prose space-y-6 py-10 text-center">
        <h1 className="text-3xl font-bold leading-tight sm:text-4xl">{t("headline")}</h1>
        <p className="text-lg text-muted">{t("subhead")}</p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/login" className="btn-primary px-6">
            {t("cta")}
          </Link>
          <Link href="/contests" className="btn-outline px-6">
            {t("secondaryCta")}
          </Link>
        </div>
      </section>
      <section className="grid gap-4 sm:grid-cols-3">
        {features.map(({ icon: Icon, title, body }) => (
          <article key={title} className="card space-y-2 p-6">
            <Icon aria-hidden className="size-6 text-brand" />
            <h2 className="font-bold">{title}</h2>
            <p className="text-sm text-muted">{body}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
