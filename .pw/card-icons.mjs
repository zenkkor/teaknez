import { chromium } from "playwright";

const targets = [
  ["home", "/", ".cards"],
  ["osebni", "/storitve/osebni-coaching.html", ".cards"],
];

const browser = await chromium.launch();
for (const [vp, w, h] of [["d", 1440, 900], ["m", 390, 844]]) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const pg = await ctx.newPage();
  for (const [name, url, sel] of targets) {
    await pg.goto("http://localhost:8765" + url, { waitUntil: "networkidle" });
    const el = await pg.$(sel);
    if (!el) {
      console.log(`${name} ${vp}: ${sel} not found`);
      continue;
    }
    await el.scrollIntoViewIfNeeded();
    await pg.waitForTimeout(150);
    const path = `.pw/card-icons-${name}-${vp}.png`;
    await el.screenshot({ path });
    console.log(`wrote ${path}`);
    // measure
    const info = await pg.evaluate((s) => {
      const root = document.querySelector(s);
      const icons = Array.from(root.querySelectorAll(".card-icon"));
      return icons.map((i) => {
        const cs = getComputedStyle(i);
        return {
          text: i.textContent.trim(),
          fontSize: cs.fontSize,
          color: cs.color,
          fontStyle: cs.fontStyle,
          marginBottom: cs.marginBottom,
        };
      });
    }, sel);
    console.log(`${name} ${vp}:`, info);
  }
  await ctx.close();
}
await browser.close();
