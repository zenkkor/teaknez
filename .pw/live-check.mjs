import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const pg = await ctx.newPage();
await pg.goto("https://teaknez.com/o-meni.html", { waitUntil: "networkidle" });
const info = await pg.evaluate(() => {
  const list = document.querySelector(".nav-list");
  const cs = getComputedStyle(list);
  return {
    listRect: list.getBoundingClientRect(),
    height: cs.height,
    minHeight: cs.minHeight,
    paddingTop: cs.paddingTop,
    paddingBottom: cs.paddingBottom,
    marginTop: cs.marginTop,
    transform: cs.transform,
    display: cs.display,
    alignItems: cs.alignItems,
    boxSizing: cs.boxSizing,
    overflowY: cs.overflowY,
  };
});
console.log(JSON.stringify(info, null, 2));
const el = await pg.$(".site-header");
if (el) await el.screenshot({ path: ".pw/nav-live.png" });
await browser.close();
