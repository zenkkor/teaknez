import { chromium } from "playwright";
import fs from "fs";

const BASE = "http://localhost:8765";
const OUT = "/tmp/pw-shots";
fs.mkdirSync(OUT, { recursive: true });

const viewports = [
  { name: "mobile-iphone", width: 390, height: 844 },
  { name: "mobile-small", width: 360, height: 740 },
  { name: "tablet", width: 820, height: 1180 },
  { name: "tablet-large", width: 1024, height: 1366 },
  { name: "desktop", width: 1440, height: 900 },
];

const pages = [
  { name: "home", url: "/" },
  { name: "about", url: "/o-meni.html" },
  { name: "services-hub", url: "/storitve.html" },
  { name: "osebni", url: "/storitve/osebni-coaching.html" },
  { name: "blog-index", url: "/blog.html" },
  { name: "blog-post", url: "/blog/vracanje-s-porodniskega-dopusta.html" },
  { name: "contact", url: "/kontakt.html" },
];

const browser = await chromium.launch();

console.log("=== Full-page screenshots across viewports ===");
for (const vp of viewports) {
  const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  const pg = await ctx.newPage();
  for (const p of pages) {
    await pg.goto(BASE + p.url, { waitUntil: "networkidle" });
    const path = `${OUT}/${vp.name}__${p.name}.png`;
    await pg.screenshot({ path, fullPage: true });
    console.log("  shot", path);
  }
  await ctx.close();
}

console.log("\n=== Interaction: desktop dropdown hover ===");
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const pg = await ctx.newPage();
  await pg.goto(BASE + "/", { waitUntil: "networkidle" });
  await pg.hover(".nav-item-dropdown .nav-link");
  await pg.waitForTimeout(400);
  const items = await pg.$$eval(".dropdown-link strong", (els) => els.map((e) => e.textContent.trim()));
  console.log("  dropdown items:", items);
  await pg.screenshot({ path: `${OUT}/desktop__dropdown-open.png`, clip: { x: 0, y: 0, width: 1440, height: 500 } });
  console.log("  shot", `${OUT}/desktop__dropdown-open.png`);
  await ctx.close();
}

console.log("\n=== Interaction: mobile nav open + submenu expand ===");
{
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const pg = await ctx.newPage();
  await pg.goto(BASE + "/", { waitUntil: "networkidle" });
  await pg.click(".nav-toggle");
  await pg.waitForTimeout(400);
  await pg.screenshot({ path: `${OUT}/mobile__nav-open.png` });
  console.log("  shot", `${OUT}/mobile__nav-open.png`);
  // Expand Storitve
  await pg.click(".nav-item-dropdown .nav-link");
  await pg.waitForTimeout(300);
  await pg.screenshot({ path: `${OUT}/mobile__nav-submenu.png` });
  console.log("  shot", `${OUT}/mobile__nav-submenu.png`);
  const expanded = await pg.getAttribute(".nav-item-dropdown", "aria-expanded");
  console.log("  submenu expanded:", expanded);
  // Close via toggle
  await pg.click(".nav-toggle");
  await pg.waitForTimeout(300);
  const closed = !(await pg.evaluate(() => document.querySelector(".site-nav").classList.contains("is-open")));
  console.log("  mobile nav closed:", closed);
  await ctx.close();
}

console.log("\n=== Console errors check ===");
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const pg = await ctx.newPage();
  const errors = [];
  pg.on("pageerror", (e) => errors.push(String(e)));
  pg.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  for (const p of pages) {
    await pg.goto(BASE + p.url, { waitUntil: "networkidle" });
  }
  console.log("  total errors:", errors.length);
  errors.slice(0, 5).forEach((e) => console.log("  -", e));
  await ctx.close();
}

console.log("\n=== Layout sanity: no horizontal overflow ===");
{
  for (const vp of viewports) {
    const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    const pg = await ctx.newPage();
    let overflow = 0;
    for (const p of pages) {
      await pg.goto(BASE + p.url, { waitUntil: "networkidle" });
      const o = await pg.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
      if (o) overflow++;
    }
    console.log(`  ${vp.name} (${vp.width}px) — pages with horizontal overflow:`, overflow);
    await ctx.close();
  }
}

await browser.close();
console.log("\nDone.");
