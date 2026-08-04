/**
 * Reusable screenshot helper for visual verification.
 *
 *   node .pw/shot.mjs <path> <name> [selector] [--open=<sel>]
 *
 *   node .pw/shot.mjs / home                     -> full page, desktop + mobile
 *   node .pw/shot.mjs /o-meni.html om .credentials-row   -> just that element
 *   node .pw/shot.mjs / testi .testimonial-featured --open=.testimonial-more>summary
 *
 * Writes .pw/<name>-d.png (1440x900) and .pw/<name>-m.png (390x844).
 * Full-page shots are downscaled so they stay viewable.
 * The cookie banner is removed automatically so it never covers content.
 *
 * NOTE: this file must live in .pw/ - playwright is installed in
 * .pw/node_modules and Node resolves it relative to the script.
 */
import { chromium } from "playwright";
import { execSync } from "node:child_process";

const [path = "/", name = "shot", selector] = process.argv.slice(2).filter(a => !a.startsWith("--"));
const openSel = (process.argv.find(a => a.startsWith("--open=")) || "").replace("--open=", "");
const BASE = "http://localhost:8765";

const browser = await chromium.launch();
for (const [vp, width, height] of [["d", 1440, 900], ["m", 390, 844]]) {
  const ctx = await browser.newContext({ viewport: { width, height } });
  const pg = await ctx.newPage();
  await pg.goto(BASE + path, { waitUntil: "networkidle" });
  // The consent banner is fixed-position and would cover whatever we capture.
  await pg.evaluate(() => document.getElementById("cookie-banner")?.remove());
  if (openSel) {
    await pg.click(openSel).catch(() => {});
    await pg.waitForTimeout(350);
  }

  const out = `.pw/${name}-${vp}.png`;
  if (selector) {
    const el = await pg.$(selector);
    if (!el) { console.error(`  ${vp}: selector not found: ${selector}`); await ctx.close(); continue; }
    await el.scrollIntoViewIfNeeded();
    await pg.waitForTimeout(250);
    await el.screenshot({ path: out });
  } else {
    await pg.screenshot({ path: out, fullPage: true });
    // Very tall captures are unwieldy to review - downscale them.
    try {
      const h = Number(execSync(`sips -g pixelHeight ${out} | awk '/pixelHeight/{print $2}'`).toString().trim());
      if (h > 2200) execSync(`sips -Z 1600 ${out} --out ${out} >/dev/null 2>&1`);
    } catch {}
  }
  console.log(`  wrote ${out}`);
  await ctx.close();
}
await browser.close();
