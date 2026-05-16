import { chromium } from "playwright";

const BASE = "http://localhost:8765";
const browser = await chromium.launch();

// 1. Contact form has web3forms action + hidden access_key
console.log("=== Contact form (web3forms) ===");
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const pg = await ctx.newPage();
  const errors = [];
  pg.on("pageerror", (e) => errors.push(String(e)));
  pg.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await pg.goto(BASE + "/kontakt.html", { waitUntil: "networkidle" });
  const info = await pg.evaluate(() => {
    const f = document.querySelector("form.contact-form");
    if (!f) return { found: false };
    const accessKey = f.querySelector("input[name='access_key']");
    const botcheck = f.querySelector("input[name='botcheck']");
    const subject = f.querySelector("input[name='subject']");
    const status = f.querySelector(".form-status");
    return {
      found: true,
      action: f.action,
      method: f.method,
      accessKey: accessKey ? accessKey.value : null,
      botcheckHidden: botcheck ? getComputedStyle(botcheck).display === "none" : false,
      subject: subject ? subject.value : null,
      hasStatus: !!status,
    };
  });
  console.log(JSON.stringify(info, null, 2));
  console.log("console errors:", errors.length, errors.slice(0, 3));
  await ctx.close();
}

// 2. Justified body copy on blog post + legal + service detail
console.log("\n=== Justified text spot checks ===");
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const pg = await ctx.newPage();
  const checks = [
    { url: "/blog/vracanje-s-porodniskega-dopusta.html", sel: ".post-body p" },
    { url: "/politika-zasebnosti.html", sel: ".legal p" },
    { url: "/storitve/osebni-coaching.html", sel: ".service-body p" },
    { url: "/", sel: ".hero-lead" },
    { url: "/o-meni.html", sel: ".about-intro p" },
  ];
  for (const c of checks) {
    await pg.goto(BASE + c.url, { waitUntil: "networkidle" });
    const align = await pg.evaluate((sel) => {
      const el = document.querySelector(sel);
      if (!el) return "MISSING";
      const cs = getComputedStyle(el);
      return cs.textAlign + " hyphens=" + cs.hyphens;
    }, c.sel);
    console.log(`  ${c.url} ${c.sel} → ${align}`);
  }
  await ctx.close();
}

// 3. Form submit interaction — verify JS handler triggers (botcheck still blocks; we just check loading state)
console.log("\n=== Form JS handler (mock submit) ===");
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const pg = await ctx.newPage();
  await pg.goto(BASE + "/kontakt.html", { waitUntil: "networkidle" });
  // Intercept the web3forms call so we don't actually send
  await pg.route("https://api.web3forms.com/submit", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true, message: "OK" }) }),
  );
  await pg.fill("#name", "Test");
  await pg.fill("#email", "test@example.com");
  await pg.fill("#message", "Hello — preverjam obrazec.");
  await pg.check("input[name='consent']");
  await pg.click("button[type='submit']");
  await pg.waitForTimeout(500);
  const statusInfo = await pg.evaluate(() => {
    const s = document.querySelector(".form-status");
    return {
      text: s ? s.textContent.trim() : null,
      classes: s ? s.className : null,
      nameAfter: document.querySelector("#name").value,
    };
  });
  console.log(JSON.stringify(statusInfo, null, 2));
  await ctx.close();
}

// 4. Sanity overflow check on all viewports for contact page
console.log("\n=== Contact page overflow ===");
{
  const viewports = [
    { name: "390", w: 390, h: 844 },
    { name: "820", w: 820, h: 1180 },
    { name: "1440", w: 1440, h: 900 },
  ];
  for (const v of viewports) {
    const ctx = await browser.newContext({ viewport: { width: v.w, height: v.h } });
    const pg = await ctx.newPage();
    await pg.goto(BASE + "/kontakt.html", { waitUntil: "networkidle" });
    const overflow = await pg.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    console.log(`  ${v.name}px overflow:`, overflow);
    await ctx.close();
  }
}

await browser.close();
console.log("\nDone.");
