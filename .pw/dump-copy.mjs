// Dump structured text content from a site for copy-comparison.
// Usage: node dump-copy.mjs <baseUrl> <outDir> <pageMapJson>
import { chromium } from "playwright";
import fs from "fs";
import path from "path";

const [, , BASE, OUT, MAPFILE] = process.argv;
if (!BASE || !OUT || !MAPFILE) {
  console.error("usage: node dump-copy.mjs <baseUrl> <outDir> <pageMapJson>");
  process.exit(1);
}
fs.mkdirSync(OUT, { recursive: true });
const pages = JSON.parse(fs.readFileSync(MAPFILE, "utf-8"));

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
const pg = await ctx.newPage();

for (const [key, urlPath] of Object.entries(pages)) {
  const url = BASE.replace(/\/$/, "") + urlPath;
  console.log("→", key, url);
  try {
    await pg.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    await pg.waitForTimeout(800);
  } catch (e) {
    console.warn("  failed:", e.message);
    continue;
  }
  const data = await pg.evaluate(() => {
    function clean(s) {
      return (s || "")
        .replace(/ /g, " ")
        .replace(/[ \t]+/g, " ")
        .replace(/\n[ \t]+/g, "\n")
        .replace(/[ \t]+\n/g, "\n")
        .replace(/\n{3,}/g, "\n\n")
        .trim();
    }
    function visible(el) {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return cs.display !== "none" && cs.visibility !== "hidden" && cs.opacity !== "0" && r.width > 0 && r.height > 0;
    }
    const out = [];
    // Walk in DOM order, capture H1..H4, P, LI, BLOCKQUOTE
    const nodes = document.body.querySelectorAll("h1, h2, h3, h4, p, li, blockquote, figcaption, button, a.btn, button.btn");
    for (const n of nodes) {
      // Skip nav and footer noise but keep CTAs
      const t = clean(n.textContent);
      if (!t || t.length < 2) continue;
      if (!visible(n)) continue;
      out.push({ tag: n.tagName.toLowerCase(), text: t });
    }
    return {
      title: document.title,
      meta_description: (document.querySelector("meta[name='description']") || {}).content || "",
      h1: clean(document.querySelector("h1") ? document.querySelector("h1").textContent : ""),
      blocks: out,
    };
  });
  const file = path.join(OUT, key + ".json");
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

await browser.close();
console.log("Done.");
