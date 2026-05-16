import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const pg = await ctx.newPage();
await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });

console.log("\n=== Overflow check on home (390px) ===");
const overflowingElements = await pg.evaluate(() => {
  const docWidth = document.documentElement.clientWidth;
  const result = [];
  document.querySelectorAll("*").forEach((el) => {
    const rect = el.getBoundingClientRect();
    if (rect.right > docWidth + 1 || rect.left < -1) {
      const id = (el.tagName + (el.id ? "#" + el.id : "") + (el.className ? "." + (typeof el.className === "string" ? el.className : "").split(" ").join(".") : "")).slice(0, 100);
      result.push({ id, right: Math.round(rect.right), left: Math.round(rect.left), width: Math.round(rect.width) });
    }
  });
  return result.slice(0, 20);
});
overflowingElements.forEach((e) => console.log("  overflow:", e));
console.log("doc clientWidth:", await pg.evaluate(() => document.documentElement.clientWidth));
console.log("doc scrollWidth:", await pg.evaluate(() => document.documentElement.scrollWidth));

console.log("\n=== Mobile nav inspection ===");
await pg.click(".nav-toggle");
await pg.waitForTimeout(400);
const navInfo = await pg.evaluate(() => {
  const nav = document.querySelector(".site-nav");
  const list = nav.querySelector(".nav-list");
  const items = Array.from(list.children).map((li) => {
    const a = li.querySelector(".nav-link");
    return {
      text: a ? a.textContent.trim().slice(0, 40) : "?",
      display: getComputedStyle(li).display,
      height: li.getBoundingClientRect().height,
    };
  });
  return {
    navDisplay: getComputedStyle(nav).display,
    navHeight: nav.getBoundingClientRect().height,
    navWidth: nav.getBoundingClientRect().width,
    navTop: nav.getBoundingClientRect().top,
    listDisplay: getComputedStyle(list).display,
    listHeight: list.getBoundingClientRect().height,
    listFlexDir: getComputedStyle(list).flexDirection,
    items,
  };
});
console.log(JSON.stringify(navInfo, null, 2));

await browser.close();
