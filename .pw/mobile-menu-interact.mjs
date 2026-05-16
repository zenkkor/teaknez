import { chromium } from "playwright";
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const pg = await ctx.newPage();

await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });

// Open menu
await pg.click(".nav-toggle");
await pg.waitForTimeout(300);
console.log("opened, URL:", pg.url());

// Try clicking "Blog" link
const blogLink = await pg.$("a[href='blog.html'].nav-link");
console.log("blog link found:", !!blogLink);
if (blogLink) {
  await blogLink.click();
  await pg.waitForLoadState("domcontentloaded");
  console.log("after blog click, URL:", pg.url());
}

// Go back to home
await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });
await pg.click(".nav-toggle");
await pg.waitForTimeout(300);

// Test clicking "Domov" (active) — what does it do?
const navOpen1 = await pg.evaluate(() => document.querySelector(".site-nav").classList.contains("is-open"));
console.log("\nbefore Domov click, nav open:", navOpen1);
await pg.click(".nav-link[href='index.html']");
await pg.waitForTimeout(500);
const navOpen2 = await pg.evaluate(() => document.querySelector(".site-nav").classList.contains("is-open"));
console.log("after Domov click, nav open:", navOpen2, "URL:", pg.url());

// Test dropdown — clicking "Storitve" then a sub-item
await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });
await pg.click(".nav-toggle");
await pg.waitForTimeout(300);
await pg.click(".nav-item-dropdown > .nav-link");
await pg.waitForTimeout(300);
console.log("\ndropdown expanded:", await pg.getAttribute(".nav-item-dropdown", "aria-expanded"));

// Now click "Osebni coaching" sublink
const sublink = await pg.$(".dropdown-link[href='storitve/osebni-coaching.html']");
console.log("sublink found:", !!sublink);
if (sublink) {
  const isClickable = await sublink.evaluate((el) => {
    const r = el.getBoundingClientRect();
    return { visible: r.width > 0 && r.height > 0, rect: r };
  });
  console.log("sublink clickable:", JSON.stringify(isClickable));
  try {
    await sublink.click({ timeout: 3000 });
    await pg.waitForLoadState("domcontentloaded");
    console.log("after sublink click, URL:", pg.url());
  } catch (e) {
    console.log("sublink click FAILED:", e.message);
  }
}

// Test click outside (on backdrop)
await pg.goto("http://localhost:8765/", { waitUntil: "networkidle" });
await pg.click(".nav-toggle");
await pg.waitForTimeout(300);
// Try clicking somewhere outside the nav (e.g. left side of screen where backdrop should be)
await pg.mouse.click(50, 400);
await pg.waitForTimeout(400);
const navOpenAfterOutside = await pg.evaluate(() => document.querySelector(".site-nav").classList.contains("is-open"));
console.log("\nafter click-outside, nav open:", navOpenAfterOutside);

// ESC close
await pg.click(".nav-toggle");
await pg.waitForTimeout(300);
await pg.keyboard.press("Escape");
await pg.waitForTimeout(300);
const navOpenAfterEsc = await pg.evaluate(() => document.querySelector(".site-nav").classList.contains("is-open"));
console.log("after ESC, nav open:", navOpenAfterEsc);

await browser.close();
