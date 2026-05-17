import { chromium } from "playwright";

const pages = [
  ["home", "/"],
  ["o-meni", "/o-meni.html"],
  ["storitve", "/storitve.html"],
  ["osebni", "/storitve/osebni-coaching.html"],
  ["blog-index", "/blog/"],
  ["blog-post", "/blog/samozavest-ni-nekaj-kar-imas/"],
  ["kontakt", "/kontakt.html"],
];

const browser = await chromium.launch();
for (const [vp, w, h] of [["d", 1440, 900], ["m", 390, 844]]) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const pg = await ctx.newPage();
  console.log(`\n=== ${vp.toUpperCase()} (${w}×${h}) ===`);
  for (const [name, url] of pages) {
    await pg.goto("http://localhost:8765" + url, { waitUntil: "networkidle" });
    const info = await pg.evaluate(() => {
      const main = document.querySelector("main");
      const sections = main ? Array.from(main.children) : [];
      const data = sections.map((sec) => {
        const cs = getComputedStyle(sec);
        return {
          tag: sec.tagName.toLowerCase(),
          cls: (typeof sec.className === "string" ? sec.className : "").slice(0, 50),
          ptop: cs.paddingTop,
          pbot: cs.paddingBottom,
          mtop: cs.marginTop,
          mbot: cs.marginBottom,
          height: Math.round(sec.getBoundingClientRect().height),
        };
      });
      // also primary CTA button surrounding
      const btn = main && main.querySelector(".cta-end .btn-primary, .cta-end button.btn-primary");
      const btnParent = btn ? btn.closest(".cta-end") : null;
      const btnInfo = btnParent
        ? {
            cta_ptop: getComputedStyle(btnParent).paddingTop,
            cta_pbot: getComputedStyle(btnParent).paddingBottom,
          }
        : null;
      // hero btn
      const heroBtn = main && main.querySelector(".hero .btn-primary");
      let heroBtnInfo = null;
      if (heroBtn) {
        const cs = getComputedStyle(heroBtn);
        const wrap = main.querySelector(".hero");
        const wrapCs = wrap ? getComputedStyle(wrap) : null;
        heroBtnInfo = {
          margin: `${cs.marginTop}/${cs.marginBottom}`,
          hero_padding: wrapCs ? `${wrapCs.paddingTop}/${wrapCs.paddingBottom}` : null,
        };
      }
      return { sections: data, btnInfo, heroBtnInfo };
    });
    console.log(`\n${name}:`);
    info.sections.forEach((s) =>
      console.log(`  <${s.tag} class="${s.cls}"> p:${s.ptop}/${s.pbot} m:${s.mtop}/${s.mbot} h:${s.height}`)
    );
    if (info.btnInfo) console.log("  cta-end:", info.btnInfo);
    if (info.heroBtnInfo) console.log("  hero btn:", info.heroBtnInfo);
  }
  await ctx.close();
}
await browser.close();
