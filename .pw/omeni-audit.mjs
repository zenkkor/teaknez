import { chromium } from "playwright";

const browser = await chromium.launch();
for (const [vp, w, h] of [["d", 1440, 900], ["m", 390, 844]]) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const pg = await ctx.newPage();
  await pg.goto("http://localhost:8765/o-meni.html", { waitUntil: "networkidle" });
  console.log(`\n=== ${vp.toUpperCase()} (${w}×${h}) ===`);
  const info = await pg.evaluate(() => {
    const sections = Array.from(document.querySelectorAll("main > section"));
    return sections.map((sec) => {
      const cs = getComputedStyle(sec);
      const r = sec.getBoundingClientRect();
      const firstHeading = sec.querySelector("h1, h2, h3");
      return {
        cls: (typeof sec.className === "string" ? sec.className : "").slice(0, 60),
        ptop: cs.paddingTop,
        pbot: cs.paddingBottom,
        height: Math.round(r.height),
        heading: firstHeading ? firstHeading.textContent.slice(0, 40) : "",
      };
    });
  });
  info.forEach((s) =>
    console.log(`  ${s.cls}\n    p:${s.ptop}/${s.pbot} h:${s.height}px — "${s.heading}"`)
  );
  await pg.screenshot({ path: `.pw/omeni-${vp}-full.png`, fullPage: true });
  console.log(`  → screenshot saved`);
  await ctx.close();
}
await browser.close();
