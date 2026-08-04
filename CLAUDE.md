# CLAUDE.md

Guidance for Claude Code (and any other AI coding agent) working in this
repository.

## What this is

Static marketing site for Tea Knez Coaching (`teaknez.com`). Slovenian-language
coaching business. Tea is an ICF ACC and EMCC EIA accredited coach who works
mainly with **women** (identity after motherhood, returning from parental
leave, career transitions) and with **organisations** (coaching for employees,
workshops for leaders and HR).

Pure static HTML/CSS/JS. No framework, no bundler, no build pipeline beyond a
single Python file.

## Site structure

Top-level nav: **Domov · Za posameznice · Za podjetja · Blog · O meni** plus a
"Rezerviraj uvodno srečanje" CTA.

| Page | File |
|---|---|
| Home | `index.html` |
| Coaching for individuals | `za-posameznice.html` |
| Coaching for companies | `za-podjetja.html` |
| Reintegration deep-dive (linked from Za podjetja, not in nav) | `podpora-vracanju.html` |
| About | `o-meni.html` |
| Contact | `kontakt.html` |
| Blog index + 9 posts | `blog/index.html`, `blog/<slug>/index.html` |
| Legal | `politika-zasebnosti.html`, `piskotki.html` |

The old `/storitve` hub and its three sub-pages were retired; don't reintroduce
them.

## Build

```bash
python3 build.py
```

Writes every `*.html`, plus `sitemap.xml`, `robots.txt` and `site.webmanifest`
into the project root. **Never hand-edit generated HTML** — edit `build.py` and
rebuild. Generated HTML *is* committed (GitHub Pages serves from the repo root).

`build.py` layout:

- `head()` — all `<meta>`, Open Graph, Twitter Card, JSON-LD, GA4 snippet
- `header()` / `footer()` — shared chrome; `footer()` also carries the cookie banner
- `contact_modal()` — the modal contact form used on landing pages
- `testimonials_section()` — featured long stories + short quote cards
- `POSTS` + `render_blog_post()` — the blog system
- `page_*()` builders, one per page, all registered in `if __name__ == "__main__"`

## Working rules

### Copy is the source of truth
Slovenian copy comes from Tea, usually as an email (`.eml`) or Google Doc
(`.docx`). **Never paraphrase or "improve" her wording.** Transcribe it
verbatim. The one standing exception: **no em dashes (—)** anywhere — she asked
for these to be removed site-wide; use `-` instead. En dashes (–) are fine.

### Extracting Tea's source files
Both formats hide things that are easy to miss:

```bash
# .eml — list every MIME part first, then extract text AND images
python3 -c "
import email; from email import policy
m = email.message_from_binary_file(open('file.eml','rb'), policy=policy.default)
[print(p.get_content_type(), p.get_filename()) for p in m.walk()]"

# .docx — text lives in word/document.xml, images in word/media/
python3 -c "
import zipfile; z = zipfile.ZipFile('file.docx')
print([n for n in z.namelist() if 'media' in n])"
```

**Always check for embedded images.** A `.docx` that is megabytes large is not
text — it has a picture in it. (This was learned the hard way: a featured blog
image was missed because only the text was extracted.)

### Images
Everything ships as WebP. Convert and resize on the way in:

```bash
cwebp -q 80 -resize 1280 0 source.png -o assets/images/name.webp   # landscape
cwebp -q 80 -resize 0 1280 source.png -o assets/images/name.webp   # portrait
cwebp -q 92 -alpha_q 100 -resize 720 0 logo.png -o assets/images/logo.webp  # logo, keep alpha
```

Rules of thumb: **max 1280 px on the long edge**, aim under ~100 KB, keep the
whole `assets/images/` folder around 1 MB. Give every image a real `alt` that
describes what is actually shown.

## Verification — do this for every visual change

Nothing ships without being looked at on **desktop (1440×900)** and **mobile
(390×844)**. The loop:

```bash
python3 build.py
lsof -ti:8765 | xargs kill -9 2>/dev/null     # always free the port first
python3 -m http.server 8765 >/dev/null 2>&1 &
sleep 1

node .pw/shot.mjs /o-meni.html omeni                      # full page
node .pw/shot.mjs /o-meni.html badges .credentials-row    # one element
node .pw/shot.mjs / testi .testimonial-featured "--open=.testimonial-more > summary"
```

Then **read the PNGs back** (`.pw/<name>-d.png`, `.pw/<name>-m.png`) and iterate
until spacing, alignment, type sizes and crops are right. Kill the server when
done.

`.pw/shot.mjs` handles the traps automatically. If you write a one-off script,
it must handle them too:

- **Playwright lives in `.pw/node_modules`** — scripts must be *inside* `.pw/`
  or the import fails. Run them from the project root.
- **Remove the cookie banner before capturing** — it is `position: fixed` and
  will cover whatever you are trying to see:
  `await pg.evaluate(() => document.getElementById("cookie-banner")?.remove())`
- **Very tall full-page shots get rejected when read back.** Downscale first:
  `sips -Z 1600 shot.png --out shot.png`
- **Element screenshots can capture the wrong region on mobile** when the sticky
  header overlaps. If a capture looks wrong, scroll the element into view and
  take a viewport screenshot instead.

`.pw/` is gitignored; scratch scripts and screenshots there are local only.

## Design system

`assets/css/main.css` is the only stylesheet. Tokens live at the top: cream /
clay / sage / earth palette, Cormorant Garamond serif + Inter sans.

Recurring patterns — reuse these rather than inventing new ones:

- Sage **top tab** (`::before`, ~40×3 px) on cards and bands
- **Italic serif** for accents, eyebrows-in-serif, pull quotes and emphasis
  inside headings (`<em>` inside `<h1>`/`<h2>` renders sage-darker italic)
- Small-caps **`.eyebrow`** above headings
- Cream cards with `--line` border and soft shadow
- Sage-gradient CTA bands (`.post-cta`, `.closing-cta`)

Body copy is justified with hyphens (`lang="sl"`). Headlines, eyebrows,
buttons, centered CTA bands and pull quotes stay unjustified — see the justify
block near the top of `main.css`.

Mobile nav uses an explicit hamburger at the 960 px breakpoint. `.site-header`
deliberately drops `backdrop-filter` on mobile so the nav's `position: fixed`
isn't trapped in a containing block. When touching desktop nav layout, **always
re-check mobile** — a desktop flex fix silently broke the mobile drawer once.

## Blog

Add a post by (1) appending an entry to `POSTS`, (2) writing a `page_blog_*()`
builder that calls `render_blog_post()`, (3) registering it in `__main__`.

`POSTS` entry fields: `slug`, `title`, `summary`, `image`, and optionally
`image_alt` and `date` (ISO `YYYY-MM-DD`).

- **Newest post goes first** in `POSTS` — that's the order the blog index shows.
- Prev/next links are derived from position in `POSTS` automatically. Don't
  hardcode neighbours.
- `date` is **optional and must be real**. Only the newest post has one; the
  eight older posts have no known publish date, so they show no byline and emit
  no `datePublished`. **Never invent a date** — a wrong date is worse than none.
  When a date is present you get a visible byline, `datePublished`/`dateModified`
  in JSON-LD, and `article:published_time`.

`render_blog_post()` options: `description` (meta description, separate from the
visible `lead`), `seo_title`, `cta={text,label,href}`, `author_block=True`.

## SEO

`head()` already emits canonical, robots, Open Graph, Twitter Card and JSON-LD
(`ProfessionalService` + `WebSite`, plus per-page `Person`, `BlogPosting`,
`BreadcrumbList`, `Service`, `ContactPage`). Pass `extra_jsonld=` for page-
specific nodes.

Two things that are easy to get wrong:

- **Canonicals use the apex domain and match the sitemap exactly** —
  `https://teaknez.com/o-meni.html` (with `.html`), blog posts with a trailing
  slash. `www.` 301-redirects to apex, so never canonicalise to `www`.
- Both `/o-meni` and `/o-meni.html` return 200 on Pages, so the canonical is
  what prevents duplicate-content ambiguity.

When Tea supplies an SEO/GEO brief, work through its pre-publish checklist and
verify programmatically (exactly one `<h1>`, meta description present, canonical
matches, date visible, author stated, image alt set, JSON-LD parses, URL in
sitemap).

## Analytics and consent

GA4 (`G-SZ4TH63Z3D`) with **Google Consent Mode v2**. Analytics defaults to
*denied*; `analytics_storage` is only granted when the visitor accepts. The
choice persists in `localStorage` under `tk-consent` and is restored early in
`<head>`. The banner is bottom-right on desktop, full-width on mobile, and can
be reopened from the footer's "Nastavitve piškotkov" link.

Don't add further tracking without Tea's explicit approval.

## Contact form

Posts to web3forms with a hidden `access_key`, protected by hCaptcha
(`data-sitekey` is web3forms' shared key — no separate hCaptcha account needed).
Honeypot field `botcheck` is hidden inline. `assets/js/main.js` intercepts the
submit, blocks until the captcha is solved, and shows inline success/error.

hCaptcha reports "failed to initialize" in headless Playwright — that's its
anti-bot detection, not a bug. It works in real browsers.

## Deploy

Push to `main` → GitHub Pages builds from the repo root. Custom domain via
`CNAME`. A deploy normally completes in under a minute.

If a Pages build hangs (stuck `queued`/`building` for a long time, `gh run
cancel` refuses because it thinks the run is complete), kick it with:

```bash
gh api -X POST repos/zenkkor/teaknez/pages/builds
gh api repos/zenkkor/teaknez/pages/builds/latest   # poll until status: built
```

Check <https://www.githubstatus.com> first to rule out a real incident.

## Commits

Descriptive multi-line messages: what changed, and *why* when it isn't obvious.
Note anything intentionally left out or awaiting input from Tea. Commit and push
only when asked.

## What NOT to do

- Don't introduce a framework or build pipeline (React, Vite, Astro, …)
- Don't hand-edit generated HTML
- Don't rewrite Tea's Slovenian copy
- Don't use em dashes
- Don't invent dates, credentials, testimonials or client names
- Don't change the visual design without an explicit ask — the warm cream/clay
  aesthetic is deliberate
- Don't add tracking or analytics without explicit approval
- Don't commit unoptimised images
- Don't ship a visual change you haven't looked at on both desktop and mobile
