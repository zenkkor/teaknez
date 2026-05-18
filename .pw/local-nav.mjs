import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const pg = await ctx.newPage();
await pg.goto("http://localhost:8765/o-meni.html", { waitUntil: "networkidle" });
const info = await pg.evaluate(() => {
  const li = document.querySelector(".nav-list > li");
  const a = li.querySelector(".nav-link");
  const cta = document.querySelector(".nav-cta");
  const list = document.querySelector(".nav-list");
  return {
    list: { top: list.getBoundingClientRect().top, bottom: list.getBoundingClientRect().bottom },
    li: { top: li.getBoundingClientRect().top, bottom: li.getBoundingClientRect().bottom },
    navLink: { top: a.getBoundingClientRect().top, bottom: a.getBoundingClientRect().bottom },
    cta: { top: cta.getBoundingClientRect().top, bottom: cta.getBoundingClientRect().bottom },
  };
});
console.log(JSON.stringify(info, null, 2));
await browser.close();
