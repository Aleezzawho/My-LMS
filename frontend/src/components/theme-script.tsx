/**
 * Runs before hydration to set `data-theme` and avoid a light/dark flash.
 * The preference lives in localStorage; "system" follows the OS.
 */
const script = `(() => {
  try {
    var stored = localStorage.getItem("lms-theme");
    var pref = stored === "light" || stored === "dark" ? stored : "system";
    var dark = pref === "dark" || (pref === "system" && matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    document.documentElement.dataset.themePref = pref;
  } catch (_) {}
})();`;

export function ThemeScript() {
  return <script dangerouslySetInnerHTML={{ __html: script }} />;
}
