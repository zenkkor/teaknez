import { chromium } from "playwright";

const pages = [
  ["home", "/"],
  ["omeni", "/o-meni.html"],
  ["storitve", "/storitve.html"],
  ["osebni", "/storitve/osebni-coaching.html"],
  ["blog", "/blog/"],
  ["post", "/blog/samozavest-ni-nekaj-kar-imas/"],
  ["kontakt", "/kontakt.html"],
];

const browser = await chromium.launch();
for (const [vp, w, h] of [["d", 1440, 900], ["m", 390, 844]]) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const pg = await ctx.newPage();
  for (const [name, url] of pages) {
    await pg.goto("http://localhost:8765" + url, { waitUntil: "networkidle" });
    await pg.screenshot({ path: `.pw/full-${name}-${vp}.png`, fullPage: true });
    console.log(`wrote .pw/full-${name}-${vp}.png`);
  }
  await ctx.close();
}
await browser.close();
