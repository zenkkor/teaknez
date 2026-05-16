import { chromium } from "playwright";

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const pg = await ctx.newPage();
await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });
await pg.click(".nav-toggle");
await pg.waitForTimeout(400);

const info = await pg.evaluate(() => {
  const nav = document.querySelector(".site-nav");
  const cs = getComputedStyle(nav);
  const list = nav.querySelector(".nav-list");
  return {
    position: cs.position,
    top: cs.top,
    right: cs.right,
    bottom: cs.bottom,
    left: cs.left,
    width: cs.width,
    height: cs.height,
    transform: cs.transform,
    display: cs.display,
    flexDirection: cs.flexDirection,
    overflow: cs.overflow,
    rect: nav.getBoundingClientRect(),
    children: Array.from(nav.children).map((c) => ({
      tag: c.tagName,
      cls: c.className,
      rect: c.getBoundingClientRect(),
    })),
    listChildrenCount: list ? list.children.length : 0,
  };
});
console.log(JSON.stringify(info, null, 2));

await browser.close();
