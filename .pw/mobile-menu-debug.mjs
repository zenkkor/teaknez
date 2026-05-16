import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const pg = await ctx.newPage();
const errors = [];
pg.on("pageerror", (e) => errors.push("PAGEERR: " + String(e)));
pg.on("console", (m) => { if (m.type() === "error") errors.push("CONS: " + m.text()); });

await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });

// Screenshot closed state
await pg.screenshot({ path: "/tmp/mm-closed.png" });

// Inspect toggle button visibility and styles
const closedInfo = await pg.evaluate(() => {
  const t = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  return {
    toggleExists: !!t,
    toggleVisible: t ? getComputedStyle(t).display : "MISSING",
    toggleRect: t ? t.getBoundingClientRect() : null,
    navExists: !!nav,
    navDisplay: nav ? getComputedStyle(nav).display : "MISSING",
    navVisibility: nav ? getComputedStyle(nav).visibility : null,
    navTransform: nav ? getComputedStyle(nav).transform : null,
    navRect: nav ? nav.getBoundingClientRect() : null,
    bodyClass: document.body.className,
  };
});
console.log("=== closed ===");
console.log(JSON.stringify(closedInfo, null, 2));

await pg.click(".nav-toggle");
await pg.waitForTimeout(500);
await pg.screenshot({ path: "/tmp/mm-open.png" });

const openInfo = await pg.evaluate(() => {
  const nav = document.querySelector(".site-nav");
  const list = nav.querySelector(".nav-list");
  const links = Array.from(nav.querySelectorAll(".nav-link, .dropdown-link, .nav-cta"));
  return {
    navOpen: nav.classList.contains("is-open"),
    bodyNavOpen: document.body.classList.contains("nav-open"),
    navRect: nav.getBoundingClientRect(),
    navBg: getComputedStyle(nav).backgroundColor,
    navColor: getComputedStyle(nav).color,
    navZ: getComputedStyle(nav).zIndex,
    listRect: list ? list.getBoundingClientRect() : null,
    listBg: list ? getComputedStyle(list).backgroundColor : null,
    linkSamples: links.slice(0, 6).map((l) => ({
      text: l.textContent.trim().slice(0, 30),
      cls: l.className,
      color: getComputedStyle(l).color,
      bg: getComputedStyle(l).backgroundColor,
      padding: getComputedStyle(l).padding,
      display: getComputedStyle(l).display,
      visible: l.getBoundingClientRect().height > 0,
      rect: l.getBoundingClientRect(),
    })),
  };
});
console.log("\n=== open ===");
console.log(JSON.stringify(openInfo, null, 2));

// Try dropdown expand
console.log("\n=== expand Storitve dropdown ===");
const dropdownClickResult = await pg.evaluate(() => {
  const dd = document.querySelector(".nav-item-dropdown .nav-link");
  if (!dd) return "no dropdown link";
  dd.click();
  return "clicked";
});
console.log(dropdownClickResult);
await pg.waitForTimeout(500);
await pg.screenshot({ path: "/tmp/mm-submenu.png" });
const subInfo = await pg.evaluate(() => {
  const dd = document.querySelector(".nav-item-dropdown");
  const menu = dd ? dd.querySelector(".dropdown-menu") : null;
  return {
    ddExpanded: dd ? dd.getAttribute("aria-expanded") : null,
    menuDisplay: menu ? getComputedStyle(menu).display : null,
    menuRect: menu ? menu.getBoundingClientRect() : null,
    menuBg: menu ? getComputedStyle(menu).backgroundColor : null,
    items: menu ? Array.from(menu.querySelectorAll(".dropdown-link")).map((l) => ({
      text: l.textContent.trim().slice(0, 60),
      display: getComputedStyle(l).display,
      color: getComputedStyle(l).color,
      rect: l.getBoundingClientRect(),
    })) : [],
  };
});
console.log(JSON.stringify(subInfo, null, 2));

console.log("\n=== errors ===");
errors.slice(0, 10).forEach((e) => console.log(" -", e));

await browser.close();
