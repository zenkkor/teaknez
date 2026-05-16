import { chromium } from "playwright";
const b = await chromium.launch();
const pages = [
  ["home", "/"],
  ["o-meni", "/o-meni.html"],
  ["osebni", "/storitve/osebni-coaching.html"],
  ["kontakt", "/kontakt.html"],
];
for (const [vp, w, h] of [["d", 1440, 900], ["m", 390, 844]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } });
  const pg = await ctx.newPage();
  for (const [name, url] of pages) {
    await pg.goto("http://localhost:8765" + url, { waitUntil: "networkidle" });
    await pg.evaluate(() => {
      const els = document.querySelectorAll(".btn-primary, button.btn-primary");
      if (!els.length) return;
      const el = els[els.length - 1];
      el.scrollIntoView({ block: "center" });
    });
    await pg.waitForTimeout(300);
    await pg.screenshot({ path: `/tmp/pm-${vp}-${name}.png` });
  }
  await ctx.close();
}
await b.close();
console.log("done");
