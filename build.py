#!/usr/bin/env python3
"""Build static teaknez.com from extracted content."""
import os, re, html as ihtml
from datetime import datetime
from pathlib import Path

CURRENT_YEAR = datetime.now().year

SITE = Path(__file__).parent

# ---------- SEO constants ----------
SITE_URL = "https://teaknez.com"
SITE_NAME = "Tea Knez Coaching"

# ---------- Analytics ----------
GA_MEASUREMENT_ID = "G-SZ4TH63Z3D"
GA_SNIPPET = f"""<!-- Google tag (gtag.js) with Consent Mode v2 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  // Default to denied until the visitor decides (GDPR / EU).
  gtag('consent', 'default', {{
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'analytics_storage': 'denied',
    'wait_for_update': 500
  }});
  // Restore a prior choice as early as possible.
  try {{
    if (localStorage.getItem('tk-consent') === 'granted') {{
      gtag('consent', 'update', {{ 'analytics_storage': 'granted' }});
    }}
  }} catch (e) {{}}
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>
"""

def _org_jsonld():
    """Shared Organization/ProfessionalService node, reused as publisher."""
    return {
        "@type": "ProfessionalService",
        "@id": f"{SITE_URL}/#organization",
        "name": SITE_NAME,
        "legalName": "Integra, Tea Knez s.p.",
        "url": f"{SITE_URL}/",
        "logo": f"{SITE_URL}/assets/images/favicon.svg",
        "image": f"{SITE_URL}/assets/images/about-tea.webp",
        "email": "tea@teaknez.com",
        "description": "Coaching za ženske in organizacije. Podpora pri pomembnih življenjskih in poklicnih prehodih, s specializacijo za vračanje po porodniškem dopustu.",
        "areaServed": {"@type": "Country", "name": "Slovenija"},
        "availableLanguage": "sl",
        "founder": {"@id": f"{SITE_URL}/#tea-knez"},
        "knowsAbout": [
            "coaching", "reintegracijski coaching", "vračanje po porodniškem dopustu",
            "karierni coaching", "organizacijski coaching", "razvoj vodij",
        ],
    }

def _website_jsonld():
    return {
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": f"{SITE_URL}/",
        "name": SITE_NAME,
        "inLanguage": "sl",
        "publisher": {"@id": f"{SITE_URL}/#organization"},
    }

def _person_jsonld():
    return {
        "@type": "Person",
        "@id": f"{SITE_URL}/#tea-knez",
        "name": "Tea Knez",
        "jobTitle": "Coachinja",
        "url": f"{SITE_URL}/o-meni.html",
        "image": f"{SITE_URL}/assets/images/about-tea.webp",
        "worksFor": {"@id": f"{SITE_URL}/#organization"},
        "knowsLanguage": "sl",
        "memberOf": [
            {"@type": "Organization", "name": "European Mentoring & Coaching Council"},
            {"@type": "Organization", "name": "International Coaching Federation"},
        ],
        "knowsAbout": [
            "reintegracijski coaching", "vračanje po porodniškem dopustu",
            "karierni coaching", "organizacijski coaching", "razvoj vodij in HR",
        ],
    }

def _breadcrumb_jsonld(trail):
    """trail: list of (name, url) tuples from Domov to current page."""
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": url}
            for i, (name, url) in enumerate(trail)
        ],
    }

def _blogposting_jsonld(title, description, url, image, date=None, modified=None):
    node = {
        "@type": "BlogPosting",
        "@id": url + "#article",
        "headline": title,
        "description": description,
        "url": url,
        "image": f"{SITE_URL}/assets/images/{image}",
        "inLanguage": "sl",
        "author": {"@id": f"{SITE_URL}/#tea-knez"},
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    # Only emit dates we actually know - never fabricate them.
    if date:
        node["datePublished"] = date
        node["dateModified"] = modified or date
    return node


# ---------- Blog helpers ----------
BLOG_AUTHOR = "Tea Knez"

_SL_MONTHS = ["januar", "februar", "marec", "april", "maj", "junij",
              "julij", "avgust", "september", "oktober", "november", "december"]

def _sl_date(iso):
    """2026-08-04 -> '4. avgust 2026'."""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d}. {_SL_MONTHS[m - 1]} {y}"

def _post_neighbors(slug):
    """Derive prev/next from position in POSTS so inserting a post can't
    desynchronise the navigation."""
    idx = next((i for i, p in enumerate(POSTS) if p["slug"] == slug), None)
    if idx is None:
        return None, None
    prev_post = POSTS[idx - 1] if idx > 0 else None
    next_post = POSTS[idx + 1] if idx < len(POSTS) - 1 else None
    return prev_post, next_post

def _jsonld_block(nodes):
    import json as _json
    graph = {"@context": "https://schema.org", "@graph": nodes}
    return '<script type="application/ld+json">' + _json.dumps(graph, ensure_ascii=False, separators=(",", ":")) + "</script>\n"


# ---------- Shared fragments ----------
def head(title, description, canonical, depth=0, og_type="website",
         og_image="about-tea.webp", og_image_alt="Tea Knez - coachinja", extra_jsonld=None,
         article_date=None):
    root = "../" * depth
    asset = root + "assets"
    og_image_url = f"{SITE_URL}/assets/images/{og_image}"

    nodes = [_org_jsonld(), _website_jsonld()]
    if extra_jsonld:
        nodes.extend(extra_jsonld if isinstance(extra_jsonld, list) else [extra_jsonld])
    jsonld = _jsonld_block(nodes)

    article_meta = ""
    if article_date:
        article_meta = (
            f'<meta property="article:published_time" content="{article_date}">\n'
            f'<meta property="article:modified_time" content="{article_date}">\n'
            f'<meta property="article:author" content="{BLOG_AUTHOR}">\n'
        )

    return f"""<!DOCTYPE html>
<html lang="sl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{GA_SNIPPET}<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="Tea Knez">
<meta name="theme-color" content="#F7F3EE">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="sl_SI">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image_url}">
<meta property="og:image:alt" content="{og_image_alt}">
{article_meta}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image_url}">
<meta name="twitter:image:alt" content="{og_image_alt}">
<link rel="icon" type="image/svg+xml" href="{asset}/images/favicon.svg">
<link rel="apple-touch-icon" href="{asset}/images/favicon.svg">
<link rel="manifest" href="{root}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset}/css/main.css">
{jsonld}</head>
<body>
"""

def header_minimal(depth=0):
    p = "../" * depth
    return f"""<a href="#main" class="skip-link">Preskoči na vsebino</a>
<header class="site-header site-header--minimal">
  <div class="container">
    <a href="{p}index.html" class="site-logo" aria-label="Tea Knez Coaching - domov">
      <span>Tea Knez<small class="tag">Coaching</small></span>
    </a>
    <a href="{p}index.html" class="nav-cta nav-cta--ghost">Na domačo stran</a>
  </div>
</header>
<main id="main">
"""


def contact_modal(depth=0, subject="Povpraševanje s teaknez.com"):
    p = "../" * depth
    return f"""<div class="modal" id="contact-modal" role="dialog" aria-labelledby="contact-modal-title" aria-modal="true" hidden>
  <div class="modal-backdrop" data-modal-close></div>
  <div class="modal-dialog" role="document">
    <button class="modal-close" type="button" aria-label="Zapri" data-modal-close>
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    <div class="modal-body">
      <span class="eyebrow">Uvodni pogovor</span>
      <h2 id="contact-modal-title">Dogovorimo se</h2>
      <p class="modal-lead">Pusti mi kontakt in javim se ti za kratek uvodni pogovor.</p>
      <form class="contact-form" action="https://api.web3forms.com/submit" method="POST" data-web3forms>
        <input type="hidden" name="access_key" value="e78b399d-a62e-494f-b90b-519f4b7f7a48">
        <input type="hidden" name="subject" value="{subject}">
        <input type="hidden" name="from_name" value="teaknez.com">
        <input type="checkbox" name="botcheck" style="display:none;" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="field">
          <label for="modal-name">Ime*</label>
          <input id="modal-name" name="name" type="text" required autocomplete="name">
        </div>
        <div class="field">
          <label for="modal-email">Email*</label>
          <input id="modal-email" name="email" type="email" required autocomplete="email">
        </div>
        <div class="field">
          <label for="modal-company">Podjetje</label>
          <input id="modal-company" name="company" type="text" autocomplete="organization">
        </div>
        <div class="field">
          <label for="modal-message">Sporočilo</label>
          <textarea id="modal-message" name="message" placeholder="Napiši na kratko, kaj te zanima…"></textarea>
        </div>
        <label class="field-check">
          <input type="checkbox" name="consent" required>
          <span>Strinjam se s <a href="{p}politika-zasebnosti.html">Pogoji.</a></span>
        </label>
        <div class="h-captcha" data-sitekey="50b2fe65-b00b-4b9e-ad62-3ba471098be2"></div>
        <button type="submit" class="btn btn-primary">Pošlji</button>
        <div class="form-status" role="status" aria-live="polite"></div>
      </form>
    </div>
  </div>
</div>
<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
"""


def header(active, depth=0):
    p = "../" * depth

    def link(label, href, key, extra=""):
        active_cls = " is-active" if active == key else ""
        return f'<a href="{href}" class="nav-link{active_cls}"{extra}>{label}</a>'

    return f"""<a href="#main" class="skip-link">Preskoči na vsebino</a>
<header class="site-header">
  <div class="container">
    <a href="{p}index.html" class="site-logo" aria-label="Tea Knez - domov">
      <span>Tea Knez<small class="tag">Professional Coach</small></span>
    </a>
    <nav class="site-nav" id="site-nav" aria-label="Glavna navigacija">
      <ul class="nav-list">
        <li>{link("Domov", p + "index.html", "home")}</li>
        <li>{link("Individualni coaching", p + "za-posameznice.html", "individuals")}</li>
        <li>{link("Za podjetja", p + "za-podjetja.html", "companies")}</li>
        <li>{link("O meni", p + "o-meni.html", "about")}</li>
        <li>{link("Blog", p + "blog/", "blog")}</li>
      </ul>
      <a href="{p}kontakt.html" class="nav-cta">Kontakt / Uvodni pogovor</a>
    </nav>
    <button class="nav-toggle" aria-label="Odpri meni" aria-controls="site-nav" aria-expanded="false"><span></span></button>
  </div>
  <div class="nav-backdrop" hidden></div>
</header>
<main id="main">
"""

def footer(depth=0):
    p = "../" * depth
    return f"""</main>
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <h3>Tea Knez</h3>
        <p class="footer-cred">ICF ACC · EMCC EIA</p>
        <p>Profesionalni coaching za posameznike in organizacije ter delavnice za podjetja.</p>
      </div>
      <div class="footer-col">
        <h4>Povezave</h4>
        <ul>
          <li><a href="{p}index.html">Domov</a></li>
          <li><a href="{p}za-posameznice.html">Individualni coaching</a></li>
          <li><a href="{p}za-podjetja.html">Za podjetja</a></li>
          <li><a href="{p}o-meni.html">O meni</a></li>
          <li><a href="{p}blog/">Blog</a></li>
          <li><a href="{p}kontakt.html">Kontakt</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Kontakt</h4>
        <ul>
          <li><a href="mailto:tea@teaknez.com">tea@teaknez.com</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-current-year>{CURRENT_YEAR}</span> Tea Knez · <a href="{p}politika-zasebnosti.html">Politika zasebnosti</a> · <a href="{p}piskotki.html">Piškotki</a> · <button type="button" class="footer-link-btn" data-cookie-settings>Nastavitve piškotkov</button></span>
    </div>
  </div>
</footer>
<div class="cookie-banner" id="cookie-banner" role="dialog" aria-label="Obvestilo o piškotkih" aria-live="polite" hidden>
  <div class="cookie-banner-inner">
    <span class="cookie-banner-eyebrow">
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5z"/><circle cx="9.5" cy="10.5" r="0.6" fill="currentColor"/><circle cx="14.5" cy="14.5" r="0.6" fill="currentColor"/><circle cx="10" cy="15.5" r="0.6" fill="currentColor"/></svg>
      Piškotki
    </span>
    <p class="cookie-banner-text">Za analizo obiska strani uporabljamo piškotke. Sam/a se odločiš, ali jih dovoliš. Več v <a href="{p}piskotki.html">politiki piškotkov</a>.</p>
    <div class="cookie-banner-actions">
      <button type="button" class="btn-cookie btn-cookie--ghost" data-consent="denied">Zavrni</button>
      <button type="button" class="btn-cookie btn-cookie--accept" data-consent="granted">Sprejmi</button>
    </div>
  </div>
</div>
<script src="{p}assets/js/main.js"></script>
</body>
</html>
"""

# Testimonials shared markup
TESTIMONIALS = [
    ("Vodenje lastnega podjetja je hitro postalo preveč razpršeno. S Teo sem začela razmišljati širše in z več jasnosti sprejemati podjetniške odločitve.",
     "Sara B."),
    ("Kot vodja ekipe sem bila pogosto ujeta med rezultate in ljudi. S coachingom sem postala mirnejša v zahtevnih situacijah in jasnejša v komunikaciji.",
     "Petra M."),
    ("V poslu sem dolgo dvomila vase, čeprav sem bila strokovno samozavestna. Coaching mi je dal strateško jasnost in pogum za pomembne odločitve.",
     "Nina R."),
    ("Navajena sem biti ves čas ‘vidna’, redko pa sem si dovolila prostor za razmislek. Naučila sem se postaviti jasnejše meje in začela ustvarjati z več notranjega miru.",
     "Maja S."),
]

# Longer client stories - shown first, as the focus of the section.
FEATURED_TESTIMONIALS = [
    {
        "name": "Živa O.",
        "paragraphs": [
            "Na začetku nisem vedela, kaj točno pričakovati, saj sem se s tovrstnim coachingom prvič zares srečala. Pred tem sem se že več let poglabljala vase in se ukvarjala s samoanalizo nerazrešenih čustev, miselnih vzorcev in samopodobe. Občutek sem imela, da sem si že odgovorila na vsa vprašanja in pogledala v vse skrivne kotičke...",
            "Na vsakem srečanju s Teo so se odpirale in odstirale različne teme, ki so bile takrat aktualne. Vsakokrat se je začelo s sproščenim pogovorom, ki se je nadaljeval s samorealizacijo, kje so še skriti občutki in zataknjena čustva, ki so me zaustavljali na moji poti, da dosežem to, kar si globoko v sebi želim.",
            "Tea me je s subtilnimi vprašanji spodbudila k razmisleku o stvareh, na katere si sama nisem nikoli zares odgovorila. Ko sem sama premlevala različne teme potiho v svojem umu, sem nezavedno obšla ali pa se nisem dovolj globoko poglobila, od kod pravzaprav izvirajo določena čustva in miselni vzorci.",
            "S Teino pomočjo sem te dele lažje ozavestila ter se z njimi soočila in jih integrirala v zdajšnjo realnost. Presenetilo me je, kako drugače je, ko na glas poveš to, kar se ti poraja v mislih, od kod to prihaja in kaj to pomeni v sedanjem trenutku. Neprecenljivo, ko imaš pred seboj sogovornika, ki ustvari prostor, da se izraziš in te pri tem neobsojajoče in sočutno podpira.",
            "Najina srečanja so okrepila mojo notranjo moč in mi dala dodaten zagon, da bolj samozavestno, odločno in brez obotavljanja nadaljujem svojo poslovno pot, misijo, ki tli v mojem srcu.",
            "Coaching s Teo bi priporočala vsakomur, ki čuti, da potrebuje spodbudo, hitrejši napredek in si želi poglobiti, razrešiti ter sprostiti globoko zakoreninjena prepričanja, ki mu/ji ne služijo več. Toplo priporočam!",
        ],
    },
    {
        "name": "Vesna T.",
        "paragraphs": [
            "S Teo sva se spoznali čisto po naključju, ravno v obdobju, ko sem to podporo najbolj potrebovala. Bila sem približno pol leta po porodniški, v času, ko sem se še privajala na novo vlogo mame, hkrati pa odpirala novo podjetje. Iskreno, precej sem se lovila. Imela sem veliko idej, želja in odgovornosti, ampak tudi ogromno dvomov, notranjih pritiskov in občutka, da skušam vse uskladiti hkrati.",
            "Tea je izjemno strokovna, empatična in predvsem zna zares poslušati. Ne posluša samo besed, ampak sliši tudi tisto, česar včasih sama ne znaš ubesediti. Ker ima tudi sama podobne življenjske izkušnje, sem imela ves čas občutek, da me res razume.",
            "Skupaj sva se dotaknili mojih omejujočih prepričanj, postavljanja ciljev, organizacije časa ter usklajevanja vlog mame in podjetnice. Z njeno pomočjo sem začela spreminjati svoj notranji “moram” v “želim” in že ta premik mi je pomagal, da sem začela na svoje odločitve gledati bolj mirno, zavestno in z manj občutka krivde.",
            "Tea mi je pomagala tudi na novo definirati, kaj zame pomeni biti uspešna. Ne samo skozi rezultate, delo in dosežke, ampak tudi skozi občutek notranjega miru, prisotnosti in zvestobe sebi. Veliko sva delali tudi na tem, kaj je res v moji moči in na kaj nimam vpliva - kar mi je pomagalo spustiti del pritiska, ki sem si ga nalagala sama.",
            "Njeno vodenje me je pripeljalo do številnih pomembnih spoznanj, ki jih še danes uporabljam pri svojem delu in v zasebnem življenju. No, vsaj poskušam...",
            "Največ pa mi pomeni občutek, ki sem ga imela po vsakem srečanju – da sem slišana, razumljena in da mi ni treba vsega nositi sama.",
            "Tea bi priporočila vsakomur, ki si želi osebne ali poslovne rasti, še posebej pa ženskam, ki se znajdejo med materinstvom in podjetniško potjo. Hvala, Tea, za tvojo podporo, usmeritve in varen prostor za rast. ❤️",
        ],
    },
    {
        "name": "Tamara K.",
        "paragraphs": [
            "Na coaching sem prišla z željo, da ponovno najdem sebe ter pridobim več notranjega miru in jasnosti. Najbolj dragocen mi je bil varen prostor, kjer sem se lahko iskreno odprla, ter podpora, ki mi je pomagala narediti konkretne korake naprej. Med procesom sem začela bolj zaupati sebi, lažje postavljati meje in sprejemati odločitve. Coaching bi priporočila vsakomur, ki čuti, da je čas za spremembo, osebno rast in življenje v večji harmoniji s seboj.",
        ],
    },
]


def _featured_testimonial(t):
    """Long client story. The opening paragraph is always visible; the rest
    expands via a native <details> so the section stays scannable. Copy is
    verbatim and never shortened."""
    paras = t["paragraphs"]
    opening = f'      <p>{paras[0]}</p>'
    rest = ""
    if len(paras) > 1:
        more = "\n".join(f"          <p>{x}</p>" for x in paras[1:])
        rest = f"""
      <details class="quote-more">
        <summary><span class="quote-more-show">Preberi celotno zgodbo</span><span class="quote-more-hide">Skrij zgodbo</span></summary>
        <div class="quote-more-body">
{more}
        </div>
      </details>"""
    return f"""    <article class="quote">
{opening}{rest}
      <cite class="quote-author">{t["name"]}</cite>
    </article>"""


def testimonials_section():
    featured = "\n".join(_featured_testimonial(t) for t in FEATURED_TESTIMONIALS)
    short = "\n".join(
        f"""    <article class="quote">
      <p>{q}</p>
      <cite class="quote-author">{name}</cite>
    </article>"""
        for q, name in TESTIMONIALS
    )
    return f"""<section class="sec sec--cream">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">IZKUŠNJE KLIENTK</span>
      <h2>Njihove besede. Njihova spoznanja.</h2>
    </div>
    <div class="quotes">
{featured}
{short}
    </div>
  </div>
</section>
"""


def cta_band(depth=0):
    p = "../" * depth
    return f"""<section class="section">
  <div class="container">
    <div class="cta-band">
      <h2>Želiš raziskati več?</h2>
      <p>Včasih že en pogovor prinese več jasnosti. Piši mi za rezervacijo prvega brezplačnega uvodnega srečanja.</p>
      <a href="{p}kontakt.html" class="btn btn-primary">Piši mi <span class="arrow">→</span></a>
    </div>
  </div>
</section>
"""

def write(path, content):
    full = SITE / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    print("wrote", path)

# ---------- INDEX ----------
def page_index():
    body = """<section class="sec sec--cream">
  <div class="container">
    <div class="hero-split">
      <div class="hero-split-copy">
        <span class="kicker">TEA KNEZ · PROFESIONALNI COACHING</span>
        <h1>Ni ene prave poti. Pomembno je, da najdeš svojo.</h1>
        <p>Coaching odpira prostor za nova vprašanja, drugačne perspektive in odločitve, ki so skladne s tvojimi cilji in vrednotami.</p>
        <p>Individualni coaching in delavnice za osebni ter profesionalni razvoj.</p>
        <div class="hero-actions">
          <a href="kontakt.html?namen=uvodni-pogovor" class="btn btn-primary">Dogovori se za uvodni pogovor</a>
        </div>
        <p class="cred-line">ICF ACC · EMCC EIA</p>
      </div>
      <div class="hero-split-media">
        <img src="assets/images/tea-blazer.webp" alt="Tea Knez, profesionalna coachinja" loading="eager" width="1025" height="1280">
      </div>
    </div>
  </div>
</section>

<section class="sec sec--beige sec--tight">
  <div class="container">
    <div class="sec-head-center">
      <h2>Kako lahko sodelujemo?</h2>
    </div>
    <div class="offer-grid">
      <a class="offer-card" href="za-posameznice.html">
        <h3>Individualni coaching</h3>
        <p>Za ženske, ki si želijo več jasnosti, zaupanja vase in prostora za svoje želje, odločitve ter spremembe.</p>
        <span class="offer-link">Razišči individualni coaching</span>
      </a>
      <a class="offer-card" href="za-podjetja.html">
        <h3>Za podjetja</h3>
        <p>Individualni coaching in delavnice za razvoj zaposlenih, boljšo komunikacijo in sodelovanje ter podporo ob pomembnih kariernih prehodih, kot sta vrnitev s starševskega dopusta ali po daljši odsotnosti.</p>
        <span class="offer-link">Razišči ponudbo za podjetja</span>
      </a>
    </div>
  </div>
</section>

<section class="sec sec--cream">
  <div class="container">
    <div class="split-copy">
      <div>
        <span class="kicker">SE PREPOZNAŠ?</span>
        <h2>Vse nekako teče. Samo ti se včasih izgubiš vmes.</h2>
      </div>
      <div class="split-copy-body">
        <p>Dan se še dobro ne začne, pa imaš v glavi že seznam vsega, kar moraš narediti. Otroci, služba, družina, obveznosti. Za vse nekako najdeš čas, zase pa pogosto zmanjka energije.</p>
        <p>Ob tem opažaš, da nisi več povsem ista. Morda manj zaupaš sebi, pogosteje dvomiš o svojih odločitvah in se sprašuješ, ali si dovolj dobra mama, partnerka, sodelavka.</p>
        <p>Trudiš se, da bi vse uskladila. Tudi ko narediš ogromno, imaš občutek, da bi lahko naredila še več. In ko si končno vzameš nekaj časa zase, se pogosto oglasi občutek krivde.</p>
        <p>Nekje med vsemi temi vlogami in pričakovanji pa se vedno pogosteje sprašuješ, kaj si pravzaprav želiš ti.</p>
        <p class="closing">Ni treba, da imaš vse odgovore. Za začetek je dovolj, da se začneš spraševati tudi o sebi.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">KONČNO TUDI TI</span>
      <h2>Kolikokrat si si že rekla: »Ko bo malo manj vsega, bom pa jaz na vrsti«?</h2>
      <p class="sec-intro">Ko bodo otroci večji. Ko bo v službi bolj mirno. Ko bo doma vse urejeno.</p>
      <p class="sec-intro">Ampak vedno pride nekaj novega. In ti spet počakaš.</p>
    </div>
    <div class="sec-head-center" style="margin-bottom:0;">
      <h2>Kaj, če bi začela živeti malo bolj po svoje?</h2>
    </div>
    <div class="point-grid">
      <article class="point-card">
        <p>Rekla ne, ne da bi potem ves večer premlevala, ali si koga prizadela.</p>
      </article>
      <article class="point-card">
        <p>Sprejela odločitev, ne da bi prej potrebovala potrditev vseh okoli sebe.</p>
      </article>
      <article class="point-card">
        <p>Si dovolila želeti nekaj zase, tudi če drugi tega ne razumejo.</p>
      </article>
    </div>
    <p class="closing-line">In nehala čakati, da bodo vsi drugi prišli na vrsto pred tabo.</p>
  </div>
</section>

<section class="sec sec--cream">
  <div class="container">
    <span class="kicker">INDIVIDUALNI COACHING</span>
    <h2 class="sec-title">Ne potrebuješ še nekoga, ki ti bo povedal, kaj moraš narediti.</h2>
    <div class="prose-block">
      <p>Verjetno imaš že sama dovolj dolg seznam stvari, ki bi jih morala narediti, spremeniti ali izboljšati.</p>
      <p class="prose-emphasis">Pri meni ne boš dobila še enega.</p>
      <p>Na najinih srečanjih se bova ustavili pri vprašanjih, za katera v vsakdanjem tempu pogosto zmanjka prostora. Kaj si v resnici želiš? Zakaj tako težko rečeš ne? Čigava pričakovanja poskušaš izpolniti? Kaj te ustavlja, ko želiš nekaj spremeniti?</p>
      <p>Včasih bova raziskovali prepričanja, ki jih imaš o sebi. Drugič tvoje vrednote, potrebe ali odločitve, pred katerimi stojiš. Ne bova iskali odgovorov, ki bi bili pravi za vse, ampak tiste, ki imajo smisel zate.</p>
      <p>Ker ni pomembno samo, da veš, kaj si želiš spremeniti. Pomembno je tudi, da najdeš svoj način, kako to prenesti v vsakdanje življenje.</p>
    </div>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <div class="hero-split hero-split--reverse">
      <div class="hero-split-copy">
        <span class="kicker">SPOZNAJ ME</span>
        <h2>Živjo, sem Tea.</h2>
        <p>Sem profesionalna coachinja z akreditacijama ICF ACC in EMCC EIA. Pa tudi mama dveh fantov, ki iz lastne izkušnje ve, kako zelo se lahko z materinstvom spremenijo naši pogledi nase, delo in življenje.</p>
        <p>Pri svojem delu mi je pomembno, da imaš prostor za iskren pogovor, razmislek in svoja spoznanja. Brez obsojanja in brez pričakovanj, kakšna bi morala biti.</p>
        <div class="hero-actions" style="margin-bottom:0;">
          <a href="o-meni.html" class="btn btn-secondary">Več o meni</a>
        </div>
      </div>
      <div class="hero-split-media">
        <img src="assets/images/tea-sofa.webp" alt="Tea Knez" loading="lazy" width="960" height="1280">
      </div>
    </div>
  </div>
</section>
""" + testimonials_section() + """
<section class="sec sec--bordo">
  <div class="container">
    <div class="invite">
      <span class="kicker">ZAČNIVA S POGOVOROM</span>
      <h2>Ni treba, da čakaš, da bo vse drugo urejeno.</h2>
      <p>Če se prepoznaš v zapisanem in si želiš nekaj spremeniti, te vabim na uvodni pogovor.</p>
      <p>Spoznali se bova, pogovorili o tem, kaj te trenutno zaposluje, in preverili, ali je coaching prava izbira zate.</p>
      <a href="kontakt.html?namen=uvodni-pogovor" class="btn btn-light">Dogovori se za uvodni pogovor</a>
    </div>
  </div>
</section>"""

    page = head(
        "Tea Knez - profesionalni coaching za ženske in organizacije",
        "Individualni coaching za ženske, ki želijo raziskati, kdo so danes, kaj jim je pomembno in kaj si želijo zase. Coaching in delavnice tudi za podjetja.",
        f"{SITE_URL}/", 0,
        og_image="tea-blazer.webp", og_image_alt="Tea Knez, profesionalna coachinja",
        extra_jsonld=_person_jsonld()
    ) + header("home", 0) + body + footer(0)
    write("index.html", page)


# ---------- ABOUT ----------
def page_about():
    body = """<section class="sec sec--cream">
  <div class="container">
    <div class="hero-split">
      <div class="hero-split-copy">
        <span class="kicker">O MENI</span>
        <h1>Živjo, sem Tea. In tudi sama sem morala na novo ugotoviti, kdo sem.</h1>
        <p>Sem profesionalna coachinja z akreditacijama ICF ACC in EMCC EIA, magistra prava in mama dveh fantov. Rada imam dobre pogovore, iskrena vprašanja in ljudi, ki si upajo podvomiti v to, kar so dolgo imeli za samoumevno.</p>
        <p>Dolgo sem verjela, da moram imeti stvari pod nadzorom. Da moram vedeti, kaj delam, kam grem in kako bom vse skupaj izpeljala. Pa še najbolje, da mi pri tem uspeva na vseh področjih življenja. :)</p>
        <p>Danes na marsikaj gledam drugače. Ne verjamem, da moramo imeti življenje ves čas pod nadzorom, niti da obstaja ena prava pot, ki bi ji morali slediti.</p>
        <p>Verjamem pa, da je vredno kdaj ustaviti avtomatski pilot in se vprašati, ali so odločitve, ki jih sprejemamo, še vedno naše.</p>
        <p>In prav tak prostor želim ustvarjati tudi pri svojem delu.</p>
      </div>
      <div class="hero-split-media">
        <img src="assets/images/tea-sofa.webp" alt="Tea Knez, profesionalna coachinja" loading="eager" width="960" height="1280">
      </div>
    </div>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <div class="narrow-col">
      <span class="kicker">MOJA POT</span>
      <h2 class="sec-title">Od prava do coachinga. Z nekaj ovinki vmes.</h2>
      <p>Moja poklicna pot ni bila ravno zgodba o tem, kako sem že pri petih letih vedela, kaj želim postati. :)</p>
      <p>Po študiju prava sem delala v različnih okoljih, prevzemala različne odgovornosti in se preizkusila tudi v podjetništvu. Veliko sem se naučila, a sem se ob tem vedno znova spraševala, kaj je tisto, kar si zares želim početi.</p>
      <p>Potem sem postala mama. In čeprav sem mislila, da imam precej jasno predstavo o sebi in svojem življenju, se je marsikaj spremenilo. Moje prioritete, odnos do dela, pričakovanja do sebe in pogled na to, kaj zame sploh pomeni uspeh.</p>
      <p>Na tej poti sem se srečala tudi z izgorelostjo. To ni bila edina prelomnica, je pa bila ena tistih izkušenj, ob katerih sem začela resneje razmišljati, kako želim živeti in delati.</p>
      <p>Coaching sem najprej spoznala kot klientka. In presenetilo me je, koliko lahko odneseš iz pogovora, v katerem ti nihče ne deli nasvetov, ne odloča namesto tebe in te ne poskuša prepričati, kaj bi bilo zate najbolje.</p>
      <p>Namesto tega dobiš prostor, da začneš drugače razmišljati, prepoznavati svoje vzorce in iskati odgovore, ki imajo smisel zate.</p>
      <p>Ta izkušnja je pomembno vplivala na mojo odločitev, da se tudi sama podam na pot profesionalnega coachinga.</p>
      <p>Danes pri svojem delu združujem strokovno znanje, različne življenjske in poklicne izkušnje ter predvsem iskreno radovednost do ljudi in njihovih zgodb.</p>
    </div>
  </div>
</section>

<section class="sec sec--bordo">
  <div class="container">
    <span class="kicker">MOJ PRISTOP</span>
    <h2 class="sec-title">Pri meni ti ni treba imeti vsega pod nadzorom.</h2>
    <div class="prose-block">
      <p>Ni ti treba priti z jasnimi odgovori, popolno razlago svoje situacije ali načrtom, kaj želiš doseči. Lahko prideš tudi z mislimi, ki jih še sama težko ubesediš.</p>
      <p>Kot coachinja sem radovedna, neposredna in iskrena. Rada poslušam tudi tisto, kar ostane neizrečeno, opazim besede, ki jih večkrat ponoviš, in postavim vprašanje, ob katerem se morda za trenutek ustaviš.</p>
      <p>Ne bom ti vedno postavljala samo prijetnih vprašanj. Včasih bova pogledali tudi tja, kjer se pojavijo dvomi, nasprotja ali prepričanja, ki jih do zdaj morda nisi postavila pod vprašaj. Vedno pa v tempu in globini, ki ju želiš raziskovati sama.</p>
      <p>Pri svojem delu mi je pomembno, da se počutiš slišano in spoštovano. Da lahko razmišljaš na glas, se ne strinjaš z mano, se nasmejiš ali preprosto nekaj časa ostaneš v tišini.</p>
      <p>Ne verjamem, da obstaja ena prava pot za vse. Verjamem pa, da si zaslužiš prostor, v katerem lahko odkriješ svojo.</p>
    </div>
  </div>
</section>

<section class="sec sec--cream">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">KAJ MI JE POMEMBNO</span>
      <h2>V kaj verjamem kot coachinja?</h2>
      <p class="sec-intro">Način, kako delam, ni odvisen samo od mojega znanja in izkušenj. Pomembne so mi tudi vrednote, ki jih prinašam v vsak coaching odnos.</p>
    </div>
    <div class="value-grid">
      <article class="value-item">
        <span class="value-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/></svg>
        </span>
        <div>
          <h3>Pristnost</h3>
          <p>Verjamem, da ti ni treba postati drugačna različica sebe, da bi bila dovolj dobra. Pomembno mi je, da lahko raziskuješ, kdo si, brez potrebe po ugajanju ali dokazovanju.</p>
        </div>
      </article>
      <article class="value-item">
        <span class="value-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>
        </span>
        <div>
          <h3>Svoboda izbire</h3>
          <p>Ne verjamem v eno pravo pot za vse. Spoštujem tvojo pravico, da sprejemaš lastne odločitve, tudi kadar so drugačne od mojih pogledov.</p>
        </div>
      </article>
      <article class="value-item">
        <span class="value-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h6M14 12h6"/><circle cx="12" cy="12" r="2"/></svg>
        </span>
        <div>
          <h3>Spoštovanje in enakovrednost</h3>
          <p>V coaching odnos vstopava kot partnerici. Ti si strokovnjakinja za svoje življenje, jaz pa prinašam coaching znanje, vprašanja in drugačne perspektive.</p>
        </div>
      </article>
      <article class="value-item">
        <span class="value-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l2.4 5.4 5.6.6-4.2 3.9 1.2 5.6L12 15.8 6.9 18.5l1.2-5.6L4 9l5.6-.6z"/></svg>
        </span>
        <div>
          <h3>Iskrenost in pogum</h3>
          <p>Pomembno mi je, da si lahko iskrena do sebe. Da si upaš pogledati tudi tisto, kar ni vedno prijetno, in raziskati vprašanja, ki jih je včasih lažje pustiti pri miru.</p>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <span class="kicker">MOJA STROKOVNA POT</span>
    <h2 class="sec-title">Strokovnost, ki jo nenehno nadgrajujem.</h2>
    <p class="sec-intro">Profesionalni coaching zame pomeni tudi odgovornost do klientov. Zato vlagam v svoje znanje, razvijam coaching kompetence in pri delu sledim etičnim standardom ICF in EMCC.</p>
    <div class="accred-grid">
      <div class="accred">
        <img src="assets/images/acc-icf.webp" alt="ICF ACC - Associate Certified Coach" loading="lazy">
        <h3>ICF ACC</h3>
        <p>Mednarodna akreditacija Associate Certified Coach organizacije International Coaching Federation.</p>
      </div>
      <div class="accred">
        <img src="assets/images/eia-emcc.webp" alt="EMCC Global Individual Accreditation - EIA" loading="lazy">
        <h3>EMCC EIA</h3>
        <p>Mednarodna individualna akreditacija za profesionalno coaching in mentorsko prakso organizacije EMCC Global.</p>
      </div>
    </div>
    <div class="accred-extra">
      <h3>Izobrazba in strokovna vključenost</h3>
      <p>Sem magistra prava z dodatnimi usposabljanji s področja coachinga, mediacije, NLP in komunikacije. Sem tudi članica Upravnega odbora ICF Slovenija in skupnosti Coachiefy, kjer ostajam povezana s strokovnim okoljem ter nadaljnjim razvojem coachinga.</p>
    </div>
  </div>
</section>

<section class="sec sec--bordo">
  <div class="container">
    <div class="invite">
      <span class="kicker">MOJI ZAPISI</span>
      <h2>Ker vseh misli pač ne morem zadržati zase.</h2>
      <p>O materinstvu, spremembah, pričakovanjih, odnosu do sebe in vseh tistih vprašanjih, ki se nam porajajo nekje med vsakdanjimi obveznostmi.</p>
      <p>Na blogu delim svoja razmišljanja, izkušnje in drugačne poglede na stvari, ki jih pogosto jemljemo za samoumevne.</p>
      <a href="blog/" class="btn btn-light">Preberi moje zapise</a>
    </div>
  </div>
</section>"""

    page = head(
        "O meni - Tea Knez, profesionalna coachinja",
        "Sem Tea Knez, profesionalna coachinja z akreditacijama ICF ACC in EMCC EIA. Spoznaj mojo pot, pristop in vrednote, ki jih prinašam v vsak coaching odnos.",
        f"{SITE_URL}/o-meni.html", 0,
        og_image="tea-sofa.webp", og_image_alt="Tea Knez, profesionalna coachinja",
        extra_jsonld=[
            _person_jsonld(),
            _breadcrumb_jsonld([("Domov", f"{SITE_URL}/"), ("O meni", f"{SITE_URL}/o-meni.html")]),
        ]
    ) + header("about", 0) + body + footer(0)
    write("o-meni.html", page)


# ---------- ZA POSAMEZNICE ----------
def page_za_posameznice():
    body = """<section class="sec sec--cream">
  <div class="container">
    <div class="hero-split">
      <div class="hero-split-copy">
        <span class="kicker">INDIVIDUALNI COACHING ZA ŽENSKE</span>
        <h1>Več jasnosti. Manj dvomov. Odločitve, za katerimi lahko stojiš.</h1>
        <p>Morda si želiš spremembe, pa ne veš, kje začeti. Morda imaš občutek, da si ves čas razpeta med tem, kar potrebujejo drugi, in tem, kar si želiš sama. Ali pa si pred odločitvijo, o kateri razmišljaš že mesece, a se nikakor ne premakneš naprej.</p>
        <p>Individualni coaching je prostor, kjer lahko raziščeš svoje misli, želje in možnosti. Brez dodatnih nasvetov, kakšna bi morala biti, in brez pričakovanja, da moraš imeti vse odgovore že danes.</p>
        <div class="hero-actions" style="margin-bottom:0;">
          <a href="kontakt.html?namen=uvodni-pogovor" class="btn btn-primary">Dogovori se za brezplačen uvodni pogovor</a>
        </div>
      </div>
      <div class="hero-split-media">
        <img src="assets/images/delovni-zvezek.webp" alt="Coaching delovni zvezek Kaj pa jaz? na mizi s kavo in beležko" loading="eager" width="854" height="1180">
      </div>
    </div>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">SPOZNAJ COACHING</span>
      <h2>Coaching je več kot samo pogovor.</h2>
      <p class="sec-intro">Coaching ni pogovor, v katerem ti nekdo pove, kako moraš živeti. Je partnerstvo, v katerem skozi razmislek, vprašanja in nova spoznanja raziskuješ svoje možnosti, sprejemaš odločitve in iščeš poti do sprememb, ki si jih želiš.</p>
    </div>
    <div class="duo-cols">
      <div class="duo-col">
        <h3>Kaj coaching je</h3>
        <p>Zaupen in ustvarjalen proces, v katerem sva enakovredni partnerici. Ti prinašaš svoje izkušnje, želje in cilje, jaz pa vprašanja, aktivno poslušanje in prostor za raziskovanje. Skupaj odkrivava nove perspektive in možnosti, ti pa odločaš, kaj je zate pravi naslednji korak.</p>
      </div>
      <div class="duo-col">
        <h3>Kaj coaching ni</h3>
        <p>Coaching ni psihoterapija, svetovanje ali mentorstvo. Kot coachinja ne postavljam diagnoz, ne zdravim duševnih stisk in ne prevzemam odločitev namesto tebe. Prav tako ti ne ponujam univerzalnih nasvetov ali vnaprej pripravljenih rešitev.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--cream">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">KDAJ NA COACHING?</span>
      <h2>Morda se prepoznaš v kateri od teh situacij.</h2>
      <p class="sec-intro">Na coaching ne prihajajo samo ženske, ki so pred veliko življenjsko odločitvijo. Včasih je razlog nekaj, kar se ponavlja že dolgo, pa si do zdaj nisi vzela časa, da bi se temu zares posvetila.</p>
    </div>
    <div class="situation-grid">
      <article class="situation">
        <h3>Ves čas usklajuješ vse in vse druge.</h3>
        <p>Zase pa pogosto zmanjka časa. Želiš si postaviti meje, ne da bi te ob tem vedno spremljal občutek krivde.</p>
      </article>
      <article class="situation">
        <h3>Preveč razmišljaš in premalo zaupaš sebi.</h3>
        <p>Odločitve premlevaš znova in znova, iščeš potrditve pri drugih in se sprašuješ, ali si se odločila prav.</p>
      </article>
      <article class="situation">
        <h3>Pred tabo je sprememba.</h3>
        <p>Vračanje v službo, nova karierna smer ali druga življenjska prelomnica. Želiš raziskati, kaj si danes želiš in kako naprej.</p>
      </article>
      <article class="situation">
        <h3>Nekje med vsemi vlogami pogrešaš sebe.</h3>
        <p>Rada imaš svoje življenje, pa vseeno čutiš, da nekaj manjka. Želiš si bolje razumeti, kaj je pomembno tebi, ne samo drugim.</p>
      </article>
      <article class="situation">
        <h3>Od sebe pričakuješ ogromno.</h3>
        <p>Trudiš se biti dobra mama, partnerka, sodelavka. Tudi ko narediš veliko, vidiš predvsem tisto, česar nisi. Želiš si manj pritiska in več prostora za svoje potrebe.</p>
      </article>
      <article class="situation">
        <h3>Težko poveš, kaj si zares želiš.</h3>
        <p>Pogosto se prilagodiš drugim, da ne bi koga razočarala ali povzročila konflikta. Svoje želje raje zadržiš zase, čeprav si želiš, da bi jih znala izraziti bolj odkrito in samozavestno.</p>
      </article>
    </div>
    <p class="closing-line">Ni treba, da se prepoznaš v vseh situacijah. Pomembno je, kaj želiš raziskati ti.</p>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">NAJINO SODELOVANJE</span>
      <h2>Kako začneva?</h2>
      <p class="sec-intro">Za prvi korak ne potrebuješ pripravljenega načrta. Dovolj je, da si želiš raziskati, ali je coaching prava izbira zate.</p>
    </div>
    <ol class="steps">
      <li class="step">
        <span class="step-num">01</span>
        <div>
          <h3>Dogovoriva se za uvodni pogovor</h3>
          <p>Kratek, brezplačen in neobvezujoč pogovor, v katerem se spoznava, pogovoriva o tem, kaj te trenutno zaposluje, in preveriva, ali je coaching ustrezna oblika podpore zate.</p>
        </div>
      </li>
      <li class="step">
        <span class="step-num">02</span>
        <div>
          <h3>Določiva smer sodelovanja</h3>
          <p>Če se odločiš za coaching, se pogovoriva o tem, kaj želiš skozi proces doseči, kako bova sodelovali in kaj lahko pričakuješ. Cilje lahko med procesom tudi prilagajava, če se tvoje potrebe spremenijo.</p>
        </div>
      </li>
      <li class="step">
        <span class="step-num">03</span>
        <div>
          <h3>Začneva s coaching srečanji</h3>
          <p>Na srečanjih raziskujeva teme, ki jih prineseš. Skozi vprašanja, poslušanje in razmislek odkrivaš nove perspektive, prepoznavaš svoje možnosti in izbiraš korake, ki jih želiš preizkusiti v vsakdanjem življenju.</p>
        </div>
      </li>
      <li class="step">
        <span class="step-num">04</span>
        <div>
          <h3>Spremljava tvoj napredek</h3>
          <p>Med procesom se vračava k tvojim ciljem, spoznanjem in spremembam, ki jih opažaš. Ob zaključku pogledava, kaj si odnesla iz sodelovanja in kako želiš nadaljevati.</p>
        </div>
      </li>
    </ol>
    <div class="step-note">
      <h3>Zaupnost in varen prostor</h3>
      <p>Coaching poteka v zaupnem in spoštljivem okolju. Pred začetkom se dogovoriva o načinu sodelovanja, zaupnosti in drugih pomembnih pogojih.</p>
    </div>
  </div>
</section>

<section class="sec sec--cream sec--tight">
  <div class="container">
    <div class="sec-head-center">
      <h2>Praktične informacije</h2>
    </div>
    <div class="facts">
      <div class="fact">
        <h3>60 minut</h3>
        <p>Trajanje posameznega coaching srečanja.</p>
      </div>
      <div class="fact">
        <h3>Online srečanja</h3>
        <p>Srečanja potekajo na daljavo, v dogovorjenih terminih.</p>
      </div>
      <div class="fact">
        <h3>Priporočen proces: 6–9 srečanj</h3>
        <p>Za bolj poglobljeno raziskovanje in prenos spoznanj v vsakdanje življenje priporočam proces vsaj šestih srečanj, pogosto pa devetih. Obseg in tempo sodelovanja prilagodiva tvojim ciljem in potrebam.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--bordo">
  <div class="container">
    <div class="invite">
      <span class="kicker">ZAČNIVA S POGOVOROM</span>
      <h2>Kaj, če bi tokrat dala priložnost sebi?</h2>
      <p>Ni treba, da že danes veš, kaj želiš spremeniti ali kako boš to naredila.</p>
      <p>Na brezplačnem uvodnem pogovoru se bova spoznali, pogledali, kaj te trenutno zaposluje, in preverili, ali je coaching prava izbira zate. Brez obveznosti in brez pritiska.</p>
      <a href="kontakt.html?namen=uvodni-pogovor" class="btn btn-light">Dogovori se za brezplačen uvodni pogovor</a>
    </div>
  </div>
</section>"""

    page = head(
        "Individualni coaching za ženske - Tea Knez",
        "Individualni coaching za ženske: več jasnosti, manj dvomov in odločitve, za katerimi lahko stojiš. Brezplačen uvodni pogovor, online srečanja po 60 minut.",
        f"{SITE_URL}/za-posameznice.html", 0,
        og_image="delovni-zvezek.webp", og_image_alt="Coaching delovni zvezek Kaj pa jaz?",
        extra_jsonld=_breadcrumb_jsonld([("Domov", f"{SITE_URL}/"), ("Individualni coaching", f"{SITE_URL}/za-posameznice.html")])
    ) + header("individuals", 0) + body + footer(0)
    write("za-posameznice.html", page)


# ---------- ZA PODJETJA ----------
def page_za_podjetja():
    body = """<section class="sec sec--cream">
  <div class="container">
    <div class="hero-split">
      <div class="hero-split-copy">
        <span class="kicker">COACHING IN DELAVNICE ZA PODJETJA</span>
        <h1>Razvoj zaposlenih ni samo vprašanje kompetenc.</h1>
        <p>Za učinkovito sodelovanje niso pomembna le znanja in veščine, temveč tudi samozavedanje, komunikacija, zaupanje vase in sposobnost soočanja s spremembami.</p>
        <p>Z individualnim coachingom in delavnicami podpiram zaposlene pri razvoju teh področij ter pri izzivih, ki jih prinašajo delo, odnosi in pomembni karierni prehodi.</p>
        <div class="hero-actions" style="margin-bottom:0;">
          <a href="kontakt.html?namen=podjetja" class="btn btn-primary">Povprašajte o sodelovanju</a>
        </div>
      </div>
      <div class="hero-split-media">
        <img src="assets/images/delavnica.webp" alt="Tea Knez vodi delavnico za skupino zaposlenih" loading="eager" width="1280" height="1244">
      </div>
    </div>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">OBLIKE SODELOVANJA</span>
      <h2>Kako lahko podprem vašo organizacijo?</h2>
      <p class="sec-intro">Vsaka organizacija ima svoje izzive, vsaka ekipa pa svoje potrebe. Zato lahko sodelovanje oblikujemo glede na cilje organizacije in ljudi, ki jim je namenjeno.</p>
    </div>
    <div class="service-grid">
      <article class="service-card">
        <h3>Individualni coaching zaposlenih</h3>
        <p>Individualni coaching zaposlenim omogoča zaupen prostor za raziskovanje poklicnih izzivov, sprejemanje odločitev, razvoj samozavedanja in iskanje lastnih načinov za učinkovitejše delovanje.</p>
        <p>Primeren je za zaposlene in vodje, ki se soočajo s spremembami, zahtevnimi odločitvami, izzivi v komunikaciji, postavljanjem meja ali prevzemanjem novih odgovornosti.</p>
      </article>
      <article class="service-card">
        <h3>Delavnice za zaposlene in ekipe</h3>
        <p>Interaktivne delavnice, ki udeležencem omogočajo raziskovanje konkretnih izzivov, izmenjavo pogledov in preizkušanje novih pristopov.</p>
        <p>Vsebine lahko vključujejo komunikacijo, sodelovanje, samozavedanje, postavljanje meja, osebno odgovornost ter soočanje s spremembami. Teme in izvedbo prilagodimo potrebam organizacije.</p>
      </article>
      <article class="service-card service-card--feature">
        <span class="service-badge">Specializacija</span>
        <span class="service-tag">POSEBNO PODROČJE</span>
        <h3>Podpora ob vrnitvi na delo</h3>
        <p>Vrnitev po starševskem dopustu ali drugi daljši odsotnosti ni vedno samo nadaljevanje tam, kjer je zaposleni ostal. Spremenijo se lahko prioritete, pričakovanja, samozavest in način usklajevanja poklicnega ter zasebnega življenja.</p>
        <p>Z individualnim coachingom in prilagojenimi delavnicami organizacijam pomagam oblikovati podporo zaposlenim pri tem prehodu, da lahko raziščejo svoje potrebe, pričakovanja in možnosti za uspešno ponovno vključitev v delovno okolje.</p>
      </article>
    </div>
  </div>
</section>

<section class="sec sec--bordo">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">ZA IZZIVI SO LJUDJE</span>
      <h2>Za vsakim poklicnim izzivom je tudi osebna zgodba.</h2>
      <p class="sec-intro">Težave pri komunikaciji, sprejemanju odločitev ali soočanju s spremembami niso vedno samo vprašanje znanja in kompetenc. V ozadju so lahko tudi prepričanja, strahovi, pričakovanja in načini razmišljanja, ki vplivajo na to, kako posameznik deluje.</p>
      <p class="sec-intro">Coaching zaposlenim omogoča, da te vzorce ozavestijo, raziščejo drugačne perspektive in poiščejo načine delovanja, ki so bolj skladni z njihovimi vrednotami, potrebami in cilji.</p>
    </div>
    <div class="situation-grid">
      <article class="situation">
        <h3>Komunikacija in odnosi</h3>
        <p>Kaj se zgodi, ko zaposleni težko izrazi svoje mnenje, se izogiba konfliktom ali vedno prevzame več, kot zmore?</p>
      </article>
      <article class="situation">
        <h3>Nove vloge in odgovornosti</h3>
        <p>Kako posameznik razvija zaupanje vase, ko prevzame novo vlogo, se sooči z dvomi ali občutkom, da mora ves čas dokazovati svojo vrednost?</p>
      </article>
      <article class="situation">
        <h3>Spremembe in prehodi</h3>
        <p>Kako najde svojo pot naprej, ko se spremenijo okoliščine, prioritete ali predstava o tem, kaj si želi od svoje kariere?</p>
      </article>
      <article class="situation">
        <h3>Pritiski in pričakovanja</h3>
        <p>Kaj posameznika žene, da si postavlja vedno višja pričakovanja, težko reče ne ali ima občutek, da nikoli ne naredi dovolj?</p>
      </article>
    </div>
  </div>
</section>

<section class="sec sec--cream">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">POTEK SODELOVANJA</span>
      <h2>Od prvega pogovora do izvedbe.</h2>
      <p class="sec-intro">Vsako sodelovanje se začne z razumevanjem potreb organizacije in ljudi, ki jim je podpora namenjena. Na tej podlagi skupaj oblikujemo ustrezen način sodelovanja.</p>
    </div>
    <ol class="steps">
      <li class="step">
        <span class="step-num">01</span>
        <div>
          <h3>Uvodni pogovor z organizacijo</h3>
          <p>Pogovorimo se o izzivih, potrebah in pričakovanjih ter preverimo, ali je ustreznejši individualni coaching, delavnica ali kombinacija obojega.</p>
        </div>
      </li>
      <li class="step">
        <span class="step-num">02</span>
        <div>
          <h3>Dogovor o sodelovanju</h3>
          <p>Opredelimo cilje, obseg, način izvedbe in pogoje sodelovanja. Pri individualnem coachingu se posebej dogovorimo tudi o vlogah, odgovornostih in zaupnosti med organizacijo, zaposlenim in coachinjo.</p>
        </div>
      </li>
      <li class="step">
        <span class="step-num">03</span>
        <div>
          <h3>Izvedba coachinga ali delavnic</h3>
          <p>Individualni coaching poteka v zaupnem partnerstvu s posameznim zaposlenim, ki aktivno sooblikuje cilje in vsebino srečanj. Delavnice pa prilagodimo dogovorjeni temi, skupini in potrebam organizacije.</p>
        </div>
      </li>
      <li class="step">
        <span class="step-num">04</span>
        <div>
          <h3>Pregled sodelovanja</h3>
          <p>Ob zaključku preverimo doseganje dogovorjenih ciljev in možnosti za nadaljnje sodelovanje. Pri individualnem coachingu morebitno povratno informiranje organizacije poteka izključno v vnaprej dogovorjenih mejah zaupnosti.</p>
        </div>
      </li>
    </ol>
  </div>
</section>

<section class="sec sec--bordo">
  <div class="container">
    <div class="narrow-col">
      <span class="kicker">STROKOVNOST IN ZAUPNOST</span>
      <h2>Zaupanje je temelj dobrega coachinga.</h2>
      <p>Pri svojem delu sledim etičnim standardom ICF (International Coaching Federation) in EMCC (European Mentoring and Coaching Council), ki poudarjajo strokovnost, integriteto, zaupnost in spoštovanje avtonomije klienta.</p>
      <p>Tudi kadar coaching financira organizacija, je pomembno, da ima zaposleni varen in zaupen prostor za raziskovanje svojih izzivov, potreb in ciljev.</p>
      <p>Zato pred začetkom sodelovanja jasno opredelimo pričakovanja, odgovornosti in meje zaupnosti. Vsebina individualnih srečanj se ne deli z delodajalcem brez ustreznega soglasja oziroma druge veljavne podlage za razkritje.</p>
      <p class="cred-line" style="margin-top:28px;">ICF ACC · EMCC EIA</p>
    </div>
  </div>
</section>

<section class="sec sec--beige">
  <div class="container">
    <div class="invite">
      <span class="kicker">ZAČNIMO S POGOVOROM</span>
      <h2>Kakšno podporo trenutno potrebujejo vaši zaposleni?</h2>
      <p>Razmišljate o individualnem coachingu, delavnici ali podpori zaposlenim ob pomembnih kariernih prehodih?</p>
      <p>Vabim vas na neobvezujoč uvodni pogovor, na katerem bomo raziskali potrebe vaše organizacije in možnosti sodelovanja.</p>
      <a href="kontakt.html?namen=podjetja" class="btn btn-primary">Povprašajte o sodelovanju</a>
    </div>
  </div>
</section>"""

    page = head(
        "Coaching in delavnice za podjetja - Tea Knez",
        "Individualni coaching in delavnice za razvoj zaposlenih, boljšo komunikacijo in podporo ob kariernih prehodih, vključno z vrnitvijo po starševskem dopustu.",
        f"{SITE_URL}/za-podjetja.html", 0,
        og_image="delavnica.webp", og_image_alt="Delavnica za zaposlene - Tea Knez",
        extra_jsonld=_breadcrumb_jsonld([("Domov", f"{SITE_URL}/"), ("Za podjetja", f"{SITE_URL}/za-podjetja.html")])
    ) + header("companies", 0) + body + footer(0)
    write("za-podjetja.html", page)


# ---------- BLOG INDEX ----------
POSTS = [
    {"slug":"slaba-vest-ko-naredim-nekaj-zase", "cat":"materinstvo", "title":"Zakaj imam slabo vest, ko naredim nekaj zase?",
     "summary":"Krivda ob času zase ne pomeni nujno, da si sebična. Lahko se pojavi zato, ker prvič ravnaš drugače in tudi svoje potrebe postavljaš med pomembne.",
     "image":"slaba-vest-ko-naredim-nekaj-zase-tea-knez.webp",
     "image_alt":"Ženska sedi sama v kavarni s kavo in knjigo, roko pa ima položeno na telefon",
     "date":"2026-09-02"},
    {"slug":"zakaj-se-ne-znam-ustaviti", "cat":"materinstvo", "title":"Zakaj se ne znam ustaviti?",
     "summary":"Počitek je lahko težak, kadar je tvoja vrednost dolgo povezana s koristnostjo, odgovornostjo in tem, koliko narediš za druge.",
     "image":"zakaj-se-ne-znam-ustaviti-tea-knez.webp",
     "image_alt":"Ženska zlaga perilo v dnevni sobi, kjer jo čakata prazen naslanjač in skodelica čaja",
     "date":"2026-08-25"},
    {"slug":"cas-zase-ne-vem-kaj-potrebujem", "cat":"materinstvo", "title":"Ko imam čas zase, ne vem, kaj potrebujem",
     "summary":"Si želiš časa zase, ko ga dobiš, pa ne veš, kaj potrebuješ? Preberi, zakaj počitek lahko postane nova naloga in kako ponovno slišati sebe.",
     "image":"cas-zase-ne-vem-kaj-potrebujem-tea-knez.webp",
     "image_alt":"Ženska med prostim trenutkom razmišlja, kaj v tem trenutku potrebuje",
     "date":"2026-08-19"},
    {"slug":"sem-samo-se-mama", "cat":"materinstvo", "title":"»Sem samo še mama?«",
     "summary":"Se po materinstvu ne prepoznaš več? Preberi, zakaj lahko ljubezen do otroka in pogrešanje sebe obstajata hkrati ter kako raziskati, kdo si danes.",
     "image":"sem-samo-se-mama-tea-knez.webp",
     "image_alt":"Ženska razmišlja o svoji identiteti in odnosu do sebe po materinstvu",
     "date":"2026-08-11"},
    {"slug":"identiteta-po-materinstvu", "cat":"materinstvo", "title":"Ko se rodi otrok, se spremeni tudi ženska",
     "summary":"Materinstvo lahko spremeni identiteto, potrebe in odnos ženske do sebe. Preberi, zakaj so te spremembe razumljive in zakaj si zaslužijo prostor.",
     "image":"identiteta-po-materinstvu-tea-knez.webp",
     "image_alt":"Mama z dojenčkom v naročju zamišljeno gleda skozi okno, v steklu se zrcali njen odsev",
     "date":"2026-08-04"},
    {"slug":"vracanje-s-porodniskega-dopusta", "cat":"materinstvo", "title":"Vračanje s porodniškega dopusta: ko se vrneš drugačna",
     "summary":"Kako podpreti vračanje s porodniškega dopusta? O izzivih, prehodu in vlogi coachinga za posameznice in podjetja.",
     "image":"blog-vracanje.webp"},
    {"slug":"kako-preprečiti-izgorelost-v-podjetjih-kultura-ravnovesja-ne-žrtvovanja", "cat":"podjetja", "title":"Kako preprečiti izgorelost v podjetjih: kultura ravnovesja, ne žrtvovanja",
     "summary":"Kultura zaupanja in ravnovesja namesto preobremenjenosti. Ustvari delovno okolje, kjer ljudje resnično zmorejo rasti.",
     "image":"blog-izgorelost.webp"},
    {"slug":"kako-premagati-sindrom-vsiljivca-(imposter-syndrome)", "cat":"rast", "title":"Kako premagati sindrom vsiljivca (imposter syndrome)",
     "summary":"O dvomu vase, ki te želi zaščititi. Spoznaj, kako prepoznati ta glas in verjeti, da si že zdaj dovolj.",
     "image":"blog-sindrom.webp"},
    {"slug":"ko-mir-v-sebi-postane-pomembnejši-od-tega-da-imaš-prav", "cat":"rast", "title":"Ko mir v sebi postane pomembnejši od tega, da imaš prav",
     "summary":"O notranji svobodi, ko mir izbereš pred dokazovanjem. Nauči se slišati sebe, ne potrebe po potrditvi.",
     "image":"blog-mir.webp"},
    {"slug":"samozavest-ni-nekaj-kar-imas", "cat":"rast", "title":"Samozavest ni nekaj, kar imaš – ampak nekaj, kar gradiš",
     "summary":"Samozavest ni lastnost, s katero se rodiš – je pot, ki jo gradiš skozi drobne izbire in notranji dialog.",
     "image":"blog-samozavest.webp"},
    {"slug":"avtenticno-vodenje-moc-resnicnega-stika", "cat":"podjetja", "title":"Avtentično vodenje: Moč resničnega stika",
     "summary":"Avtentično vodenje ne temelji na popolnosti, temveč na iskrenosti in povezanosti. Kako voditi z resničnostjo.",
     "image":"blog-avtenticno.webp"},
    {"slug":"notranji-kritik-kako-ga-prepoznati-in-spremeniti-v-zaveznika", "cat":"rast", "title":"Notranji kritik: Kako ga prepoznati in spremeniti v zaveznika",
     "summary":"Notranji kritik pogosto ovira našo rast, a lahko postane vir učenja. Kako ga prepoznati in preoblikovati.",
     "image":"blog-notranji.webp"},
    {"slug":"odpornost-in-proznost-celostna-notranja-moc", "cat":"rast", "title":"Odpornost in prožnost: Kako graditi notranjo moč celostno",
     "summary":"Odpornost ni le miselna trdnost – vključuje telo, čustva, misli in odnose. Kako celostno graditi notranjo moč.",
     "image":"blog-odpornost.webp"},
]

# Three confirmed blog categories. Assignment of existing articles is a
# proposal pending Tea's confirmation (see PREVERITI in the brief).
BLOG_CATEGORIES = [
    ("materinstvo", "Materinstvo in družina"),
    ("rast", "Osebna rast in coaching"),
    ("podjetja", "Za podjetja in vodje"),
]
CATEGORY_LABEL = dict(BLOG_CATEGORIES)


def newsletter_section(depth=0):
    """Signups are delivered through web3forms with their own subject, so the
    form genuinely works rather than only appearing to."""
    p = "../" * depth
    return f"""<section class="sec sec--bordo sec--tight">
  <div class="container">
    <div class="newsletter">
      <span class="kicker">OSTANIVA V STIKU</span>
      <h2>Kakšno dobro misel ti lahko pošljem tudi v nabiralnik.</h2>
      <p>Občasno ti pošljem novo razmišljanje z bloga, povabilo na brezplačno delavnico ali posebno ponudbo za coaching. Brez vsakodnevnih sporočil in nepotrebne pošte.</p>
      <form class="newsletter-form" action="https://api.web3forms.com/submit" method="POST" data-web3forms>
        <input type="hidden" name="access_key" value="e78b399d-a62e-494f-b90b-519f4b7f7a48">
        <input type="hidden" name="subject" value="Nova prijava na e-novice">
        <input type="hidden" name="from_name" value="teaknez.com - e-novice">
        <input type="checkbox" name="botcheck" style="display:none;" tabindex="-1" autocomplete="off" aria-hidden="true">
        <label class="sr-only" for="news-email-{depth}">Tvoj e-naslov</label>
        <input id="news-email-{depth}" name="email" type="email" required autocomplete="email" placeholder="Tvoj e-naslov">
        <button type="submit" class="btn btn-light">Prijavi se na novice</button>
      </form>
      <p class="newsletter-note">S prijavo soglašaš s prejemanjem e-novic. Odjaviš se lahko kadarkoli. Več v <a href="{p}politika-zasebnosti.html">politiki zasebnosti</a>.</p>
      <div class="form-status" role="status" aria-live="polite"></div>
    </div>
  </div>
</section>
"""


def page_blog_index():
    filters = "\n".join(
        f'      <button type="button" class="filter-btn" data-filter="{key}" aria-pressed="false">{label}</button>'
        for key, label in BLOG_CATEGORIES
    )
    cards = []
    for p in POSTS:
        cat = p.get("cat", "")
        date_html = ""
        if p.get("date"):
            date_html = f'<time datetime="{p["date"]}">{_sl_date(p["date"])}</time>'
        cards.append(f"""      <a class="post-card" href="{p['slug']}/" data-cat="{cat}">
        <div class="post-card-media"><img src="../assets/images/{p['image']}" alt="{p.get('image_alt', '')}" loading="lazy"></div>
        <div class="post-card-body">
          <p class="post-card-meta"><span>{CATEGORY_LABEL.get(cat, '')}</span>{date_html}</p>
          <h3>{p['title']}</h3>
          <p>{p['summary']}</p>
          <span class="post-card-more">Preberi članek</span>
        </div>
      </a>""")
    cards_html = "\n".join(cards)

    body = f"""<section class="sec sec--cream sec--tight">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">BLOG · TEA KNEZ</span>
      <h1>Misli, ki jih ne zadržim zase.</h1>
      <p class="sec-intro">O materinstvu, spremembah, odnosu do sebe in vprašanjih, ki si jih včasih premalokrat zastavimo.</p>
    </div>
    <div class="filters" role="group" aria-label="Filtriraj zapise po kategoriji">
      <button type="button" class="filter-btn" data-filter="all" aria-pressed="true">Vsi zapisi</button>
{filters}
    </div>
    <div class="posts-grid" id="posts-grid">
{cards_html}
    </div>
    <p class="posts-empty" id="posts-empty" hidden>V tej kategoriji trenutno ni zapisov. <button type="button" class="link-btn" data-filter="all">Prikaži vse zapise</button></p>
  </div>
</section>
""" + newsletter_section(1)

    page = head(
        "Blog - misli o materinstvu, spremembah in odnosu do sebe | Tea Knez",
        "O materinstvu, spremembah, odnosu do sebe in vprašanjih, ki si jih včasih premalokrat zastavimo. Zapisi coachinje Tee Knez.",
        f"{SITE_URL}/blog/", 1,
        og_image="blog-vracanje.webp", og_image_alt="Blog - Tea Knez",
        extra_jsonld=[
            {
                "@type": "Blog",
                "@id": f"{SITE_URL}/blog/#blog",
                "name": "Blog - Tea Knez",
                "url": f"{SITE_URL}/blog/",
                "inLanguage": "sl",
                "publisher": {"@id": f"{SITE_URL}/#organization"},
            },
            _breadcrumb_jsonld([("Domov", f"{SITE_URL}/"), ("Blog", f"{SITE_URL}/blog/")]),
        ]
    ) + header("blog", 1) + body + footer(1)
    write("blog/index.html", page)


# ---------- BLOG POSTS ----------
def render_blog_post(slug, title, lead, image, body_html,
                     description=None, seo_title=None, cta=None, author_bio=None):
    """Render one blog post.

    lead        - visible intro paragraph under the title
    description - meta description (falls back to lead)
    seo_title   - full <title> override (falls back to "<title> - Tea Knez")
    cta         - dict(text=..., label=..., href=...) rendered under the article
    author_bio  - bio text for the author card under the article; each post
                  uses the wording from its own SEO brief, so pass it in
    Date, image alt and prev/next all come from the POSTS entry.
    """
    meta = next((p for p in POSTS if p["slug"] == slug), {})
    date = meta.get("date")
    image_alt = meta.get("image_alt", "")
    description = description or lead
    prev_post, next_post = _post_neighbors(slug)

    cat_label = CATEGORY_LABEL.get(meta.get("cat", ""), "")
    bits = []
    if cat_label:
        bits.append(f'<span class="post-meta-cat">{cat_label}</span>')
    bits.append(f'<span class="post-meta-author">{BLOG_AUTHOR}</span>')
    if date:
        bits.append(f'<time datetime="{date}">{_sl_date(date)}</time>')
    sep = '<span class="post-meta-sep" aria-hidden="true">·</span>'
    byline = '\n    <p class="post-meta">' + sep.join(bits) + "</p>"

    cta_html = ""
    if cta:
        cta_html = f"""
<section class="section">
  <div class="container-narrow">
    <div class="post-cta">
      <p>{cta["text"]}</p>
      <a href="{cta["href"]}" class="btn btn-primary">{cta["label"]}</a>
    </div>
  </div>
</section>
"""

    author_html = ""
    if author_bio:
        author_html = f"""
<section class="section">
  <div class="container-narrow">
    <aside class="post-author">
      <div class="post-author-photo">
        <img src="../../assets/images/about-tea.webp" alt="Tea Knez" loading="lazy">
      </div>
      <div class="post-author-body">
        <span class="post-author-eyebrow">Avtorica</span>
        <p class="post-author-name">Tea Knez</p>
        <p>{author_bio}</p>
        <a class="post-author-link" href="../../o-meni.html">Spoznaj Teo in njeno pot</a>
      </div>
    </aside>
  </div>
</section>
"""

    nav = ""
    if prev_post or next_post:
        prev_html = f'<a href="../{prev_post["slug"]}/" style="display:flex;flex-direction:column;gap:6px;color:var(--ink-soft);"><span style="font-size:.8rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);">← Prejšnji</span><strong style="color:var(--ink);font-family:var(--serif);font-size:1.15rem;font-weight:500;">{prev_post["title"]}</strong></a>' if prev_post else "<span></span>"
        next_html = f'<a href="../{next_post["slug"]}/" style="display:flex;flex-direction:column;gap:6px;color:var(--ink-soft);text-align:right;align-items:flex-end;"><span style="font-size:.8rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);">Naslednji →</span><strong style="color:var(--ink);font-family:var(--serif);font-size:1.15rem;font-weight:500;">{next_post["title"]}</strong></a>' if next_post else "<span></span>"
        nav = f"""
<section class="section">
  <div class="container-narrow">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;padding-top:50px;border-top:1px solid var(--line);">
      {prev_html}
      {next_html}
    </div>
  </div>
</section>
"""
    body = f"""<section class="post-hero">
  <div class="container-narrow">
    <a class="back-link" href="../../blog/">Nazaj na blog</a>
    <h1>{title}</h1>{byline}
    <p class="lead">{lead}</p>
  </div>
</section>

<div class="post-image"><img src="../../assets/images/{image}" alt="{image_alt}"></div>

<article class="post-body">
{body_html}
</article>
{cta_html}{author_html}{nav}"""

    post_url = f"{SITE_URL}/blog/{slug}/"
    page = head(
        seo_title or f"{title} - Tea Knez",
        description,
        post_url, 2,
        og_type="article", og_image=image, og_image_alt=image_alt or title,
        article_date=date,
        extra_jsonld=[
            _blogposting_jsonld(title, description, post_url, image, date=date),
            _breadcrumb_jsonld([
                ("Domov", f"{SITE_URL}/"),
                ("Blog", f"{SITE_URL}/blog/"),
                (title, post_url),
            ]),
        ]
    ) + header("blog", 2) + body + footer(2)
    write(f"blog/{slug}/index.html", page)


def page_blog_slaba_vest():
    body = """<p>Po dolgem času si vzameš dve uri zase. Greš na kavo, trening, sprehod ali k frizerju. Nihče doma ni ogrožen. Otrok je z osebo, ki ji zaupaš. Vse je urejeno.</p>
<p>Pa vseeno večkrat pogledaš na telefon. Razmišljaš, ali je doma vse v redu. Ali si predolgo odsotna. Ali bi morala ta čas porabiti koristneje. Morda se celo zalotiš, da si želiš čim prej nazaj.</p>
<p>Ne zato, ker ti čas zase ne bi prijal. Ampak zato, ker se je skupaj z njim pojavila slaba vest.</p>
<p>Če se v tem prepoznaš, to še ne pomeni, da si sebična ali da delaš nekaj narobe. Krivda se lahko pojavi tudi takrat, ko narediš nekaj, česar nisi vajena: med vse pomembne ljudi za trenutek postaviš tudi sebe.</p>
<p>Slaba vest, ko mama naredi nekaj zase, se lahko pojavi zaradi prepričanja, da morajo biti potrebe otroka in drugih vedno pred njenimi. Občutek krivde zato ni vedno dokaz napačnega ravnanja, ampak je lahko odziv na postavljanje novih meja in upoštevanje lastnih potreb.</p>

<h2>Zakaj se krivda pojavi ravno takrat, ko poskrbiš zase?</h2>
<p>Ko postaneš mama, se veliko tvoje pozornosti razumljivo usmeri v otroka. Spremljaš njegove potrebe, predvidevaš, organiziraš in se prilagajaš.</p>
<p>Sčasoma lahko postane samoumevno, da so potrebe drugih na prvem mestu, tvoje pa pridejo na vrsto, ko je vse drugo urejeno.</p>
<p>Težava je, da je le redko zares vse urejeno. Vedno obstaja še nekaj, kar bi lahko naredila. Nekaj, kar bi lahko pripravila, pospravila ali preverila. Zato se lahko ob času zase pojavi občutek, da si nekje, kjer ne bi smela biti.</p>
<p>V ozadju je lahko prepričanje: Če nekaj namenim sebi, bo nekdo drug zaradi tega dobil manj.</p>
<p>Toda čas zase ni nujno nekaj, kar jemlješ družini. Lahko je tudi način, da ostajaš v odnosu s sabo, svojimi potrebami in omejitvami.</p>

<h2>Krivda ni vedno dokaz, da si ravnala narobe</h2>
<p>Krivda ima pomembno funkcijo. Lahko nas opozori, kadar ravnamo v nasprotju s svojimi vrednotami ali nekomu povzročimo škodo. Toda vsak občutek krivde še ni zanesljiv dokaz, da smo naredile nekaj napačnega. Včasih se krivda pojavi, ker smo prekršile staro pravilo.</p>
<p>Na primer:</p>
<ul>
  <li>dobra mama je vedno na voljo;</li>
  <li>druge moram najprej osrečiti;</li>
  <li>počitek si moram zaslužiti;</li>
  <li>če prosim za pomoč, obremenjujem druge;</li>
  <li>če uživam brez otroka, z mano nekaj ni v redu.</li>
</ul>
<p>Ta pravila lahko delujejo zelo resnično, tudi če jih nisi nikoli zavestno izbrala. Zato se ob skrbi zase lahko počutiš krivo, čeprav se v resnici samo učiš ravnati drugače.</p>

<h2>Ko si čas zase dovoliš, vendar v njem ne moreš uživati</h2>
<p>Včasih ženska fizično odide, misli pa ostanejo doma. Preverja sporočila. V glavi organizira naslednji dan. Razmišlja, kaj bo morala nadoknaditi, ko se vrne. Svojo odsotnost poskuša čim bolj skrajšati in drugim pokazati, da zaradi nje ne bodo ničesar izgubili.</p>
<p>Tako čas zase postane še ena naloga, ki jo mora opraviti pravilno in brez posledic. Toda če moraš biti tudi med počitkom odgovorna za vse, potem se v resnici nisi zares umaknila iz vloge tiste, ki vse drži skupaj. Več o tem, zakaj je lahko tako težko zares prenehati, lahko prebereš v članku <a href="../zakaj-se-ne-znam-ustaviti/">»Zakaj se ne znam ustaviti?«</a>.</p>
<p>Morda zato vprašanje ni samo kako si lahko vzamem več časa zase, ampak je tudi ali si lahko dovolim, da v tem času nisem odgovorna za vse?</p>

<h2>Skrb zase ni nasprotje skrbi za druge</h2>
<p>Skrb zase se včasih predstavlja kot razkošje: masaža, vikend oddih, popolna rutina ali veliko prostega časa.</p>
<p>Toda lahko je precej manjša in bolj vsakdanja.</p>
<p>Lahko pomeni, da:</p>
<ul>
  <li>dokončaš kavo, preden se lotiš naslednje naloge;</li>
  <li>poveš, da danes ne zmoreš še ene obveznosti;</li>
  <li>prosiš za pomoč, ne da bi najprej dokazala, da si poskusila vse;</li>
  <li>narediš nekaj samo zato, ker ti je prijetno;</li>
  <li>upoštevaš svojo utrujenost, še preden postane nevzdržna.</li>
</ul>
<p>Skrb zase ne pomeni, da potrebe drugih niso pomembne. Pomeni, da tvoje potrebe niso samodejno vedno zadnje. Če ti je ob prostem času pogosto nejasno, kaj sploh potrebuješ, o tem več v članku <a href="../cas-zase-ne-vem-kaj-potrebujem/">»Ko imam čas zase, ne vem, kaj potrebujem«</a>.</p>

<h2>Kaj ti želi krivda preprečiti?</h2>
<p>Ko se pojavi slaba vest, jo pogosto poskušamo čim prej odstraniti. Odpovemo načrt, se vrnemo domov ali si obljubimo, da si bomo naslednjič čas zase bolje zaslužile.</p>
<p>Lahko pa se ob krivdi za trenutek ustaviš in jo raziščeš. Kaj ti govori? Česa se boji, da bi se zgodilo, če bi sebe redno postavljala med pomembne? Bi koga razočarala? Bi izgubila občutek, da si dobra mama? Bi morala drugim prepustiti del odgovornosti? Bi ugotovila, da ne želiš več vsega početi tako kot prej?</p>
<p>Krivde ni treba ignorirati. Prav tako ji ni treba vedno prepustiti odločitve.</p>

<h2>Kako lahko pomaga coaching</h2>
<p>Coaching ti ne pove, koliko časa zase potrebuješ ali kako ga moraš preživeti.</p>
<p>Lahko pa ti ponudi prostor, v katerem raziščeš, kaj zate pomeni skrb zase, katera pričakovanja nosiš in zakaj se ob lastnih potrebah tako hitro pojavi krivda. Morda odkriješ, da težava ni v tem, da ne znaš poskrbeti zase.</p>
<p>Morda si se naučila, da je varneje, sprejemljiveje ali bolj pravilno vedno najprej poskrbeti za druge. Krivda se ob spremembi morda ne bo takoj umaknila.</p>
<p>Toda njena prisotnost še ne pomeni, da se moraš vrniti k staremu načinu.</p>

<p class="pullquote">Za začetek se lahko vprašaš: Kaj bi naredila zase, če krivda za trenutek ne bi odločala namesto tebe?</p>
"""
    render_blog_post(
        "slaba-vest-ko-naredim-nekaj-zase",
        "Zakaj imam slabo vest, ko naredim nekaj zase?",
        "Krivda še ne pomeni, da delaš nekaj narobe. Včasih se pojavi zato, ker prvič ravnaš drugače.",
        "slaba-vest-ko-naredim-nekaj-zase-tea-knez.webp",
        body,
        description="Imaš slabo vest, ko narediš nekaj zase? Preberi, zakaj krivda ne pomeni vedno, da delaš nekaj narobe, in kaj se lahko skriva za njo.",
        seo_title="Slaba vest, ko naredim nekaj zase | Tea Knez",
        cta={
            "text": "Če želiš raziskati, zakaj se ob tvojih potrebah tako hitro pojavi krivda in kaj bi želela izbrati drugače, si lahko ogledaš možnosti individualnega coachinga.",
            "label": "Spoznaj individualni coaching",
            "href": "../../za-posameznice.html",
        },
        author_bio="Tea Knez je nosilka akreditacij ACC pri ICF in EIA pri EMCC. Kot coachinja podpira predvsem ženske po materinstvu pri raziskovanju identitete, izčrpanosti, krivde, perfekcionizma, meja, pomembnih odločitev in odnosa do sebe.",
    )


def page_blog_zakaj_se_ne_znam_ustaviti():
    body = """<p>Ves dan si želiš trenutka miru. Ko ga končno dobiš, pa namesto počitka pospraviš kuhinjo, pripraviš stvari za naslednji dan, odgovoriš na sporočila ali začneš urejati nekaj, kar bi lahko počakalo.</p>
<p>Morda si rečeš: “Samo še to naredim, potem pa se bom malo vsedla.”</p>
<p>Toda za eno nalogo pride druga. Ko se končno ustaviš, je večer skoraj mimo. Zakaj je lahko tako težko počivati, tudi ko imaš možnost?</p>
<p>Človek se lahko težko ustavi, kadar se ob mirovanju pojavijo krivda, nemir ali občutek, da bi moral biti koristen. Če je počitek dovoljen šele po vseh opravljenih nalogah, v življenju z nenehnimi obveznostmi skoraj nikoli ne pride na vrsto.</p>

<h2>Ko mirovanje ne prinese miru</h2>
<p>Počitek navzven lahko pomeni, da sediš ali ležiš. Znotraj pa se lahko dogaja nekaj povsem drugega. Misli še vedno preverjajo, česa nisi naredila. Opaziš nered. Spomniš se obveznosti. Začneš načrtovati naslednji dan. Morda se celo pojavi nelagodje, češ da bi ta čas morala porabiti bolje. Telo se ustavi, občutek odgovornosti pa ne.</p>
<p>Zato ni nenavadno, da ženska reče, da ne zna počivati. Morda ni težava v sami dejavnosti, ampak v tem, da mirovanje odpre prostor za občutke, ki jih med nenehnim delovanjem lažje presliši. Če se ob prostem času pogosto vprašaš, kaj bi sploh potrebovala, lahko prebereš tudi članek <a href="../cas-zase-ne-vem-kaj-potrebujem/">»Ko imam čas zase, ne vem, kaj potrebujem«</a>.</p>

<h2>Počitek kot nagrada</h2>
<p>Veliko ljudi se zgodaj nauči, da počitek pride po opravljenem delu. Najprej naloge, nato prosti čas. Najprej odgovornost, nato užitek. Najprej poskrbi za druge, nato zase.</p>
<p>Takšno pravilo je lahko uporabno, dokler je delo mogoče zares zaključiti. V življenju z majhnimi otroki pa je le redko vse narejeno. Perilo se ponovno nabere. Nekdo je spet lačen. Na seznam pride nova obveznost.</p>
<p>Če je počitek dovoljen šele po koncu vseh nalog, ga skoraj ni mogoče doseči. Zato vprašanje ni samo, ali imaš dovolj časa. Pomembno je tudi, pod katerimi pogoji si počitek sploh dovoliš.</p>

<h2>Ko je koristnost povezana z lastno vrednostjo</h2>
<p>Za nekatere ženske je občutek vrednosti močno povezan s tem, koliko naredijo za druge.</p>
<p>Ko organizirajo, rešujejo, skrbijo in predvidevajo, vedo, kakšna je njihova naloga. Čutijo, da prispevajo in da so potrebne. Ko se ustavijo, pa se lahko pojavi vprašanje: Kaj pa zdaj upravičuje moj čas?</p>
<p>Takrat počitek ni samo odsotnost dela. Lahko pomeni trenutek, v katerem nisi koristna, učinkovita ali na voljo.</p>
<p>In če si dolgo prejemala priznanje predvsem zato, ker veliko zmoreš, je takšno mirovanje lahko neprijetno. To ne pomeni, da je s tabo nekaj narobe. Pomeni lahko, da si oblikovala način delovanja, ki ti je nekoč pomagal, danes pa te morda izčrpava.</p>

<h2>Počivati, čeprav seznam ni prazen</h2>
<p>Počitek ne zahteva, da se pretvarjaš, da nalog ni. Zahteva pa možnost, da se v nekem trenutku odločiš: Za danes je dovolj.</p>
<p>To je lahko težje, kot se sliši. Morda se moraš srečati z občutkom, da nekoga razočaraš. Da nisi naredila dovolj. Da bi dobra mama, partnerka ali sodelavka nadaljevala. Toda seznam opravkov ni objektivno merilo tvoje vrednosti. Tvoje potrebe ne postanejo legitimne šele takrat, ko so potrebe vseh drugih izpolnjene.</p>
<p>Če se ob skrbi zase pogosto pojavi tudi slaba vest, o tem več v članku <a href="../slaba-vest-ko-naredim-nekaj-zase/">»Zakaj imam slabo vest, ko naredim nekaj zase?«</a>.</p>

<h2>Kaj se pojavi, ko se ustaviš?</h2>
<p>Namesto da se siliš v počitek, lahko najprej radovedno opazuješ, kaj ti ga otežuje.</p>
<p>Ko se vsedeš, kaj najprej pomisliš?</p>
<p>Se pojavi krivda? Nemir? Dolgčas? Strah, da boš izgubila nadzor? Občutek, da moraš biti vedno pripravljena?</p>
<p>Morda ugotoviš, da ne potrebuješ nove tehnike sproščanja.</p>
<p>Morda potrebuješ dovoljenje, da nehaš, tudi kadar bi lahko naredila še več.</p>

<h2>Kako lahko pomaga coaching</h2>
<p>Coaching ni namenjen temu, da ti nekdo predpiše, koliko časa moraš počivati ali kako naj bo videti tvoja rutina. Lahko pa ponudi prostor, v katerem raziščeš pravila, ki jih imaš o počitku, delu in lastni vrednosti.</p>
<p>Kaj mora biti izpolnjeno, da si dovoliš ustaviti? Česa se bojiš, da bi se zgodilo, če ne bi vsega dokončala? Komu poskušaš dokazati, da zmoreš? Včasih se sprememba ne začne z dodatno prosto uro.</p>

<p class="pullquote">Začne se z drugačnim odgovorom na vprašanje: Ali si smem odpočiti, tudi če bi lahko naredila še več?</p>
"""
    render_blog_post(
        "zakaj-se-ne-znam-ustaviti",
        "Zakaj se ne znam ustaviti?",
        "Včasih počitka ne preprečuje pomanjkanje časa, ampak to, kar začutimo, ko nehamo delati.",
        "zakaj-se-ne-znam-ustaviti-tea-knez.webp",
        body,
        description="Se težko ustaviš tudi takrat, ko bi lahko počivala? Preberi, zakaj se lahko ob počitku pojavita nemir in krivda ter kaj se skriva pod njima.",
        seo_title="Zakaj se ne znam ustaviti in počivati? | Tea Knez",
        cta={
            "text": "Če želiš raziskati, kaj se v tebi zgodi, ko se ustaviš, ter kakšna pravila imaš o počitku, odgovornosti in lastni vrednosti, si lahko ogledaš individualni coaching.",
            "label": "Spoznaj individualni coaching",
            "href": "../../za-posameznice.html",
        },
        author_bio="Tea Knez je nosilka akreditacij ACC pri ICF in EIA pri EMCC. Kot coachinja podpira predvsem ženske po materinstvu pri raziskovanju identitete, izčrpanosti, krivde, perfekcionizma, meja, pomembnih odločitev in odnosa do sebe.",
    )


def page_blog_cas_zase():
    body = """<p>Ko večino dneva skrbiš za otroka, družino, delo in stvari, ki morajo biti opravljene, se čas zase pogosto zdi kot nekaj, kar bi rešilo vsaj del tvoje utrujenosti.</p>
<p>Želiš si miru. Nekaj ur brez prekinitev. Trenutek, ko te nihče ničesar ne potrebuje. Ko ta čas končno pride, pa se lahko zgodi nekaj nepričakovanega.</p>
<p>Ne veš, kaj bi z njim.</p>
<p>Bi počivala? Šla na sprehod? Telovadila? Poklicala prijateljico? Prebrala knjigo ali naredila nekaj koristnega? Morda vzameš telefon, pospraviš kuhinjo ali urediš nekaj, kar že dolgo čaka. Ko se prosti čas izteče, imaš občutek, da ga nisi dobro izkoristila.</p>

<p class="pullquote">Končno sem imela čas zase, pa sem ga spet zapravila.</p>

<p>Ko imaš čas zase, morda ne veš, kaj bi počela, ker je bil tvoj vsakdan dolgo usmerjen predvsem v potrebe drugih. Odgovor na vprašanje »Kaj potrebujem jaz?« zato ne pride vedno takoj. To ne pomeni, da nimaš svojih želja ali da si izgubila sebe. Morda svoje potrebe samo ponovno prepoznavaš.</p>

<h2>Čas zase ni vedno takoj prijeten</h2>
<p>Veliko govorimo o tem, kako pomembno je, da si mama vzame čas zase. Manj pogosto pa govorimo o tem, kaj se zgodi, ko ga dejansko dobi.</p>
<p>Tvoj vsakdan je večino časa organiziran okoli vprašanj: Kaj potrebuje otrok? Kaj moram še urediti? Kaj ne sme biti pozabljeno? Ko se nato pojavi vprašanje »Kaj si želim jaz?«, odgovor morda ne pride takoj.</p>
<p>To ne pomeni, da si izgubila sebe. Morda si bila samo tako dolgo usmerjena v potrebe drugih, da svoje trenutno težje prepoznaš. Če se poleg nejasnosti glede svojih potreb srečuješ tudi z občutkom, da se po materinstvu ne prepoznaš več, lahko prebereš članek <a href="../sem-samo-se-mama/">»Sem samo še mama?«</a>.</p>

<h2>Ko prosti čas postane nova naloga</h2>
<p>Če počivaš, se morda sprašuješ, ali bi morala ta čas izkoristiti bolj aktivno. Če greš telovadit, razmišljaš, ali bi bolj potrebovala počitek. Če ostaneš doma, se ti zdi, da bi morala ven.</p>
<p>Namesto vprašanja »Kaj mi danes ustreza?« se pojavi vprašanje: Kaj bi bilo najbolj pravilno narediti?</p>
<p>Takrat čas zase postane nov projekt, pri katerem lahko uspeš ali ne uspeš.</p>
<p>Pojavi se lahko notranji glas: »Morala bi uživati.« »Spet sem zapravila čas.« »Včasih sem vedela, kaj me veseli.« Toda ne obstaja en pravilen način počitka. Včasih potrebuješ gibanje, drugič tišino. Včasih pogovor, drugič samoto. Včasih pa samo uro, v kateri ti ni treba narediti ničesar.</p>

<h2>Morda ne potrebuješ še enega načrta</h2>
<p>Ko ne veš, kaj bi počela, lahko začneš iskati nove ideje, rutine in nasvete za skrb zase. Nekateri so lahko uporabni, vendar lahko tudi skrb zase hitro postane še en seznam stvari, ki bi jih morala opraviti.</p>
<p>Morda ne potrebuješ več idej. Morda potrebuješ prostor, da opaziš, kaj se dogaja v tebi. Odgovor se morda ne pokaže kot jasna želja. Lahko se začne kot občutek, da bi rada zaprla oči. Kot želja po sprehodu brez cilja. Kot odpor do še enega pogovora. Kot potreba, da ti danes ne bi bilo treba biti koristna. Prepoznavanje potreb je lahko postopno učenje poslušanja majhnih signalov, ki jih v hrupu vsakdana hitro preslišiš.</p>

<h2>Tudi telefon in opravila imajo svojo vlogo</h2>
<p>Opravila so jasna. Imajo začetek, konec in viden rezultat. Zato lahko delujejo varno in obvladljivo. Telefon pa ti omogoči, da za trenutek ne izbiraš in ne čutiš vsega, kar se pokaže, ko se ustaviš.</p>
<p>Namesto kritike lahko poskusiš z radovednostjo: Kaj mi telefon ali opravilo v tem trenutku omogočata? Kaj bi se pojavilo, če ne bi takoj zapolnila praznega prostora?</p>

<h2>Ni ti treba vedeti takoj</h2>
<p>Če dolgo nisi imela dovolj prostora zase, en prost večer verjetno ne bo takoj prinesel jasnosti.</p>
<p>Morda šele takrat opaziš, kako utrujena si. Morda postaneš nemirna ali ne začutiš ničesar posebnega. Tudi to je informacija. Ni ti treba vsakega trenutka zase spremeniti v posebno izkušnjo. Ni treba, da si po njem boljša, mirnejša ali produktivnejša.</p>
<p>Coaching ti lahko ponudi prostor, kjer ti ni treba takoj poznati odgovorov. Kjer lahko brez pritiska raziskuješ svoje občutke, potrebe in želje. Morda nisi pozabila, kaj potrebuješ. Morda šele ponovno vzpostavljaš stik z delom sebe, ki je bil dolgo tišji od vseh drugih zahtev.</p>
<p>Več o tem, kako materinstvo lahko spremeni odnos ženske do sebe, lahko prebereš v članku <a href="../identiteta-po-materinstvu/">»Ko se rodi otrok, se spremeni tudi ženska«</a>.</p>

<p class="pullquote">Za začetek se lahko vprašaš: Kaj se zgodi v meni, ko se vprašam, kaj si želim jaz?</p>
"""
    render_blog_post(
        "cas-zase-ne-vem-kaj-potrebujem",
        "Ko imam čas zase, ne vem, kaj potrebujem",
        "Dolgo si želiš nekaj časa zase. Ko ga končno dobiš, pa obstaneš in ugotoviš, da sploh ne veš, kaj bi ti v tem trenutku ustrezalo.",
        "cas-zase-ne-vem-kaj-potrebujem-tea-knez.webp",
        body,
        description="Si želiš časa zase, ko ga dobiš, pa ne veš, kaj potrebuješ? Preberi, zakaj počitek lahko postane nova naloga in kako ponovno slišati sebe.",
        seo_title="Ko imam čas zase, ne vem, kaj potrebujem | Tea Knez",
        cta={
            "text": "Morda ti ni treba že vedeti, kaj potrebuješ. Če želiš v zaupnem coaching procesu raziskati, kaj se zgodi, ko se ustaviš, in ponovno vzpostaviti stik s svojimi potrebami, si lahko ogledaš možnosti individualnega coachinga.",
            "label": "Razišči individualni coaching",
            "href": "../../za-posameznice.html",
        },
        author_bio="Tea Knez je nosilka akreditacij ACC pri ICF in EIA pri EMCC. Kot coachinja podpira predvsem ženske po materinstvu pri raziskovanju identitete, izčrpanosti, krivde, perfekcionizma, meja, pomembnih odločitev in odnosa do sebe.",
    )


def page_blog_sem_samo_se_mama():
    body = """<p>Ko postaneš mama, se v kratkem času spremeni zelo veliko. Tvoj vsakdan, telo, odnosi, odgovornosti in način, kako razporejaš svoj čas. Potrebe otroka hitro postanejo zelo jasne. Tvoje pa se lahko počasi umaknejo v ozadje.</p>
<p>Morda se nekega dne ustaviš in pomisliš: Sploh ne vem več, kdo sem.</p>
<p>Po materinstvu se morda ne prepoznaš več, ker so se v kratkem času spremenili tvoj vsakdan, telo, odnosi, odgovornosti in prostor za lastne potrebe. To ne pomeni, da si izgubila sebe. Morda še nisi imela dovolj prostora, da bi opazila, kako si se ob materinstvu spremenila tudi ti.</p>

<h2>Lahko imaš rada svoje življenje in hkrati pogrešaš sebe</h2>
<p>Ta občutek je lahko zelo zmeden. Veš, da imaš veliko razlogov za hvaležnost. Rada imaš svojega otroka. Morda si si materinstva dolgo želela.</p>
<p>Kljub temu lahko pogrešaš svojo prejšnjo svobodo, energijo, delo, ustvarjalnost ali preprosto občutek, da veš, kaj ti je všeč in kaj potrebuješ. To ne pomeni, da si nehvaležna ali da je s tabo nekaj narobe. Ljubezen do otroka in pogrešanje sebe lahko obstajata hkrati.</p>

<h2>Morda nisi izgubila sebe</h2>
<p>Ko rečeš, da se ne prepoznaš več, to ne pomeni nujno, da te ni več. Morda se je samo spremenilo toliko stvari, da še nisi imela prostora opaziti, kako si se ob njih spremenila tudi ti.</p>
<p>Stvari, ki so ti bile pomembne prej, ti danes morda ne pomenijo več enako. Nekateri deli tebe so lahko za nekaj časa ostali v ozadju, ker zanje ni bilo dovolj časa, energije ali prostora. To ne pomeni, da so izginili.</p>

<h2>Ni se ti treba vrniti k stari sebi</h2>
<p>Pogosto slišimo, da se mora ženska po rojstvu otroka »spet najti«. Kot da obstaja ena prejšnja različica nje, h kateri se mora vrniti. Kaj pa, če cilj ni vrnitev?</p>
<p>Morda lahko raziščeš, kaj želiš iz svojega prejšnjega življenja ohraniti, kaj se je spremenilo in kaj ti je pomembno danes. Ni ti treba takoj vedeti, kdo si zdaj.</p>
<p>Identiteta po materinstvu se lahko oblikuje postopoma. Več o spremembah identitete, potreb in odnosa do sebe po rojstvu otroka lahko prebereš tudi v članku <a href="../identiteta-po-materinstvu/">»Ko se rodi otrok, se spremeni tudi ženska«</a>.</p>

<h2>Kdo si danes?</h2>
<p>Ko se ne prepoznaš več, lahko hitro začneš iskati odgovor zunaj sebe.</p>
<p>Opazuješ druge ženske, bereš nasvete in razmišljaš, kaj bi morala narediti, da bi se spet počutila kot ti. Toda ni enega pravilnega odgovora. Ena ženska pogreša delo. Druga potrebuje več samote. Tretja si želi več bližine, ustvarjalnosti ali podpore.</p>
<p>Pomembno je, da začneš raziskovati, kaj je tvoje. Kaj pogrešaš? Kaj ti je danes pomembnejše kot prej? Pri čem se za trenutek spet počutiš kot ti?</p>

<h2>Coaching kot prostor za raziskovanje</h2>
<p>Coaching ni namenjen temu, da ti nekdo pove, kdo si ali kakšna bi morala postati.</p>
<p>Lahko pa ti ponudi prostor, kjer se ti ni treba prilagajati potrebam vseh drugih. Prostor, kjer lahko raziščeš svoje občutke, potrebe, vrednote in odločitve. Včasih prvi premik ni odgovor.</p>
<p>Lahko je že spoznanje: Morda nisem izginila. Morda šele spoznavam, kdo sem danes.</p>

<p class="pullquote">Za začetek se lahko vprašaš: Kaj pri sebi danes najtežje prepoznam?</p>
"""
    render_blog_post(
        "sem-samo-se-mama",
        "»Sem samo še mama?«",
        "Lahko imaš rada svojega otroka in svoje življenje, pa se vseeno ne počutiš več kot ti.",
        "sem-samo-se-mama-tea-knez.webp",
        body,
        description="Se po materinstvu ne prepoznaš več? Preberi, zakaj lahko ljubezen do otroka in pogrešanje sebe obstajata hkrati ter kako raziskati, kdo si danes.",
        seo_title="Sem samo še mama? Izguba sebe po materinstvu | Tea Knez",
        cta={
            "text": "Ni ti treba že vedeti, kdo si danes. Če želiš v zaupnem coaching procesu raziskati, kaj se je po materinstvu spremenilo in kaj je pomembno zate, si lahko ogledaš možnosti individualnega coachinga.",
            "label": "Oglej si individualni coaching",
            "href": "../../za-posameznice.html",
        },
        author_bio="Tea Knez je nosilka akreditacij ACC pri ICF in EIA pri EMCC. Kot coachinja podpira predvsem ženske po materinstvu pri raziskovanju identitete, izčrpanosti, krivde, perfekcionizma, meja, pomembnih odločitev in odnosa do sebe.",
    )


def page_blog_identiteta():
    body = """<p>Ko se rodi otrok, se pozornost razumljivo usmeri vanj. Kako spi? Ali dovolj je? Kako napreduje? Kako se privaja na svet? Tudi mamo ljudje pogosto vprašajo, kako je, vendar se pogovor hitro vrne k otroku. Manj pogosto se zares ustavimo pri vprašanju, kaj se je z rojstvom otroka spremenilo v njej. Materinstvo namreč ni samo nova vloga in drugačen urnik. Za nekatere ženske pomeni tudi veliko spremembo identitete, prioritet, odnosov in načina, kako doživljajo sebe.</p>

<h2>Ko postaneš mama, ne prenehaš biti ti</h2>
<p>Materinstvo lahko v življenje prinese veliko ljubezni, bližine in smisla. Hkrati lahko prinese odgovornost, ki je prej nisi poznala, utrujenost, manj predvidljivosti in občutek, da so tvoje potrebe nenadoma vedno na koncu. Zelo dobro začneš prepoznavati, kaj potrebuje otrok. Opazuješ, predvidevaš, organiziraš in skrbiš, da vsakdan nekako teče. Veliko težje pa lahko postane odgovoriti na preprosta vprašanja: Kako sem jaz? Kaj potrebujem? Kaj mi je pomembno? Kaj me še veseli?</p>
<p>To ne pomeni, da je s tabo nekaj narobe. Prav tako ne pomeni, da nisi hvaležna ali da svojega otroka nimaš dovolj rada. Lahko imaš rada materinstvo in hkrati pogrešaš dele sebe, ki imajo zdaj manj prostora. Lahko si predana mama in si obenem želiš pogovora, v katerem nisi obravnavana samo skozi svojo vlogo. Ženska z rojstvom otroka ne preneha obstajati, vendar se lahko v množici novih potreb, nalog in pričakovanj težje sliši.</p>

<h2>Tudi sama sem potrebovala pomoč</h2>
<p>Ta tema zame ni samo strokovna. Med drugo porodniško sem doživela močno telesno in mentalno izčrpanost. Dolgo sem poskušala zdržati, obvladati vsakdan in iti naprej. Šele ko tako ni šlo več, sem si priznala, da potrebujem pomoč. Nisem potrebovala še enega seznama stvari, ki bi jih morala narediti bolje. Potrebovala sem prostor, da se ustavim, razumem, kaj se z mano dogaja, in ponovno vzpostavim stik s sabo.</p>
<p>Ta izkušnja je pomemben del razloga, da danes delam z ženskami po materinstvu. Ne zato, ker bi verjela, da vse doživljamo enako. Moja zgodba ni razlaga zgodbe druge ženske. Vem pa, kako osamljen je lahko občutek, da bi morala zmogla, medtem ko v sebi čutiš, da ne zmoreš več na isti način. In vem, kako pomembno je, da te nekdo ne poskuša takoj popraviti, ampak te najprej zares posluša.</p>

<h2>Materinstvo lahko spremeni odnos do sebe</h2>
<p>Po rojstvu otroka se lahko spremenijo tvoje prioritete, ambicije, meje in odnos do časa. Stvari, ki so se ti zdele prej pomembne, morda nimajo več enake teže. Lahko začneš drugače razmišljati o delu, partnerstvu, prijateljstvih ali načinu življenja. Morda pogrešaš svojo prejšnjo spontanost. Morda se ne prepoznaš več v ženski, kakršna si bila, hkrati pa še ne veš, kdo postajaš.</p>
<p>Ob takšnih spremembah se lahko hitro pojavi pritisk, da bi se morala »spet najti« ali vrniti k stari sebi. Toda morda naloga ni samo vrnitev. Morda potrebuješ čas in prostor, da raziščeš, kaj želiš ohraniti, kaj se je spremenilo in kaj ti je pomembno danes. Identiteta po materinstvu ni nujno nekaj, kar moraš čim hitreje dokončno opredeliti. Lahko je proces, v katerem se na novo srečuješ s sabo.</p>

<h2>Ta prostor ni namenjen temu, kako postati boljša mama</h2>
<p>Veliko vsebin za mame govori o razvoju otroka, vzgoji, spanju, prehrani in organizaciji družinskega življenja. Vse to ima svoje mesto. Ta prostor pa je namenjen drugačnim vprašanjem: Kaj se po materinstvu dogaja s tabo? Kako se je spremenil tvoj odnos do sebe? Kaj se skriva pod krivdo, perfekcionizmom, notranjim kritikom, potrebo po nadzoru ali težavo pri postavljanju meja?</p>
<p>Pri svojem delu ne izhajam iz prepričanja, da ti manjka še en pravilen odgovor. Coaching razumem kot zaupen prostor, v katerem lahko raziskuješ svoje doživljanje, potrebe, vrednote in odločitve. Coach ti ne pove, kdo bi morala biti ali kako bi morala živeti. Z vprašanji, poslušanjem in zrcaljenjem ti pomaga ustvariti več jasnosti ter slišati tudi tisto, kar v vsakdanjem hrupu težko pride do besede.</p>
<p>Ko se rodi otrok, se lahko spremeni tudi ženska. To ni napaka, ki jo je treba odpraviti. Je sprememba, ki si zasluži pozornost. Morda ti danes ni treba poznati vseh odgovorov. Začneš lahko z enim vprašanjem:</p>

<p class="pullquote">Kaj se je po materinstvu najbolj spremenilo v mojem odnosu do sebe?</p>
"""
    render_blog_post(
        "identiteta-po-materinstvu",
        "Ko se rodi otrok, se spremeni tudi ženska",
        "Materinstvo ne spremeni le vsakdana. Spremeni lahko tudi odnos ženske do sebe, njenih potreb, telesa, dela, odnosov in tega, kdo verjame, da mora biti.",
        "identiteta-po-materinstvu-tea-knez.webp",
        body,
        description="Materinstvo lahko spremeni identiteto, potrebe in odnos ženske do sebe. Preberi, zakaj so te spremembe razumljive in zakaj si zaslužijo prostor.",
        seo_title="Identiteta po materinstvu: kako se spremeni ženska | Tea Knez",
        cta={
            "text": "Materinstvo lahko odpre vprašanja, na katera ni mogoče odgovoriti z enim nasvetom. Če želiš raziskati, kaj se je po materinstvu spremenilo v tvojem odnosu do sebe, si lahko ogledaš možnosti individualnega coachinga.",
            "label": "Oglej si individualni coaching",
            "href": "../../za-posameznice.html",
        },
        author_bio="Tea Knez je ACC ICF in EIA EMCC certificirana coachinja. Pri svojem delu podpira predvsem ženske po materinstvu pri raziskovanju identitete, izčrpanosti, krivde, perfekcionizma, meja in odnosa do sebe.",
    )


def page_blog_vracanje():
    body = """<p>Vračanje s porodniškega dopusta na prvi pogled deluje kot precej praktična stvar. Uvajanje otroka v vrtec. Usklajevanje urnikov. Jutra, ki naenkrat postanejo bolj intenzivna. Ponoven prehod iz domačega ritma v službenega. In potem pride še tisti trenutek, ko ponovno sedeš za računalnik in naj bi se stvari nekako nadaljevale. Pa vendar se veliko žensk v tem obdobju za trenutek ustavi in potiho pomisli:</p>

<p class="pullquote">“Nisem več ista.”</p>

<p>In res nisi.</p>

<p>Ne samo zato, ker imaš otroka. Ampak ker se je v tem času nekaj v tebi premaknilo. Drugače gledaš na čas. Na energijo. Na to, kaj ti je zares pomembno. In hkrati se znajdeš v okolju, ki od tebe pogosto pričakuje, da se boš vrnila takšna, kot si bila prej.</p>

<h2>Med dvema svetovoma</h2>
<p>Veliko žensk opisuje, da se ob vrnitvi počutijo, kot da stojijo med dvema svetovoma. Na eni strani je <strong>delo</strong>, kjer želijo ponovno najti svojo samozavest, občutek kompetentnosti in pripadnosti. Na drugi strani je <strong>dom</strong>, kjer so njihove prioritete drugačne, bolj jasne, bolj čustveno povezane.</p>

<p>Vmes pa se pojavi tiha napetost:</p>
<ul>
  <li>Ali delam dovolj?</li>
  <li>Sem še vedno “dovolj dobra” v službi?</li>
  <li>Kako naj vse to uskladim, ne da se izgubim?</li>
</ul>
<p>To niso vprašanja, na katera obstaja en pravilen odgovor. So pa vprašanja, ki si zaslužijo prostor.</p>

<h2>Prehod, ki ga pogosto ne vidimo</h2>
<p>Čeprav je vračanje s porodniškega dopusta zelo pogosta izkušnja, je kot prehod pogosto neviden. Na zunaj se zdi, da se stvari normalizirajo. Znotraj pa se pogosto dogaja veliko več.</p>
<p>Novejše raziskave kažejo, da je to ena ključnih kariernih prelomnic, ki pomembno vpliva na dobrobit, delovno učinkovitost in dolgoročno vključenost zaposlenih. Način, kako je ta prehod podprt, lahko močno zaznamuje, kako se posameznica ponovno vzpostavi v svoji vlogi.</p>

<h2>Kaj pri tem lahko naredi podjetje?</h2>
<p>Podjetja imajo tukaj večjo vlogo, kot se morda zdi na prvi pogled. Ne gre samo za fleksibilnost ali organizacijo dela (čeprav je to pomembno). Gre za to, ali zaposleni v tem obdobju dobijo prostor, kjer lahko predelajo ta prehod.</p>
<p>Ko je ta podpora prisotna, se to pokaže zelo konkretno:</p>
<ul>
  <li>zaposlene se hitreje in bolj stabilno ponovno vključijo v delo</li>
  <li>imajo več jasnosti in notranje stabilnosti</li>
  <li>so bolj zavzete in dolgoročno bolj povezane s podjetjem</li>
</ul>
<p>In pogosto je razlika prav v tem, ali imajo nekje prostor, kjer lahko stvari zares izgovorijo, razmislijo in jih postavijo na novo.</p>

<h2>Kje pride v igro coaching?</h2>
<p>Coaching ni prostor, kjer nekdo pove, kaj bi morala narediti. Je prostor, kjer lahko za trenutek ustaviš tempo in se vprašaš:</p>
<blockquote>“Kaj pa zdaj res potrebujem jaz?”</blockquote>
<p>V takem prostoru lahko:</p>
<ul>
  <li>razjasniš, kaj so tvoje prioritete v tej novi fazi</li>
  <li>ponovno vzpostaviš občutek kompetentnosti</li>
  <li>najdeš svoj način usklajevanja dela in življenja</li>
  <li>in predvsem – razviješ način delovanja, ki je zate dolgoročno vzdržen</li>
</ul>
<p>Ne gre za hitro rešitev. Gre za to, da si dovoliš, da se v novo fazo ne vrneš na silo, ampak zavestno.</p>

<p>Vračanje s porodniškega dopusta ni vrnitev nazaj. Je prehod naprej. In način, kako je ta prehod podprt, lahko naredi veliko razliko – tako za posameznico kot za organizacijo. Morda ne potrebujemo več rešitev. Morda potrebujemo več prostora, kjer si lahko stvari dovolimo na novo razumeti.</p>

<p class="pullquote">Kako si želiš, da bi izgledalo tvoje vračanje – ne takšno, kot ga pričakuje okolje, ampak takšno, ki je zares usklajeno s tabo?</p>

<div class="cta-final">
<p>👉 <strong>Če ob branju prepoznavaš sebe</strong> in čutiš, da bi ti v tem obdobju koristil prostor za razmislek in podporo, ali pa kot podjetje razmišljate, kako bolje podpreti zaposlene ob vračanju s porodniškega dopusta, me lahko kontaktiraš za kratek pogovor.</p>
</div>
"""
    render_blog_post(
        "vracanje-s-porodniskega-dopusta",
        "Vračanje s porodniškega dopusta: ko se vrneš drugačna",
        "Kako podpreti vračanje s porodniškega dopusta? O izzivih, prehodu in vlogi coachinga za posameznice in podjetja.",
        "blog-vracanje.webp",
        body,
    )


def page_blog_izgorelost():
    body = """<p class="pullquote">Izgorelost se ne začne z izčrpanostjo, ampak z željo po tem, da bi bilo vse popolno.</p>

<p>Ko ljudje v podjetju nenehno delujejo “nad svojimi mejami” – ne zato, ker morajo, ampak ker želijo dokazati svojo vrednost – se postopoma izčrpajo.</p>
<p>In ko izgori posameznik, izgubi energijo tudi ekipa. Kultura izgorelosti postane sistemska.</p>

<h2>Prvi korak: ozaveščanje</h2>
<p>Preprečevanje izgorelosti ni le osebna odgovornost, temveč vodstvena.</p>
<p>Kultura podjetja, kjer se uspeh meri le z rezultati, ne pa tudi z dobrobitjo, dolgoročno izgubi ravnovesje.</p>
<p>Voditelji, ki znajo ustvariti varno okolje, v katerem je pogovor o mejah sprejet, postavljajo temelje zdrave produktivnosti.</p>

<h2>Kako ustvariti kulturo ravnovesja</h2>
<ul>
  <li>Spodbujaj odprte pogovore o obremenjenosti brez strahu pred sodbo.</li>
  <li>Poudarjaj pomen počitka kot dela uspeha, ne kot nagrade zanj.</li>
  <li>Dajaj zgled: pokaži, da znaš ustaviti tudi sam.</li>
  <li>Prepoznaj, da so “mehke veščine” – sočutje, razumevanje, prisotnost – pravzaprav trdne veščine prihodnosti.</li>
</ul>

<ul>
  <li>Kako v našem okolju govorimo o utrujenosti?</li>
  <li>Ali znamo priznati, da smo ljudje, preden smo zaposleni?</li>
  <li>Kaj bi pomenilo, če bi bila skrb za dobrobit del naše strategije uspeha?</li>
</ul>

<p>Izgorelost ni neizogibna. Je klic po spremembi. Ko podjetje izbere kulturo zaupanja, ravnovesja in človečnosti, se delo ne le izboljša – postane prostor, kjer ljudje rastejo skupaj.</p>

<div class="cta-final">
<p>👉 <strong>Če želiš raziskati</strong>, kako v tvojem podjetju ustvariti kulturo ravnovesja in preprečiti izgorelost, me kontaktiraj – skupaj lahko razvijemo okolje, kjer uspeh temelji na zdravju, ne na izčrpanosti.</p>
</div>
"""
    render_blog_post(
        "kako-preprečiti-izgorelost-v-podjetjih-kultura-ravnovesja-ne-žrtvovanja",
        "Kako preprečiti izgorelost v podjetjih: kultura ravnovesja, ne žrtvovanja",
        "Kultura zaupanja in ravnovesja namesto preobremenjenosti. Ustvari delovno okolje, kjer ljudje resnično zmorejo rasti.",
        "blog-izgorelost.webp",
        body,
    )


def page_blog_sindrom():
    body = """<p>Kolikokrat si se vprašal/a, ali si res dovolj dober?</p>
<p>Tisti občutek, da si na “napačnem mestu” ali da bo nekdo kmalu ugotovil, da ne veš dovolj, pozna skoraj vsak.</p>
<p>To je <strong>sindrom vsiljivca</strong> – notranji glas, ki dvomi v tvojo vrednost, tudi ko imaš dokaze o uspehu pred sabo.</p>

<h2>Zakaj se pojavi</h2>
<p>Sindrom vsiljivca ni znak nesposobnosti, temveč posledica visokih standardov, perfekcionizma in notranje negotovosti.</p>
<p>Pogosto se pojavi pri ljudeh, ki jim je mar, ki želijo prispevati in delati dobro. Paradoksalno ravno ti najbolj dvomijo vase.</p>
<p>Ko te vodi notranji občutek “nisem dovolj”, se lahko ujameš v nenehno dokazovanje – dosežki pridejo, a miru ni.</p>

<h2>Kako se začne spreminjati</h2>
<p>Prvi korak je, da prepoznaš, da občutek ne odraža realnosti. Dvom ni dokaz resnice, ampak znak, da rasteš izven cone udobja.</p>
<p>Drugi korak je, da dovoliš sebi, da nisi popoln. Da uspeh ne pomeni odsotnosti napak, ampak pogum, da greš naprej, kljub njim.</p>

<ul>
  <li>Namesto “nisem dovolj dober” poskusi reči: “Učim se in rastem.”</li>
  <li>Dovoli si praznovati male uspehe.</li>
  <li>Obkroži se z ljudmi, ki ti pomagajo videti resničnost, ne iluzijo lastne negotovosti.</li>
</ul>

<ul>
  <li>Kdaj sem nazadnje podvomil/a vase kljub temu, da sem nekaj dobro naredil/a?</li>
  <li>Kako bi ravnal/a, če bi verjel/a, da sem dovolj?</li>
  <li>Katera prepričanja o sebi mi ne služijo več?</li>
</ul>

<p class="pullquote">Sindrom vsiljivca ne izgine, ko dosežeš več, ampak ko začneš verjeti, da si že zdaj dovolj.</p>

<div class="cta-final">
<p>👉 <strong>Če želiš raziskati</strong>, kako se osvoboditi notranjega dvoma in voditi iz zaupanja vase, me kontaktiraj – skupaj bova gradila tvoj občutek jasnosti in miru v profesionalni rasti.</p>
</div>
"""
    render_blog_post(
        "kako-premagati-sindrom-vsiljivca-(imposter-syndrome)",
        "Kako premagati sindrom vsiljivca (imposter syndrome)",
        "O dvomu vase, ki te želi zaščititi. Spoznaj, kako prepoznati ta glas in verjeti, da si že zdaj dovolj.",
        "blog-sindrom.webp",
        body,
    )


def page_blog_mir():
    body = """<p>Včasih nas v razpravah, odnosih ali življenjskih situacijah vodi potreba, da dokažemo svoj prav. Želimo, da drugi razumejo našo plat, da priznajo našo resnico. Toda pogosto se ob tem zapletemo v napetost, dokazovanje in čustveno izčrpanost.</p>
<p>Mir, ki ga iščemo, se oddaljuje – ravno zato, ker ga želimo doseči z razumom, ne z notranjim sprejemanjem.</p>

<h2>Pot od potrebe po prav do notranje svobode</h2>
<p>Ko mir v sebi postane pomembnejši od tega, da imaš prav, se začne prava sprememba.</p>
<p>Ne pomeni, da se vdaš ali pustiš, da te drugi pohodijo. Pomeni, da izbereš stik s sabo – da ostaneš v svoji resnici brez potrebe, da jo kdorkoli potrdi.</p>
<p class="pullquote">To je svoboda: ko tvoj notranji mir ne zavisi več od zunanjih odzivov.</p>
<p>Mir prihaja, ko se naučimo opazovati svoje misli in čustva, ne da bi jih morali takoj zagovarjati.</p>
<p>Ko v pogovoru začutimo napetost in namesto, da bi dokazovali, izberemo dih – in s tem ohranimo stik s seboj.</p>

<ul>
  <li>Ko se vprašaš: <em>“Kaj je zdaj zame res pomembno – da imam prav ali da ohranim mir?”</em></li>
  <li>Ko zavestno izbereš tišino, ne zato, ker nimaš odgovora, ampak ker mir govori glasneje kot ego.</li>
  <li>Ko razumeš, da mir ni šibkost, ampak znak notranje zrelosti.</li>
</ul>

<ul>
  <li>Kdaj sem se nazadnje zapletel/a v dokazovanje, ki mi je vzelo mir?</li>
  <li>Kaj bi se zgodilo, če bi v tistem trenutku izbrala mir namesto prav?</li>
  <li>Kako bi izgledal moj dan, če bi moj mir postal moja prioriteta?</li>
</ul>

<p>Mir v sebi je prostor, kamor se vedno lahko vrneš. Ni odvisen od zunanjih okoliščin, ampak od tvoje odločitve, da izbereš stik namesto dokazovanja.</p>

<div class="cta-final">
<p>👉 <strong>Če želiš raziskati</strong>, kako lahko gradiš notranji mir v odnosih in življenjskih izzivih, me kontaktiraj – skupaj bova odkrila načine, kako najti mir, ki ostane tudi, ko okoliščine niso popolne.</p>
</div>
"""
    render_blog_post(
        "ko-mir-v-sebi-postane-pomembnejši-od-tega-da-imaš-prav",
        "Ko mir v sebi postane pomembnejši od tega, da imaš prav",
        "O notranji svobodi, ko mir izbereš pred dokazovanjem. Nauči se slišati sebe, ne potrebe po potrditvi.",
        "blog-mir.webp",
        body,
    )


def page_blog_samozavest():
    body = """<h2>Kaj pravzaprav pomeni samozavest?</h2>
<p>Ko govorimo o samozavesti, mnogi pomislijo na ljudi, ki so glasni, karizmatični ali vedno prepričani vase. A resnična samozavest nima nujno veze z nastopom navzven. Gre za notranje stanje – za občutek, da zaupamo vase, tudi takrat, ko ne poznamo vseh odgovorov in ko ne gre vse po načrtih.</p>
<p>Samozavest ni nekaj, kar “dobimo” ali kar je dano le izbranim. Je proces, pot, ki jo gradimo z majhnimi koraki. In kar je najpomembneje – je lastnost, ki se spreminja. Včasih jo čutimo močno, drugič skoraj izgine. In to je človeško.</p>

<h2>Korenine samozavesti</h2>
<p>Naša samozavest se pogosto gradi že v otroštvu – skozi odzive staršev, učiteljev, okolja. A v odraslosti ni več odvisna samo od zunanjih potrditev. Takrat postane predvsem notranji dialog:</p>
<blockquote>Kaj verjamem o sebi? Kako govorim s sabo, ko mi ne uspe?</blockquote>
<p>Samozavest se hrani takrat, ko si dovolimo biti iskreni do sebe – ko prepoznamo svoje močne plati, pa tudi ranljivosti, in jih sprejmemo kot del celote.</p>

<p>Samozavest ne pride z enim velikim dejanjem. Gradi se skozi drobne izbire vsak dan:</p>
<ul>
  <li>ko si dovolimo izraziti svoje mnenje,</li>
  <li>ko naredimo nekaj novega, čeprav nas je strah,</li>
  <li>ko si priznamo, da smo naredili napako, in gremo naprej.</li>
</ul>
<p>Vsak tak trenutek postane nova opeka v temelju zaupanja vase.</p>

<ul>
  <li>Katere besede si najpogosteje rečem, ko naredim napako? Bi jih rekel/a enako osebi, ki jo imam rad/a?</li>
  <li>Kdaj sem nazadnje naredil/a nekaj kljub strahu – in kako sem se ob tem počutil/a?</li>
  <li>Katera mala dejanja bi mi danes pomagala okrepiti občutek, da zaupam vase?</li>
</ul>

<p>Samozavest ni končni cilj, ki ga dosežemo in obdržimo za vedno. Je kot mišica – krepi se, ko jo uporabljamo, in oslabi, če jo zanemarimo. Zato ni pomembno, da smo “vedno samozavestni”, ampak da znamo v vsakdanjih trenutkih izbrati zaupanje vase, tudi ko je težko.</p>

<div class="cta-final">
<p>👉 <strong>Če želiš raziskati</strong>, kako bi lahko krepil/a svojo samozavest v varnem, sočutnem prostoru, me kontaktiraj – skupaj bova našla načine, kako graditi temelje, ki te bodo podpirali na tvoji poti.</p>
</div>
"""
    render_blog_post(
        "samozavest-ni-nekaj-kar-imas",
        "Samozavest ni nekaj, kar imaš – ampak nekaj, kar gradiš",
        "Samozavest ni lastnost, s katero se rodiš – je pot, ki jo gradiš skozi drobne izbire in notranji dialog. Preberi, kako lahko začneš danes.",
        "blog-samozavest.webp",
        body,
    )


def page_blog_avtenticno():
    body = """<h2>Kaj pomeni biti avtentičen vodja?</h2>
<p>Vodja se pogosto razume kot oseba, ki ima odgovore, sprejema odločitve in vodi druge k ciljem. A resnično učinkovito vodenje ne temelji na popolnosti, temveč na avtentičnosti. To pomeni, da si upaš pokazati, kdo v resnici si – z močmi in z negotovostmi.</p>
<p>Avtentičen vodja ne nosi maske. Ne skuša ustvariti podobe brez napak, ampak gradi prostor, kjer se sodelavci počutijo sprejeti, slišani in vključeni. Prav ta stik je temelj zaupanja, na katerem raste sodelovanje in predanost.</p>

<p>V ekipi, kjer vlada iskrenost, se ljudje upajo izraziti. Lažje delijo svoje ideje, priznajo napake in sodelujejo pri iskanju rešitev. Vodja, ki pokaže človečnost, pravzaprav krepi svojo avtoriteto – ker gradi na zaupanju, ne na strahu.</p>
<p>Avtentično vodenje torej ni znak šibkosti, ampak poguma. Poguma, da se pokažeš resničen, da poslušaš in dopuščaš, da ima vsak glas svojo vrednost.</p>

<ul>
  <li>Kdaj sem kot vodja najbolj resnično jaz?</li>
  <li>Kaj poskušam skriti, ker mislim, da “ni dovolj dobro”?</li>
  <li>Kako lahko danes odprem več prostora za iskren dialog v svoji ekipi?</li>
</ul>

<h2>Pot avtentičnega vodenja</h2>
<p>Biti avtentičen ne pomeni, da deliš vse svoje misli brez filtra, ampak da ostajaš zvest svojim vrednotam in deluješ skladno z njimi. To je proces, ki zahteva samorefleksijo in pripravljenost na učenje.</p>
<p>Vsakič, ko se odločiš nastopiti brez maske in v dialogu prisluhniti resnično, narediš korak k avtentičnemu vodenju. In prav ti majhni koraki ustvarjajo spremembe v tvojem timu in v tvojem načinu vodenja.</p>

<p class="pullquote">Avtentično vodenje je vabilo k stiku – s seboj in z drugimi.</p>

<p>Je izbira, da vodiš ne le z znanjem, ampak tudi z iskrenostjo in prisotnostjo.</p>

<div class="cta-final">
<p>👉 <strong>Če želiš raziskati</strong>, kako lahko razvijaš svoj avtentični slog vodenja v varnem in reflektivnem prostoru, me kontaktiraj. Skupaj bova pogledala, kako tvoje vrednote lahko postanejo temelj navdihujočega vodenja.</p>
</div>
"""
    render_blog_post(
        "avtenticno-vodenje-moc-resnicnega-stika",
        "Avtentično vodenje: Moč resničnega stika",
        "Avtentično vodenje ne temelji na popolnosti, temveč na iskrenosti in povezanosti. Preberi, kako lahko kot vodja navdihuješ s svojo avtentičnostjo.",
        "blog-avtenticno.webp",
        body,
    )


def page_blog_notranji():
    body = """<p>V vsakem izmed nas obstaja glas, ki nas opozarja, kritizira ali zadržuje. Pogosto mu rečemo <strong>notranji kritik</strong>. Njegove besede so lahko ostre:</p>
<blockquote>“Nisi dovolj dober/a. Kaj pa, če ti ne uspe? Ne izpostavljaj se.”</blockquote>
<p>Ta glas nas lahko upočasni, zmanjša naš pogum in nam prepreči, da bi naredili korak naprej.</p>
<p>Toda notranji kritik ni vedno naš sovražnik. Pogosto je del nas, ki skuša – na svoj neroden način – poskrbeti za našo varnost. Nastal je v preteklosti, ko smo se učili, da je bolje biti previden, se umakniti ali se ne izpostavljati, kot pa tvegati bolečino in zavrnitev.</p>

<h2>Prepoznati glas kritika</h2>
<p>Prvi korak je, da ločimo sebe od kritika. Notranji kritik je del nas, a ni naše bistvo. Ko ga prepoznamo, lahko opazimo njegove besede kot nekaj, kar se dogaja znotraj nas – ne pa kot resnico o tem, kdo smo.</p>

<ul>
  <li>Kateri stavek moj notranji kritik najpogosteje ponavlja?</li>
  <li>V katerih situacijah se njegov glas najglasneje oglasi?</li>
  <li>Kako bi zvenel moj notranji dialog, če bi bil prijaznejši?</li>
</ul>

<p>Namesto da se z notranjim kritikom borimo, ga lahko povabimo v dialog. Lahko ga vprašamo:</p>
<blockquote>“Kaj želiš s tem doseči? Pred čim me želiš obvarovati?”</blockquote>
<p>Presenečeni bomo, ko ugotovimo, da pogosto želi samo, da ne bi doživeli neuspeha, zavrnitve ali sramu.</p>
<p>S tem ko mu damo glas, se začne njegov ton mehčati. Kritična sporočila se lahko počasi preoblikujejo v opozorila, ki nam pomagajo bolj zavestno sprejemati odločitve. In tam, kjer nas je prej ustavljal, nas lahko začne usmerjati.</p>

<h2>Pot k notranjemu zavezniku</h2>
<p>Notranji kritik ne bo nikoli povsem izginil – in to tudi ni njegov namen. Lahko pa postane drugačen: iz ostrega sodnika se spremeni v notranji kompas, ki nas opozarja, kje potrebujemo več zaupanja vase.</p>
<p class="pullquote">Vsakič, ko mu prisluhnemo z nežnostjo in brez sodbe, naredimo korak k temu, da ga preoblikujemo v zaveznika.</p>

<p>Notranji kritik je lahko ovira, a tudi priložnost. Ko se naučimo opazovati in razumeti njegov glas, ne izgubljamo več energije za boj proti njemu. Namesto tega lahko ustvarimo notranji dialog, ki nas podpira pri rasti.</p>

<div class="cta-final">
<p>👉 <strong>Če želiš raziskati</strong> svoj odnos z notranjim kritikom in ga spremeniti v vir notranje moči, me kontaktiraj – skupaj lahko ustvariva varen prostor, kjer boš odkril/a, kako v njegovem glasu prepoznati priložnost.</p>
</div>
"""
    render_blog_post(
        "notranji-kritik-kako-ga-prepoznati-in-spremeniti-v-zaveznika",
        "Notranji kritik: Kako ga prepoznati in spremeniti v zaveznika",
        "Notranji kritik pogosto ovira našo rast, a lahko postane vir učenja. Preberi, kako ga prepoznati in ga preoblikovati v notranjega zaveznika.",
        "blog-notranji.webp",
        body,
    )


def page_blog_odpornost():
    body = """<h2>Odpornost ni togost, temveč gibljivost</h2>
<p>Ko slišimo besedo <strong>odpornost</strong>, si pogosto predstavljamo trdnost – nekoga, ki se ne zlomi in ostane neomajen ne glede na okoliščine. A v resnici odpornost ni togost, ampak prožnost. Gre za sposobnost, da se upognemo, ko je treba, in se nato znova poravnamo. Tako kot drevo, ki se pod težo vetra skloni, a se ne zlomi.</p>
<p>Odpornost je torej gibljivost življenja – da se znamo vračati k sebi tudi takrat, ko nas zunanje okoliščine izzovejo.</p>

<p>Odpornost ni le lastnost uma. Je nekaj, kar prežema vse naše bitje:</p>
<ul>
  <li><strong>Telo:</strong> Ko smo spočiti, negujemo svoje zdravje in poslušamo signale telesa, lažje zdržimo obremenitve.</li>
  <li><strong>Čustva:</strong> Ko si dovolimo čutiti, namesto da čustva potiskamo stran, ustvarjamo prostor za iskreno izkušnjo in predelavo.</li>
  <li><strong>Misli:</strong> Ko opazujemo svoj notranji dialog in ga oblikujemo v bolj sočutnega, krepimo notranjo stabilnost.</li>
  <li><strong>Odnosi:</strong> Ko smo povezani z ljudmi, ki nas podpirajo, lažje nosimo izzive in v njih najdemo smisel.</li>
</ul>
<p>Vsak izmed teh stebrov deluje skupaj. Če zanemarimo enega, odpornost izgublja svojo celostno moč.</p>

<ul>
  <li>Kako se moje telo oglasi, ko sem pod stresom? Ali mu namenim dovolj počitka in nege?</li>
  <li>Kaj naredim s svojimi čustvi – jih izrazim ali jih zadržim v sebi?</li>
  <li>Kakšen je ton mojega notranjega dialoga? Bi ga želel/a slišati vsak dan od nekoga drugega?</li>
  <li>Kateri ljudje v mojem življenju me podpirajo in mi vračajo občutek moči?</li>
</ul>

<p>Gradnja odpornosti ni projekt, ki ga opravimo naenkrat. Je proces drobnih odločitev: da gremo spat nekoliko prej, da si dovolimo solze, da se sprehodimo na svežem zraku, da izrečemo prijazno besedo sebi ali drugim.</p>
<p>Vsak tak korak postane del notranjega tkiva, ki nas drži skupaj, ko pridejo izzivi.</p>

<p>Odpornost in prožnost sta dar, ki ju lahko razvijamo vsak dan. Nista končna točka, ampak način življenja, kjer se učimo vračati k sebi in živeti usklajeno s telesom, čustvi, mislimi in odnosi.</p>

<div class="cta-final">
<p>👉 <strong>Če želiš raziskati</strong>, kako lahko ti gradiš svojo notranjo odpornost na celosten način, me kontaktiraj – skupaj bova ustvarila varen prostor, kjer boš lahko odkril/a svojo moč in prožnost.</p>
</div>
"""
    render_blog_post(
        "odpornost-in-proznost-celostna-notranja-moc",
        "Odpornost in prožnost: Kako graditi notranjo moč celostno",
        "Odpornost ni le miselna trdnost – vključuje telo, čustva, misli in odnose. Preberi, kako lahko celostno gradiš notranjo moč in prožnost.",
        "blog-odpornost.webp",
        body,
    )


# ---------- CONTACT ----------
def page_contact():
    body = """<section class="sec sec--cream sec--tight">
  <div class="container">
    <div class="sec-head-center">
      <span class="kicker">KONTAKT</span>
      <h1>Tukaj sem za tvoja vprašanja.</h1>
      <p class="sec-intro">Te zanima individualni coaching, sodelovanje s podjetji ali bi se rada dogovorila za uvodni pogovor?</p>
      <p class="sec-intro">Piši mi in z veseljem ti odgovorim.</p>
      <p class="sec-intro"><a href="mailto:tea@teaknez.com">tea@teaknez.com</a></p>
    </div>
    <div class="contact-wrap">
      <div class="contact-card">
        <span class="kicker">POŠLJI SPOROČILO</span>
        <form class="contact-form" action="https://api.web3forms.com/submit" method="POST" data-web3forms>
          <input type="hidden" name="access_key" value="e78b399d-a62e-494f-b90b-519f4b7f7a48">
          <input type="hidden" name="subject" value="Novo sporočilo s teaknez.com">
          <input type="hidden" name="from_name" value="teaknez.com - kontaktni obrazec">
          <input type="checkbox" name="botcheck" style="display:none;" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="field">
            <label for="namen">Zanima me</label>
            <select id="namen" name="zanima_me" data-intent-select>
              <option value="Uvodni pogovor">Uvodni pogovor</option>
              <option value="Individualni coaching">Individualni coaching</option>
              <option value="Sodelovanje s podjetji">Sodelovanje s podjetji</option>
              <option value="Drugo">Drugo</option>
            </select>
          </div>
          <div class="field">
            <label for="name">Ime in priimek</label>
            <input id="name" name="name" type="text" required autocomplete="name">
          </div>
          <div class="field">
            <label for="email">E-naslov</label>
            <input id="email" name="email" type="email" required autocomplete="email">
          </div>
          <div class="field">
            <label for="message">Sporočilo</label>
            <textarea id="message" name="message"></textarea>
          </div>
          <label class="field-check">
            <input type="checkbox" name="consent" required>
            <span>Seznanjena sem s <a href="politika-zasebnosti.html">politiko zasebnosti</a>.</span>
          </label>
          <div class="h-captcha" data-sitekey="50b2fe65-b00b-4b9e-ad62-3ba471098be2"></div>
          <button type="submit" class="btn btn-primary">Pošlji sporočilo</button>
          <div class="form-status" role="status" aria-live="polite"></div>
        </form>
        <script src="https://js.hcaptcha.com/1/api.js" async defer></script>
      </div>
    </div>
  </div>
</section>
""" + newsletter_section(0)

    page = head(
        "Kontakt - Tea Knez",
        "Te zanima individualni coaching, sodelovanje s podjetji ali uvodni pogovor? Piši mi na tea@teaknez.com in z veseljem ti odgovorim.",
        f"{SITE_URL}/kontakt.html", 0,
        og_image="tea-blazer.webp", og_image_alt="Kontakt - Tea Knez",
        extra_jsonld=[
            {
                "@type": "ContactPage",
                "@id": f"{SITE_URL}/kontakt.html#contactpage",
                "url": f"{SITE_URL}/kontakt.html",
                "name": "Kontakt - Tea Knez",
                "inLanguage": "sl",
                "about": {"@id": f"{SITE_URL}/#organization"},
            },
            _breadcrumb_jsonld([("Domov", f"{SITE_URL}/"), ("Kontakt", f"{SITE_URL}/kontakt.html")]),
        ]
    ) + header("contact", 0) + body + footer(0)
    write("kontakt.html", page)


# ---------- LEGAL ----------
def page_privacy():
    body = """<section class="page-header">
  <div class="container">
    <span class="eyebrow">Pravno</span>
    <h1>Politika zasebnosti</h1>
  </div>
</section>

<section class="legal">
<p>Ta politika zasebnosti določa, kako podjetje <strong>Integra, Tea Knez s.p.</strong> zbira, uporablja in varuje osebne podatke uporabnikov spletne strani <a href="https://www.teaknez.com">www.teaknez.com</a>.</p>
<p>Pri obdelavi osebnih podatkov ravnamo v skladu z <strong>Uredbo (EU) 2016/679</strong> Evropskega parlamenta in Sveta z dne 27. aprila 2016 (GDPR), <strong>Zakonom o varstvu osebnih podatkov (ZVOP-2)</strong> ter <strong>Zakonom o elektronskih komunikacijah (ZEKom-2)</strong>. Podjetje spoštuje zasebnost posameznikov in osebne podatke obdeluje zakonito, pošteno in pregledno.</p>

<h2>1. Podatki o upravljavcu</h2>
<p>Upravljavec osebnih podatkov: Tea Knez s.p., Trg komandanta Staneta 8, 1000 Ljubljana, Slovenija<br>
E-pošta: <a href="mailto:tea.knezz@gmail.com">tea.knezz@gmail.com</a><br>
Davčna številka: SI89887662<br>
Zavezanec za DDV: da</p>

<h2>2. Namen zbiranja osebnih podatkov</h2>
<p>Osebne podatke zbiramo in obdelujemo izključno z namenom zagotavljanja delovanja spletne strani in komuniciranja z uporabniki. To vključuje:</p>
<ul>
  <li>odgovore na vprašanja, poslana preko kontaktnega obrazca ali e-pošte,</li>
  <li>izvajanje dogovorjenih storitev coachinga,</li>
  <li>obveščanje o novih vsebinah ali dogodkih (le z vašo izrecno privolitvijo),</li>
  <li>zagotavljanje pravilnega delovanja spletnega mesta in uporabniške izkušnje.</li>
</ul>

<h2>3. Vrste osebnih podatkov</h2>
<p>Upravljavec lahko obdeluje naslednje podatke:</p>
<ul>
  <li>ime in priimek,</li>
  <li>elektronski naslov,</li>
  <li>telefonska številka,</li>
  <li>vsebina sporočila v obrazcu ali e-pošti,</li>
  <li>tehnični podatki (npr. IP-naslov, vrsta brskalnika, čas dostopa – preko piškotkov).</li>
</ul>

<h2>4. Pravna podlaga za obdelavo</h2>
<p>Podatke obdelujemo na naslednjih pravnih podlagah (v skladu s 6. členom GDPR):</p>
<ul>
  <li><strong>osebna privolitev</strong> (npr. ob pošiljanju sporočila ali prijavi na novice),</li>
  <li><strong>pogodbeni odnos</strong> (za izvedbo dogovorjene storitve),</li>
  <li><strong>zakonska obveznost</strong> (npr. izdaja računov),</li>
  <li><strong>zakoniti interes</strong> (varnost, preprečevanje zlorab, izboljšava uporabniške izkušnje).</li>
</ul>

<h2>5. Hramba osebnih podatkov</h2>
<p>Podatke hranimo le toliko časa, kolikor je potrebno za dosego namena, zaradi katerega so bili zbrani, oziroma v skladu z zakonskimi zahtevami.</p>
<ul>
  <li>Podatki, pridobljeni na podlagi privolitve, se hranijo do preklica.</li>
  <li>Računi in podatki, povezani s storitvami, se hranijo 10 let (v skladu z davčno zakonodajo).</li>
  <li>Po izteku obdobja hrambe se podatki varno izbrišejo ali anonimizirajo.</li>
</ul>

<h2>6. Pogodbeni obdelovalci in prenos podatkov</h2>
<p>V določenih primerih lahko obdelavo osebnih podatkov zaupamo zunanjim izvajalcem (npr. ponudnikom spletnega gostovanja, vzdrževanja spletne strani, računovodskim servisom). Z njimi imamo sklenjene pogodbe o obdelavi osebnih podatkov, skladne z zahtevami GDPR. Podatkov ne posredujemo tretjim osebam ali izven EU, razen če to zahteva zakon.</p>

<h2>7. Piškotki</h2>
<p>Spletna stran uporablja piškotke (cookies) za zagotavljanje osnovnega delovanja in izboljšanje uporabniške izkušnje. Uporabljajo se lahko naslednje vrste piškotkov:</p>
<ul>
  <li><strong>Nujni piškotki:</strong> potrebni za osnovno delovanje strani,</li>
  <li><strong>Analitični piškotki:</strong> za spremljanje obiska in izboljšanje vsebine,</li>
  <li><strong>Marketinški piškotki:</strong> uporabljajo se le ob vaši izrecni privolitvi.</li>
</ul>
<p>Uporabnik lahko kadarkoli spremeni nastavitve piškotkov ali jih izbriše v svojem brskalniku. Več v <a href="piskotki.html">politiki piškotkov</a>.</p>

<h2>8. Vaše pravice</h2>
<p>V skladu z zakonodajo imate pravico do:</p>
<ul>
  <li>dostopa do svojih osebnih podatkov,</li>
  <li>popravka netočnih podatkov,</li>
  <li>izbrisa (“pravica do pozabe”),</li>
  <li>omejitve obdelave,</li>
  <li>prenosljivosti podatkov,</li>
  <li>ugovora obdelavi,</li>
  <li>preklica privolitve za obdelavo.</li>
</ul>
<p>Zahtevo za uveljavljanje pravic lahko pošljete na e-naslov: <a href="mailto:tea@teaknez.com">tea@teaknez.com</a>. Na zahteve bomo odgovorili najpozneje v roku 30 dni.</p>
<p>Če menite, da so bile vaše pravice kršene, se lahko pritožite pri <strong>Informacijskem pooblaščencu RS</strong>: Informacijski pooblaščenec, Zaloška cesta 59, 1000 Ljubljana, e-pošta: <a href="mailto:gp.ip@ip-rs.si">gp.ip@ip-rs.si</a>.</p>

<h2>9. Varnost podatkov</h2>
<p>Uporabljamo ustrezne tehnične in organizacijske ukrepe za zaščito osebnih podatkov pred izgubo, zlorabo ali nepooblaščenim dostopom.</p>

<h2>10. Spremembe politike zasebnosti</h2>
<p>Politika zasebnosti se lahko občasno posodobi, da bo usklajena z zakonodajo ali spremembami v poslovanju. Veljavna različica je vedno objavljena na spletni strani <a href="https://www.teaknez.com">www.teaknez.com</a>.</p>

<p class="legal-meta">📅 Veljavnost: od 1. 1. 2026<br>© Tea Knez s.p. – vsi podatki so varovani.</p>
</section>
"""
    page = head(
        "Politika zasebnosti – Tea Knez",
        "Politika zasebnosti spletne strani teaknez.com v skladu z GDPR in slovensko zakonodajo.",
        f"{SITE_URL}/politika-zasebnosti.html", 0,
        extra_jsonld=_breadcrumb_jsonld([("Domov", f"{SITE_URL}/"), ("Politika zasebnosti", f"{SITE_URL}/politika-zasebnosti.html")])
    ) + header("", 0) + body + footer(0)
    write("politika-zasebnosti.html", page)


def page_cookies():
    body = """<section class="page-header">
  <div class="container">
    <span class="eyebrow">Pravno</span>
    <h1>Politika piškotkov</h1>
  </div>
</section>

<section class="legal">
<p>Spletna stran <a href="https://www.teaknez.com">www.teaknez.com</a>, katere upravljalec je <strong>Integra, Tea Knez s.p.</strong>, za svoje pravilno delovanje uporablja t. i. <strong>piškotke</strong> (ang. <em>cookies</em>). Piškotki so majhne datoteke, ki se shranijo na vašo napravo, ko obiščete spletno stran. Omogočajo prepoznavo vaše naprave, prilagajanje vsebine in izboljšanje uporabniške izkušnje.</p>

<h2>Vrste piškotkov, ki jih uporabljamo</h2>

<h2>1. Nujno potrebni piškotki</h2>
<p>Ti piškotki so potrebni za osnovno delovanje spletnega mesta in jih ni mogoče onemogočiti. Uporabljajo se npr. za:</p>
<ul>
  <li>pomnjenje nastavitev o soglasju za piškotke,</li>
  <li>pravilno prikazovanje strani,</li>
  <li>delovanje obrazcev.</li>
</ul>

<h2>2. Analitični piškotki</h2>
<p>Ti piškotki nam pomagajo razumeti, kako uporabniki uporabljajo spletno stran, da jo lahko izboljšujemo. Zbirajo anonimne podatke o obiskih (npr. število obiskovalcev, najpogosteje obiskane strani ipd.). Uporabljajo se samo, če z njimi izrecno soglašate.</p>

<h2>3. Funkcionalni piškotki</h2>
<p>Omogočajo, da si stran zapomni vaše izbire (npr. jezik, regijo ali nastavitve prikaza), in tako izboljša uporabniško izkušnjo.</p>

<h2>4. Marketinški piškotki</h2>
<p>Uporabljajo se za prikazovanje vsebin, ki so relevantne za uporabnika, in za analizo uspešnosti oglaševanja. Nameščajo se le, če jih izrecno dovolite.</p>

<h2>Upravljanje soglasja za piškotke</h2>
<p>Pri prvem obisku strani se prikaže obvestilo o piškotkih, kjer lahko izberete, katere vrste piškotkov dovoljujete. Soglasje lahko kadarkoli spremenite ali prekličete v nastavitvah brskalnika ali prek gumba <strong>“Nastavitve piškotkov”</strong>, ki je dostopen na dnu spletne strani.</p>
<p>Če piškotkov ne sprejmete, bo spletna stran še vedno delovala, vendar nekatere funkcije morda ne bodo optimalne.</p>

<h2>Piškotki tretjih oseb</h2>
<p>Na spletni strani se lahko uporabljajo tudi piškotki zunanjih storitev, kot so:</p>
<ul>
  <li><strong>Google Analytics</strong> (analitika obiskov),</li>
  <li><strong>Meta Pixel</strong> (Facebook oglaševanje, če je omogočeno).</li>
</ul>
<p>Te storitve imajo lastne politike zasebnosti, s katerimi se lahko seznanite na spletnih straneh ponudnikov: <a href="https://policies.google.com/privacy">Google – zasebnost in pogoji</a>, <a href="https://www.facebook.com/policy.php">Meta (Facebook) – politika zasebnosti</a>.</p>

<h2>Hramba piškotkov</h2>
<p>Piškotki se hranijo toliko časa, kolikor je potrebno za dosego namena, zaradi katerega so bili nameščeni:</p>
<ul>
  <li>sejni piškotki: do zaprtja brskalnika,</li>
  <li>trajni piškotki: največ 12 mesecev.</li>
</ul>

<h2>Vaše pravice</h2>
<p>V skladu z veljavno zakonodajo imate pravico, da kadar koli zahtevate dostop, popravek, izbris ali omejitev obdelave osebnih podatkov, pridobljenih s piškotki. Zahtevo lahko pošljete na e-naslov <a href="mailto:tea@teaknez.com">tea@teaknez.com</a>.</p>

<p class="legal-meta">Upravljavec spletne strani: Tea Knez s.p.<br>📅 Veljavnost politike piškotkov: od 1. 1. 2026<br>© Tea Knez s.p. – vsi podatki so varovani.</p>
</section>
"""
    page = head(
        "Politika piškotkov – Tea Knez",
        "Politika piškotkov spletne strani teaknez.com – kateri piškotki se uporabljajo in kako jih lahko upravljate.",
        f"{SITE_URL}/piskotki.html", 0,
        extra_jsonld=_breadcrumb_jsonld([("Domov", f"{SITE_URL}/"), ("Politika piškotkov", f"{SITE_URL}/piskotki.html")])
    ) + header("", 0) + body + footer(0)
    write("piskotki.html", page)


# ---------- STANDALONE LANDING PAGE ----------
def page_podpora_vracanju():
    body = """<section class="page-header page-header--landing">
  <div class="container">
    <div class="page-header-intro">
      <span class="eyebrow">Coaching</span>
      <h1>Reintegracijski coaching za zaposlene <em>po porodniškem dopustu</em></h1>
      <span class="page-header-rule" aria-hidden="true"></span>
      <p class="lead">Podpiram organizacije in zaposlene pri ustvarjanju bolj samozavestnega, podprtega in trajnostnega prehoda nazaj v delovno okolje po porodniškem dopustu.</p>
      <button type="button" class="btn btn-primary page-header-cta" data-open-modal="contact-modal">Dogovorimo se za uvodni pogovor</button>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="prose-narrow prose-narrow--center">
      <span class="eyebrow">Prehod</span>
      <h2>Vračanje po porodniškem dopustu <em>ni administrativen proces</em></h2>
      <p>Zaposlene se po porodniškem dopustu pogosto vračajo s spremenjeno identiteto, drugačnimi prioritetami in novimi pričakovanji do dela. Notranje doživljanje prehoda vpliva na samozavest, fokus, energijo - ter na občutek pripadnosti delovnemu okolju.</p>
      <p>Praktični izzivi se prepletajo s čustvenimi: usklajevanje novih osebnih in profesionalnih vlog, postavljanje meja, ponovno opredeljevanje svojega prispevka. Navzven zaposlene morda delujejo "nazaj v rutini", notranje pa še vedno potekajo pomembne spremembe.</p>
      <p>Način, kako organizacija podpre zaposleno v tem obdobju, neposredno vpliva na njeno dobro počutje, zavzetost in <strong>dolgoročno zadržanje kadra</strong>.</p>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="prose-narrow prose-narrow--center">
      <span class="eyebrow">Pristop</span>
      <h2>Zakaj <em>coaching</em>?</h2>
      <p>Vsako vračanje na delo je drugačno. Ne obstaja univerzalna rešitev, ki bi delovala za vsako zaposleno ali vsako organizacijo.</p>
      <p>Coaching ustvari prostor, kjer lahko zaposlena sama razišče, kar v tem trenutku najbolj potrebuje - prioritete, identitetne spremembe, samozavest, komunikacijo, postavljanje meja, odločitve, ki ji omogočijo trajnostno reintegracijo.</p>
      <p>Kot coachinja, certificirana po standardih <strong>ICF</strong>, ne ponujam vnaprej določenih modulov ali odgovorov. Vsak coaching proces sledi <strong>potrebam, ciljem in izzivom posameznice</strong>.</p>
      <p>Coaching deluje, ker zaposlena sama prepozna svoje vire, vzorce in najboljše odločitve zase. To je močnejši in trajnejši temelj za vrnitev v delovno okolje kot katerikoli zunanji nasvet ali generičen trening.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Sodelovanje</span>
      <h2>Trije <em>načini sodelovanja</em></h2>
      <p>Pristop prilagodim potrebam organizacije in posamezne zaposlene.</p>
    </div>
    <div class="offerings-stack">
      <article class="offering-block">
        <span class="offering-label">Signature specializacija</span>
        <h3>Reintegracijski coaching za zaposlene</h3>
        <p class="offering-sub">Individualna coaching podpora po porodniškem dopustu</p>
        <p>Coaching podpora zaposlenim, ki se po porodniškem dopustu vračajo na delo. Naslavlja prehod celostno - od identitetnih sprememb in samozavesti do trajnostnega usklajevanja novih življenjskih in poklicnih vlog.</p>
        <div class="offering-benefits">
          <div>
            <span class="offering-benefit-tag">Za zaposleno</span>
            <p>Več samozavesti, jasnosti in stabilnejši prehod nazaj v delovno okolje.</p>
          </div>
          <div>
            <span class="offering-benefit-tag">Za organizacijo</span>
            <p>Bolj uspešna reintegracija, večja zavzetost in večja možnost zadržanja kadra.</p>
          </div>
        </div>
        <p class="offering-note">Coaching proces sledi potrebam, ciljem in izzivom posameznice - ne vnaprej določenemu kurikulumu.</p>
      </article>

      <article class="offering-block">
        <span class="offering-label">Skupinska podpora</span>
        <h3>Seminar za vodje in HR</h3>
        <p class="offering-sub">Kako podpreti zaposleno ob vračanju po porodniškem dopustu - 2-urni interaktivni seminar</p>
        <p>Vodjem in HR strokovnjakom ponuja praktičen okvir za bolj podporno vodenje zaposlenih v prehodnem obdobju. Skupaj raziščemo dinamiko vračanja, najpogostejše izzive in konkretne pristope k komunikaciji in podpori - od check-in pogovorov do postavljanja realističnih pričakovanj.</p>
      </article>

      <article class="offering-block">
        <span class="offering-label">Profesionalna podpora</span>
        <h3>Coaching za zaposlene</h3>
        <p class="offering-sub">Individualni coaching onkraj reintegracije</p>
        <p>Coaching za zaposlene in strokovnjake, ki želijo bolj zavestno navigirati svojo profesionalno pot. Najpogostejše teme: karierni razvoj, samozavest, komunikacija, prehodi v vodstvene vloge, postavljanje meja in usklajevanje profesionalne in osebne vloge.</p>
        <p class="offering-note">Coaching proces sledi potrebam in ciljem posameznika - ne vnaprej določenim temam.</p>
      </article>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Učinki</span>
      <h2>Kaj prinaša <em>sodelovanje</em></h2>
    </div>
    <div class="benefits-split">
      <div class="benefit-col">
        <span class="benefit-col-tag">Za zaposlene</span>
        <ul class="benefit-list">
          <li>več samozavesti</li>
          <li>več jasnosti</li>
          <li>bolj gladek prehod</li>
          <li>močnejša profesionalna identiteta</li>
        </ul>
      </div>
      <div class="benefit-col">
        <span class="benefit-col-tag">Za organizacije</span>
        <ul class="benefit-list">
          <li>močnejše zadržanje kadra</li>
          <li>večja zavzetost zaposlenih</li>
          <li>boljša izkušnja zaposlenih</li>
          <li>bolj uspešna reintegracija</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="cta-end cta-end--landing">
  <div class="container">
    <h2>Dogovorimo se za <em>uvodni pogovor</em></h2>
    <p class="cta-end-lead">Vsaka organizacija ima drugačne potrebe in kontekst. Uvodni pogovor je raziskovalen - skupaj prepoznava, katera oblika podpore bi vašim zaposlenim in vodjem najbolje služila.</p>
    <button type="button" class="btn btn-primary" data-open-modal="contact-modal">Dogovorimo se za uvodni pogovor</button>
  </div>
</section>"""

    body += "\n" + contact_modal(0, subject="Povpraševanje – reintegracijski coaching")
    page = head(
        "Reintegracijski coaching za zaposlene po porodniškem dopustu - Tea Knez",
        "Coaching za zaposlene ob vračanju po porodniškem dopustu in podpora organizacijam. Seminar za vodje in HR. Individualni coaching za zaposlene in strokovnjake.",
        f"{SITE_URL}/podpora-vracanju.html", 0,
        og_image="service-podjetja.webp", og_image_alt="Reintegracijski coaching po porodniškem dopustu",
        extra_jsonld=[
            {
                "@type": "Service",
                "@id": f"{SITE_URL}/podpora-vracanju.html#service",
                "name": "Reintegracijski coaching za zaposlene po porodniškem dopustu",
                "serviceType": "Reintegracijski coaching",
                "url": f"{SITE_URL}/podpora-vracanju.html",
                "provider": {"@id": f"{SITE_URL}/#organization"},
                "areaServed": {"@type": "Country", "name": "Slovenija"},
                "audience": {"@type": "Audience", "audienceType": "Organizacije, vodje, HR in zaposleni"},
            },
            _breadcrumb_jsonld([
                ("Domov", f"{SITE_URL}/"),
                ("Za podjetja", f"{SITE_URL}/za-podjetja.html"),
                ("Reintegracijski coaching", f"{SITE_URL}/podpora-vracanju.html"),
            ]),
        ]
    ) + header("services", 0) + body + footer(0)
    write("podpora-vracanju.html", page)




# ---------- Sitemap & robots ----------
def page_sitemap():
    today = datetime.now().strftime("%Y-%m-%d")
    # (path, changefreq, priority)
    entries = [
        ("/", "monthly", "1.0"),
        ("/za-posameznice.html", "monthly", "0.9"),
        ("/za-podjetja.html", "monthly", "0.9"),
        ("/podpora-vracanju.html", "monthly", "0.8"),
        ("/o-meni.html", "yearly", "0.8"),
        ("/blog/", "weekly", "0.7"),
        ("/kontakt.html", "yearly", "0.7"),
        ("/politika-zasebnosti.html", "yearly", "0.3"),
        ("/piskotki.html", "yearly", "0.3"),
    ] + [(f"/blog/{p['slug']}/", "yearly", "0.6") for p in POSTS]
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for path, changefreq, priority in entries:
        body += (
            "  <url>\n"
            f"    <loc>{SITE_URL}{path}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>\n"
        )
    body += "</urlset>\n"
    write("sitemap.xml", body)
    write("robots.txt",
          "User-agent: *\n"
          "Allow: /\n\n"
          f"Sitemap: {SITE_URL}/sitemap.xml\n")


def page_webmanifest():
    import json as _json
    manifest = {
        "name": "Tea Knez Coaching",
        "short_name": "Tea Knez",
        "description": "Coaching za ženske in organizacije.",
        "lang": "sl",
        "start_url": "/",
        "scope": "/",
        "display": "browser",
        "background_color": "#F7F3EE",
        "theme_color": "#F7F3EE",
        "icons": [
            {"src": "/assets/images/favicon.svg", "type": "image/svg+xml", "sizes": "any", "purpose": "any"}
        ],
    }
    write("site.webmanifest", _json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


# ---------- Build ----------
if __name__ == "__main__":
    page_index()
    page_about()
    page_za_posameznice()
    page_za_podjetja()
    page_blog_index()
    page_blog_slaba_vest()
    page_blog_zakaj_se_ne_znam_ustaviti()
    page_blog_cas_zase()
    page_blog_sem_samo_se_mama()
    page_blog_identiteta()
    page_blog_vracanje()
    page_blog_izgorelost()
    page_blog_sindrom()
    page_blog_mir()
    page_blog_samozavest()
    page_blog_avtenticno()
    page_blog_notranji()
    page_blog_odpornost()
    page_contact()
    page_privacy()
    page_cookies()
    page_podpora_vracanju()
    page_sitemap()
    page_webmanifest()
    print("\nBuild complete.")
