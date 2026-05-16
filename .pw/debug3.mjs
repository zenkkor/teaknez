import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const pg = await ctx.newPage();
await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });
await pg.click(".nav-toggle");
await pg.waitForTimeout(400);
await pg.click(".nav-item-dropdown .nav-link");
await pg.waitForTimeout(400);

const info = await pg.evaluate(() => {
  const dd = document.querySelector(".nav-item-dropdown");
  const menu = dd.querySelector(".dropdown-menu");
  const links = Array.from(menu.querySelectorAll(".dropdown-link"));
  return {
    ddExpanded: dd.getAttribute("aria-expanded"),
    menuDisplay: getComputedStyle(menu).display,
    menuRect: menu.getBoundingClientRect(),
    menuColor: getComputedStyle(menu).color,
    menuBg: getComputedStyle(menu).backgroundColor,
    links: links.map((l) => ({
      text: l.textContent.trim().slice(0, 40),
      display: getComputedStyle(l).display,
      color: getComputedStyle(l).color,
      bg: getComputedStyle(l).backgroundColor,
      rect: l.getBoundingClientRect(),
      visibility: getComputedStyle(l).visibility,
      opacity: getComputedStyle(l).opacity,
    })),
  };
});
console.log(JSON.stringify(info, null, 2));
await browser.close();
