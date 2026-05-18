import { chromium } from "playwright";

const browser = await chromium.launch();
for (const [vp, w, h] of [["d", 1440, 900], ["m", 390, 844]]) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const pg = await ctx.newPage();
  await pg.goto("http://localhost:8765/o-meni.html", { waitUntil: "networkidle" });
  const el = await pg.$(".page-header");
  if (el) {
    await el.screenshot({ path: `.pw/header-${vp}.png` });
    console.log(`wrote .pw/header-${vp}.png`);
  }
  await ctx.close();
}
await browser.close();
