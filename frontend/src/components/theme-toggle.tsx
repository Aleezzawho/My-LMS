"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

type Pref = "system" | "light" | "dark";
const ORDER: Pref[] = ["system", "light", "dark"];
const STORAGE_KEY = "lms-theme";

function apply(pref: Pref) {
  const dark =
    pref === "dark" || (pref === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  document.documentElement.dataset.themePref = pref;
}

export function ThemeToggle() {
  const t = useTranslations("theme");
  const [pref, setPref] = useState<Pref>("system");

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    setPref(stored === "light" || stored === "dark" ? stored : "system");
  }, []);

  useEffect(() => {
    if (pref !== "system") return;
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = () => apply("system");
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, [pref]);

  function cycle() {
    const next = ORDER[(ORDER.indexOf(pref) + 1) % ORDER.length];
    setPref(next);
    if (next === "system") localStorage.removeItem(STORAGE_KEY);
    else localStorage.setItem(STORAGE_KEY, next);
    apply(next);
  }

  const Icon = pref === "dark" ? Moon : pref === "light" ? Sun : Monitor;
  const label = `${t("label")}: ${t(pref)}`;

  return (
    <button type="button" onClick={cycle} className="btn-ghost px-2.5" aria-label={label} title={label}>
      <Icon aria-hidden className="size-5" />
    </button>
  );
}
