import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const pg = await ctx.newPage();
await pg.goto("http://localhost:8765/o-meni.html", { waitUntil: "networkidle" });
const info = await pg.evaluate(() => {
  const p = document.querySelector(".page-header--about .about-intro > div:last-child p:first-of-type");
  if (!p) return { error: "no element" };
  const cs = getComputedStyle(p);
  const rect = p.getBoundingClientRect();
  return {
    text: p.textContent.slice(0, 30),
    fontSize: cs.fontSize,
    rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    parentBorderLeft: getComputedStyle(p.parentElement).borderLeft,
    parentPaddingLeft: getComputedStyle(p.parentElement).paddingLeft,
  };
});
console.log(JSON.stringify(info, null, 2));
await browser.close();
