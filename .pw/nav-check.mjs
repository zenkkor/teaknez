import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const pg = await ctx.newPage();
await pg.goto("http://localhost:8765/o-meni.html", { waitUntil: "networkidle" });
const info = await pg.evaluate(() => {
  const nav = document.querySelector(".site-nav");
  const list = document.querySelector(".nav-list");
  const cta = document.querySelector(".nav-cta");
  return {
    nav: { rect: nav.getBoundingClientRect(), cs: { alignItems: getComputedStyle(nav).alignItems, height: getComputedStyle(nav).height } },
    list: { rect: list.getBoundingClientRect(), cs: { height: getComputedStyle(list).height, alignItems: getComputedStyle(list).alignItems } },
    cta: { rect: cta.getBoundingClientRect(), cs: { height: getComputedStyle(cta).height, marginTop: getComputedStyle(cta).marginTop } },
  };
});
console.log(JSON.stringify(info, null, 2));
const el = await pg.$(".site-header");
if (el) await el.screenshot({ path: ".pw/nav-d.png" });
await browser.close();
