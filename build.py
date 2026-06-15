#!/usr/bin/env python3
"""Build static teaknez.com from extracted content."""
import os, re, html as ihtml
from datetime import datetime
from pathlib import Path

CURRENT_YEAR = datetime.now().year

SITE = Path(__file__).parent

# ---------- Shared fragments ----------
def head(title, description, canonical, depth=0):
    asset = "../" * depth + "assets"
    return f"""<!DOCTYPE html>
<html lang="sl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://www.teaknez.com{asset.replace('..', '').lstrip('/')}/images/hero.webp">
<link rel="icon" type="image/svg+xml" href="{asset}/images/favicon.svg">
<link rel="apple-touch-icon" href="{asset}/images/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset}/css/main.css">
</head>
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

    arrow = '<svg class="nav-cta-arrow" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 8h10"/><path d="M9 4l4 4-4 4"/></svg>'

    return f"""<a href="#main" class="skip-link">Preskoči na vsebino</a>
<header class="site-header">
  <div class="container">
    <a href="{p}index.html" class="site-logo" aria-label="Tea Knez Coaching - domov">
      <span>Tea Knez<small class="tag">Coaching</small></span>
    </a>
    <nav class="site-nav" id="site-nav" aria-label="Glavna navigacija">
      <ul class="nav-list">
        <li>{link("Domov", p + "index.html", "home")}</li>
        <li>{link("Za posameznice", p + "za-posameznice.html", "individuals")}</li>
        <li>{link("Za podjetja", p + "za-podjetja.html", "companies")}</li>
        <li>{link("Blog", p + "blog/", "blog")}</li>
        <li>{link("O meni", p + "o-meni.html", "about")}</li>
      </ul>
      <a href="{p}kontakt.html" class="nav-cta">Rezerviraj uvodno srečanje {arrow}</a>
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
        <p>Coaching za ženske in organizacije. Prostor za jasen razmislek, zrele odločitve in trajne spremembe.</p>
      </div>
      <div class="footer-col">
        <h4>Coaching</h4>
        <ul>
          <li><a href="{p}za-posameznice.html">Za posameznice</a></li>
          <li><a href="{p}za-podjetja.html">Za podjetja</a></li>
          <li><a href="{p}podpora-vracanju.html">Vračanje po porodniški</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Raziskuj</h4>
        <ul>
          <li><a href="{p}o-meni.html">O meni</a></li>
          <li><a href="{p}blog/">Blog</a></li>
          <li><a href="{p}kontakt.html">Kontakt</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Pravno</h4>
        <ul>
          <li><a href="{p}politika-zasebnosti.html">Politika zasebnosti</a></li>
          <li><a href="{p}piskotki.html">Politika piškotkov</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span data-current-year>{CURRENT_YEAR}</span> Integra, Tea Knez s.p.</span>
    </div>
  </div>
</footer>
<script src="{p}assets/js/main.js"></script>
</body>
</html>
"""

# Testimonials shared markup
TESTIMONIALS = [
    ("Vodenje lastnega podjetja je hitro postalo preveč razpršeno. S Teo sem začela razmišljati širše in z več jasnosti sprejemati podjetniške odločitve.",
     "Sara", "ustanoviteljica marketing studia"),
    ("Kot vodja ekipe sem bila pogosto ujeta med rezultate in ljudi. S coachingom sem postala mirnejša v zahtevnih situacijah in jasnejša v komunikaciji.",
     "Petra", "vodja ekipe v bančnem sektorju"),
    ("V poslu sem dolgo dvomila vase, čeprav sem bila strokovno samozavestna. Coaching mi je dal strateško jasnost in pogum za pomembne odločitve.",
     "Nina", "solo trenerka"),
    ("Navajena sem biti ves čas ‘vidna’, redko pa sem si dovolila prostor za razmislek. Naučila sem se postaviti jasnejše meje in začela ustvarjati z več notranjega miru.",
     "Maja", "influencerka"),
]

def testimonials_section():
    cards = "\n".join(
        f"""    <article class="testimonial">
      <blockquote>»{q}«</blockquote>
      <footer class="testimonial-author">
        <span class="testimonial-avatar" aria-hidden="true">{name[0]}</span>
        <cite><strong>{name}</strong><span>{role}</span></cite>
      </footer>
    </article>"""
        for q, name, role in TESTIMONIALS
    )
    return f"""<section class="section section-cream">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Zaupanje strank</span>
      <h2>Kaj pravijo stranke</h2>
      <p>Vsak pogovor prinese drugačno zgodbo - od večje jasnosti in samozavesti, do konkretnih premikov v življenju.</p>
    </div>
    <div class="testimonials">
{cards}
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
    body = """<section class="page-hero page-hero--home">
  <div class="container">
    <div class="page-hero-grid">
      <div class="page-hero-text">
        <h1>Več jasnosti.<br><em>Manj razpetosti.</em><br>Več tebe.</h1>
        <p class="hero-lead">Pomagam ženskam, ki usklajujejo materinstvo, kariero in življenjske odgovornosti, ustvariti več prostora za premišljene odločitve, jasne prioritete in tisto, kar je res pomembno.</p>
        <div class="dual-cta">
          <a href="za-posameznice.html" class="btn-outline">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"/><path d="M4 20c0-3.5 3.5-6 8-6s8 2.5 8 6"/></svg>
            <span>Sem posameznica</span>
          </a>
          <a href="za-podjetja.html" class="btn-outline">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 9h2M9 12h2M9 15h2M13 9h2M13 12h2M13 15h2"/></svg>
            <span>Sem podjetje</span>
          </a>
        </div>
        <ul class="trust-strip">
          <li>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4l2 5h5l-4 3 1.5 6L12 14l-4.5 4L9 12 5 9h5z"/></svg>
            <span>Več jasnosti</span>
          </li>
          <li>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 12h18"/><path d="M7 8l-4 4 4 4"/><path d="M17 8l4 4-4 4"/></svg>
            <span>Manj razpetosti</span>
          </li>
          <li>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/></svg>
            <span>Več tebe</span>
          </li>
          <li>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-12V4l-8-2-8 2v6c0 8 8 12 8 12z"/><path d="M9 11l2 2 4-4"/></svg>
            <span>Zrele odločitve</span>
          </li>
          <li>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2v20"/><path d="M5 9c1-3 4-5 7-5"/><path d="M19 9c-1-3-4-5-7-5"/><path d="M5 15c1 3 4 5 7 5"/><path d="M19 15c-1 3-4 5-7 5"/></svg>
            <span>Trajne spremembe</span>
          </li>
        </ul>
      </div>
      <div class="page-hero-image">
        <img src="assets/images/hero.webp" alt="Tea Knez - coaching" loading="eager">
      </div>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="reasons-split">
      <div class="reasons-split-text">
        <span class="eyebrow">Za obdobja, ko se veliko spreminja</span>
        <h2>Se prepoznaš v katerem od teh občutkov?</h2>
        <p>Ni treba, da vse nosiš sama. Včasih najbolj pomaga prostor, kjer lahko za trenutek odložiš vse vloge in prisluhneš sebi.</p>
      </div>
      <ul class="dotted-list">
        <li>si v obdobju sprememb in iščeš smer naprej</li>
        <li>usklajuješ materinstvo, kariero in življenjske odgovornosti</li>
        <li>želiš sprejemati odločitve, ki so res skladne s tabo</li>
        <li>čutiš, da je čas, da ponovno namenjaš prostor tudi sebi</li>
        <li>si želiš več miru, zaupanja vase in notranje trdnosti</li>
      </ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="outcomes-block">
      <h2>Kaj se spremeni?</h2>
      <p class="outcomes-block-lead">Ko imaš prostor za razmislek in podporo, se začnejo premikati tudi stvari, ki so prej stale na mestu.</p>
      <ul class="dotted-list">
        <li>odločitve sprejemaš z več zaupanja in manj dvoma</li>
        <li>lažje prepoznaš, kaj je v tem obdobju res pomembno</li>
        <li>jasneje postavljaš prioritete</li>
        <li>z več miru usklajuješ različne življenjske vloge</li>
        <li>ponovno najdeš čas s sabo in svojimi potrebami</li>
      </ul>
      <p class="outcomes-block-italic">Ne zato, ker bi dobila vse odgovore. Ampak zato, ker začneš bolj zaupati sebi.</p>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Moj pristop</span>
      <h2>Kako je delati z mano?</h2>
      <p>Vsaka ženska pride z drugačno zgodbo. Nekaj pa jim je skupno: iščejo prostor, kjer jim ni treba imeti vseh odgovorov.</p>
    </div>
    <div class="approach-cards">
      <article class="approach-card">
        <div class="approach-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M16 26c0-6 4-10 8-12"/><path d="M16 26c0-6-4-10-8-12"/><path d="M16 26V8"/><path d="M16 8c1-3 4-4 6-3"/><path d="M16 8c-1-3-4-4-6-3"/></svg>
        </div>
        <h3>Brez hitrih rešitev</h3>
        <p>Ne verjamem v univerzalne recepte. Verjamem v razmislek, ki je resnično za tebe, tvojo situacijo in obdobje, v katerem si.</p>
      </article>
      <article class="approach-card">
        <div class="approach-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14h12v6a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4v-6z"/><path d="M22 16h2a3 3 0 0 1 0 6h-2"/><path d="M14 9c1-2 3-2 4 0M18 9c1-2 3-2 4 0"/></svg>
        </div>
        <h3>Dovolj prostora za razmislek</h3>
        <p>V hitrem tempu življenja redko dobimo prostor, da si dovolimo razmislek. Coaching je prostor, kjer imaš nemoten čas zase. Razmislek pa je razlika med ponavljanjem in resničnim korakom naprej.</p>
      </article>
      <article class="approach-card">
        <div class="approach-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M16 27s-9-5.5-9-13a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 7.5-9 13-9 13z"/></svg>
        </div>
        <h3>Toplo. Neposredno. Iskreno.</h3>
        <p>Ob teh ne tipam. Sem ti na voljo s pravimi vprašanji in z empatijo. Hkrati pa te povabim k pogumnim odgovorom in k iskrenemu pogledu nase.</p>
      </article>
    </div>
  </div>
</section>
""" + testimonials_section() + """"""

    page = head(
        "Tea Knez - Coaching za ženske in podjetja",
        "Coaching za ženske, ki usklajujejo materinstvo, kariero in odgovornosti, ter podporo organizacijam pri prehodih zaposlenih. Več jasnosti. Manj razpetosti. Več tebe.",
        "https://www.teaknez.com/", 0
    ) + header("home", 0) + body + footer(0)
    write("index.html", page)


# ---------- ABOUT ----------
def page_about():
    body = """<section class="page-hero">
  <div class="container">
    <div class="page-hero-grid">
      <div class="page-hero-text">
        <span class="eyebrow">O meni</span>
        <h1>Pozdravljena, sem Tea.</h1>
        <p class="hero-italic">Coachinja, podjetnica, žena in mama.</p>
        <p>Verjamem, da imajo ženske vse vire v sebi, le včasih potrebujejo prostor, odgovornost svojega časa in pomoč konkretnih kompasov.</p>
        <p>Danes spremljam predvsem ženske v pomembnih življenjskih in kariernih prehodih — od vračanja s porodniške do usklajevanja materinstva, kariere in podjetništva.</p>
      </div>
      <div class="page-hero-image">
        <img src="assets/images/about-tea.webp" alt="Tea Knez">
      </div>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="about-story">
      <span class="eyebrow">Moja zgodba</span>
      <h2>Vsaka izkušnja me je nekaj <em>naučila</em>.</h2>
      <p>Moja pot ni začela s coachingom. Začela se je kot pravnica, mediatorka in nato razvila naprej — analitično in odločeno na izpostavah.</p>
      <p>Različna delovna področja so me naučila, kako pomembni so odnosi, razumevanje in sposobnost poslušati slišano druge.</p>
      <p>Kot vodja ekip sem skozi leta razvila tudi posebno občutljivost za prelome — trenutke, ko ljudi karierne in osebne odločitve počasi prikrivajo nove ravni odgovornosti.</p>
      <p>Danes svoje izkušnje in podjetniško izkušnjo vključim v coaching, kjer s tem podpiram ženske v pomembnih prehodih — z naravnim tempom, vključeno in iskreno odločnostjo.</p>
    </div>
    <div class="section-head section-head--center" style="margin-top: 72px;">
      <span class="eyebrow">Moj pristop</span>
      <h2>Coaching zame ni svetovanje. Je strukturiran proces razmisleka.</h2>
    </div>
    <div class="approach-cards">
      <article class="approach-card">
        <div class="approach-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="16" r="10"/><path d="M16 11v5l3 3"/></svg>
        </div>
        <h3>Ustavimo se</h3>
        <p>Z usmerjenimi vprašanji odprem prostor, kjer lahko slišiš lasten glas — namesto da te prehitevajo zunanji nasveti.</p>
      </article>
      <article class="approach-card">
        <div class="approach-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 24l6-12 4 8 4-6 6 10"/><path d="M3 28h26"/></svg>
        </div>
        <h3>Razložimo</h3>
        <p>Prepoznava vzorcev, vrednot in resničnih prioritet. Vidiš celotno sliko — od zunaj in znotraj.</p>
      </article>
      <article class="approach-card">
        <div class="approach-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 16l5 5L24 9"/></svg>
        </div>
        <h3>Določiti ti</h3>
        <p>Zaupaš si in delaš premišljene korake. Ker so naslednji koraki tvoji — ne moji.</p>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Izobrazba in akreditacije</span>
      <h2>Strokovna podpora. <em>Dokazana zavezanost kakovosti.</em></h2>
      <p>Coaching ni zgolj veščina — je profesija. Zato si nenehno izpopolnjujem znanje in zagotavljam, da delam v skladu s standardi ICF in EMCC.</p>
    </div>
    <div class="credentials-row">
      <ul class="credentials-bullets">
        <li>magistra prava</li>
        <li>certificirana organizacijska coachinja</li>
        <li>certificirana NLP mojstrica in coachinja</li>
        <li>strokovna izobraževanja s področja coachinga in komunikacije</li>
        <li>stalno strokovno izpopolnjevanje in supervizija</li>
        <li>članica European Mentoring &amp; Coaching Council (EMCC)</li>
        <li>članica International Coaching Federation (ICF)</li>
      </ul>
      <div class="credentials-badges">
        <div class="cred-badge">
          <div class="cred-badge-mark cred-badge-mark--emcc">
            <span class="cred-badge-mark-tag">EMCC</span>
            <small>European Mentoring &amp; Coaching Council</small>
          </div>
          <div class="cred-badge-text">
            <strong>EIA EMCC</strong>
            <span>Accredited Coach</span>
          </div>
        </div>
        <div class="cred-badge">
          <div class="cred-badge-mark cred-badge-mark--icf">
            <span class="cred-badge-mark-tag">ICF</span>
          </div>
          <div class="cred-badge-text">
            <strong>ACC ICF</strong>
            <span>Accredited Coach</span>
          </div>
        </div>
      </div>
    </div>
    <div class="section-head section-head--center" style="margin-top: 80px;">
      <span class="eyebrow">Vrednote, ki me vodijo</span>
    </div>
    <div class="value-strip">
      <article class="value-item">
        <div class="value-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="16" r="6"/><circle cx="16" cy="16" r="1.5" fill="currentColor"/><path d="M2 16c4-6 8-9 14-9s10 3 14 9c-4 6-8 9-14 9S6 22 2 16z"/></svg>
        </div>
        <h3>Prisotnost</h3>
        <p>V vsakem srečanju sem polno prisotna, polno zbrana in odprta za to, kar prinaša ta trenutek.</p>
      </article>
      <article class="value-item">
        <div class="value-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M16 26V12"/><path d="M16 12c-3 0-5 2-5 5"/><path d="M16 12c3 0 5 2 5 5"/><path d="M8 26h16"/></svg>
        </div>
        <h3>Rast</h3>
        <p>Verjamem, da nosimo v sebi resnico in moč. Jaz sem tu, da ti pomagam te dvignit na površje.</p>
      </article>
      <article class="value-item">
        <div class="value-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M16 27s-9-6-9-13a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 7-9 13-9 13z"/></svg>
        </div>
        <h3>Zaupanje</h3>
        <p>Coaching je zaupen prostor, kjer si lahko taka, kot si. Brez sodbe, brez pričakovanj, ki niso tvoja.</p>
      </article>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="closing-recognize">
      <div class="closing-recognize-text">
        <h2>Če si pri branju prepoznala sebe ...</h2>
        <p>Mogoče je čas, da si vzameš trenutek zase. Na brezplačnem uvodnem srečanju bova skupaj raziskali, kaj v tem trenutku najbolj iščeš in kako bi ti coaching lahko služil.</p>
        <a href="kontakt.html" class="btn btn-primary">Rezerviraj uvodno srečanje →</a>
      </div>
      <div class="closing-recognize-image">
        <img src="assets/images/coaching-section.webp" alt="">
      </div>
    </div>
  </div>
</section>"""

    page = head(
        "O meni - Tea Knez",
        "Sem Tea Knez, coachinja, mediatorka in podjetnica. Spoznaj moj pristop, vrednote in pot, ki vodi v ustvarjanje prostora za zrele odločitve.",
        "https://www.teaknez.com/o-meni", 0
    ) + header("about", 0) + body + footer(0)
    write("o-meni.html", page)



# ---------- ZA POSAMEZNICE ----------
def page_za_posameznice():
    body = """<section class="page-hero">
  <div class="container">
    <div class="page-hero-grid">
      <div class="page-hero-text">
        <span class="eyebrow">Coaching za ženske</span>
        <h1>Več jasnosti.<br><em>Manj razpetosti.</em><br>Več tebe.</h1>
        <p>Materinstvo, kariera, partnerstvo, podjetništvo, vsakodnevne obveznosti. V določenih obdobjih se lahko zgodi, da postane vsega preveč. Ne zato, ker ne bi zmogla. Temveč zato, ker nosiš veliko odgovornosti in ob tem pogosto zmanjka prostora za razmislek o tem, kaj potrebuješ ti.</p>
        <p>Coaching je prostor, kjer se za trenutek ustaviš. Prostor, kjer lahko razčlenjuješ svoje misli, odločitve in izzive brez pričakovanj, da moraš imeti vse odgovore.</p>
        <p>Skupaj ustvariva prostor za več jasnosti, zaupanja vase in odločitve, ki so skladne s tabo.</p>
      </div>
      <div class="page-hero-image">
        <img src="assets/images/about-tea.webp" alt="Tea Knez">
      </div>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Ko te kliče sprememba</span>
      <h2>Tukaj sem, da te podprem, ko ...</h2>
    </div>
    <ul class="dual-list">
      <li>usklajuješ materinstvo, kariero ali podjetništvo in se pogosto počutiš razpeto med različnimi vlogami</li>
      <li>se vračaš s porodniške in iščeš svoj način prehoda nazaj v delo</li>
      <li>si pred pomembno osebno ali karierno odločitvijo</li>
      <li>čutiš, da si se med vsemi odgovornostmi nekoliko izgubila</li>
      <li>želiš več zaupanja vase in manj notranjega dvoma</li>
      <li>si želiš prostor za iskren razmislek in podporo</li>
    </ul>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Kaj lahko pričakuješ?</span>
      <h2>Prostor za jasnost, podporo in rast</h2>
    </div>
    <div class="duo-split">
      <div class="duo-col">
        <span class="duo-eyebrow">Moj pristop</span>
        <p>Coaching ni svetovanje in ni terapija. Je strukturiran, zaupen proces, kjer s pravimi vprašanji odpirava prostor za razmislek, ki ga v vsakdanu morda nimaš. V kombinaciji refleksije, usmerjenih vprašanj in konkretnih korakov bova raziskovali tisto, kar je trenutno najbolj pomembno zate.</p>
      </div>
      <div class="duo-col">
        <span class="duo-eyebrow">Kako delujeva skupaj</span>
        <p>Coaching proces izhaja iz tvoje izkušnje. Skozi pogovor ti pomagam slišati lasten glas, prepoznati notranje vzorce in postaviti korake, ki so smiselni zate. Vsako srečanje se prilagaja tvojemu ritmu in cilju — ni vnaprej določene poti.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Kaj ti coaching prinese</span>
      <h2>Spremembe, ki jih začutiš v <em>vsakdanjem življenju</em></h2>
    </div>
    <div class="outcome-grid">
      <article class="outcome-card">
        <span class="outcome-tag">Več jasnosti</span>
        <p>Lažje prepoznaš, kaj v tem obdobju res šteje, in kaj lahko za zdaj odložiš.</p>
      </article>
      <article class="outcome-card">
        <span class="outcome-tag">Močnejše zaupanje vase</span>
        <p>Bolj verjameš svojim odločitvam in ne potrebuješ zunanje potrditve, da si v redu.</p>
      </article>
      <article class="outcome-card">
        <span class="outcome-tag">Jasne prioritete</span>
        <p>Veš, kam usmerjati svojo energijo in kateri koraki te vodijo naprej.</p>
      </article>
      <article class="outcome-card">
        <span class="outcome-tag">Zdrave meje</span>
        <p>Lažje rečeš ne, kar ti ne služi, in da, kar ti je pomembno.</p>
      </article>
      <article class="outcome-card">
        <span class="outcome-tag">Več notranjega miru</span>
        <p>Ob izzivih ohraniš stik s sabo in odločitve sprejemaš iz mirnejšega prostora.</p>
      </article>
      <article class="outcome-card">
        <span class="outcome-tag">Občutek, da nisi sama</span>
        <p>V coachingu imaš zaupen prostor, kjer lahko misliš na glas in si slišana.</p>
      </article>
    </div>
    <p class="closing-italic">Ne zato, ker bi kdorkoli drug vedel namesto tebe. Ampak zato, ker se končno slišiš v skladu s sabo.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="cta-pair">
      <div class="cta-pair-info">
        <h3>Individualni coaching</h3>
        <ul class="tick-list">
          <li>60-minutna srečanja</li>
          <li>Online ali v živo</li>
          <li>Prilagojeno tvojemu ritmu in cilju</li>
        </ul>
      </div>
      <div class="cta-pair-action">
        <h3>Rezerviraj uvodni pogovor</h3>
        <p>Na brezplačnem spoznavnem klicu bova raziskali, kaj te trenutno najbolj zaposluje, kakšno podporo iščeš in ali je coaching prava izbira zate.</p>
        <a href="kontakt.html" class="btn btn-primary">Rezerviraj uvodno srečanje →</a>
      </div>
    </div>
  </div>
</section>"""

    page = head(
        "Coaching za posameznice - Tea Knez",
        "Coaching za ženske, ki usklajujejo materinstvo, kariero in podjetništvo. Prostor za jasnost, zaupanje vase in odločitve, skladne s sabo.",
        "https://www.teaknez.com/za-posameznice.html", 0
    ) + header("individuals", 0) + body + footer(0)
    write("za-posameznice.html", page)


# ---------- ZA PODJETJA ----------
def page_za_podjetja():
    body = """<section class="page-hero">
  <div class="container">
    <div class="page-hero-grid">
      <div class="page-hero-text">
        <span class="eyebrow">Storitve za podjetja</span>
        <h1>Podprite zaposlene ob <em>vračanju na delo</em> in drugih pomembnih prehodih</h1>
        <p>Organizacije danes vse več pozornosti namenjajo razvoju zaposlenih, zavzetosti in dobremu počutju. Kljub temu pa so prav obdobja velikih sprememb pogosto tista, v katerih zaposleni potrebujejo največ podpore.</p>
        <p>Že zaposlenega je za podjetje veliko, prilagajanje in ohranja stik s tem, kar ji omogoča dolgoročno uspeh.</p>
        <p>Coaching ni vnaprej določen, ki bi predpisoval, kar je za zaposlene podporo v ključnih prehodnih obdobjih. Je prepoznavanje individualnih potreb in oblikovanje podpore, ki res deluje.</p>
        <p>Sem podjetjem, ki želijo s strokovnostjo in z dolgoročno podporo ustvariti prostor za bolj samozavesten, podprt in uspešen prehod — za zaposlene, vodje in celotno organizacijo.</p>
      </div>
      <div class="page-hero-image">
        <img src="assets/images/service-podjetja.webp" alt="Coaching za podjetja">
      </div>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Kako lahko sodelujemo?</span>
      <h2>Dve poti podpore za vaše <em>zaposlene in vodje</em></h2>
      <p>Coaching in delavnica se dopolnjujeta in jih je mogoče izvajati skupaj, s katerim se zaposlenim podpora podpora, vodjam pa samozavestno pri svoji vlogi.</p>
    </div>
    <div class="duo-card-grid">
      <article class="duo-card">
        <span class="duo-card-eyebrow">Coaching za zaposlene</span>
        <h3>Coaching za zaposlene <em>ob vračanju s porodniške</em></h3>
        <p>Vračanje s porodniške ne pomeni le organizacijskih sprememb. Je tudi notranji prehod, ki vpliva na samozavest, prioritete in identiteto.</p>
        <p class="duo-card-sub">Podpora pri:</p>
        <ul class="tick-list two-col">
          <li>vračanju na delo po porodniški</li>
          <li>komunikaciji z vodjo in sodelavci</li>
          <li>postavljanju mej</li>
          <li>karierni rasti</li>
          <li>usklajevanju delovnih in družinskih obveznosti</li>
          <li>kariernem prehodu v novo vlogo</li>
        </ul>
        <p class="duo-card-note">Že in po uvodni VOD srečanju, kjer pogovorim pričakovanja, je coaching usmerjen v podporo zaposleni.</p>
      </article>
      <article class="duo-card">
        <span class="duo-card-eyebrow">Delavnica za vodje in HR</span>
        <h3>Delavnica za vodje in HR — <em>Kako podpreti zaposlene s porodniške</em></h3>
        <p>Vodje in HR strokovnjaki imajo ključno vlogo pri uspehu prehoda zaposlene nazaj v delovni proces. Delavnica vodjem ponudi praktične orodja in znanje za razumevanje dinamike in podpornih pristopov.</p>
        <p class="duo-card-sub">Teme delavnice:</p>
        <ul class="tick-list two-col">
          <li>kaj se pogosto spreminja po prihodu zaposlene</li>
          <li>učinkovita komunikacija pri vračanju</li>
          <li>postavitev pričakovanj in pogovorov</li>
          <li>usklajenje pričakovanj med poslom in zaposleno</li>
          <li>postavitev realističnih pričakovanj</li>
          <li>komunikacija o napredovanjih in razvoju</li>
        </ul>
        <p class="duo-card-note">Delavnica je vodjem priložnost za razvoj veščin, zaposleni pa boljši podporni prostor — za bolj uspešno reintegracijo in dolgoročno zadržanje kadra.</p>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="closing-cta">
      <div class="closing-cta-text">
        <h2>Skupaj ustvarimo okolje, v katerem ljudje uspevajo.</h2>
        <p>S pravim pristopom v obdobjih sprememb krepimo zavzetost, zaupanje in dolgoročno povezanost zaposlenih z organizacijo.</p>
      </div>
      <div class="closing-cta-action">
        <a href="kontakt.html" class="btn btn-primary">Pridobi ponudbo →</a>
      </div>
    </div>
  </div>
</section>"""

    page = head(
        "Coaching za podjetja - Tea Knez",
        "Coaching za zaposlene ob vračanju s porodniške in delavnica za vodje in HR. Strokovna podpora pri pomembnih prehodih za zaposlene in organizacijo.",
        "https://www.teaknez.com/za-podjetja.html", 0
    ) + header("companies", 0) + body + footer(0)
    write("za-podjetja.html", page)


# ---------- BLOG INDEX ----------
POSTS = [
    {"slug":"vracanje-s-porodniskega-dopusta", "title":"Vračanje s porodniškega dopusta: ko se vrneš drugačna",
     "summary":"Kako podpreti vračanje s porodniškega dopusta? O izzivih, prehodu in vlogi coachinga za posameznice in podjetja.",
     "image":"blog-vracanje.webp"},
    {"slug":"kako-preprečiti-izgorelost-v-podjetjih-kultura-ravnovesja-ne-žrtvovanja", "title":"Kako preprečiti izgorelost v podjetjih: kultura ravnovesja, ne žrtvovanja",
     "summary":"Kultura zaupanja in ravnovesja namesto preobremenjenosti. Ustvari delovno okolje, kjer ljudje resnično zmorejo rasti.",
     "image":"blog-izgorelost.webp"},
    {"slug":"kako-premagati-sindrom-vsiljivca-(imposter-syndrome)", "title":"Kako premagati sindrom vsiljivca (imposter syndrome)",
     "summary":"O dvomu vase, ki te želi zaščititi. Spoznaj, kako prepoznati ta glas in verjeti, da si že zdaj dovolj.",
     "image":"blog-sindrom.webp"},
    {"slug":"ko-mir-v-sebi-postane-pomembnejši-od-tega-da-imaš-prav", "title":"Ko mir v sebi postane pomembnejši od tega, da imaš prav",
     "summary":"O notranji svobodi, ko mir izbereš pred dokazovanjem. Nauči se slišati sebe, ne potrebe po potrditvi.",
     "image":"blog-mir.webp"},
    {"slug":"samozavest-ni-nekaj-kar-imas", "title":"Samozavest ni nekaj, kar imaš – ampak nekaj, kar gradiš",
     "summary":"Samozavest ni lastnost, s katero se rodiš – je pot, ki jo gradiš skozi drobne izbire in notranji dialog.",
     "image":"blog-samozavest.webp"},
    {"slug":"avtenticno-vodenje-moc-resnicnega-stika", "title":"Avtentično vodenje: Moč resničnega stika",
     "summary":"Avtentično vodenje ne temelji na popolnosti, temveč na iskrenosti in povezanosti. Kako voditi z resničnostjo.",
     "image":"blog-avtenticno.webp"},
    {"slug":"notranji-kritik-kako-ga-prepoznati-in-spremeniti-v-zaveznika", "title":"Notranji kritik: Kako ga prepoznati in spremeniti v zaveznika",
     "summary":"Notranji kritik pogosto ovira našo rast, a lahko postane vir učenja. Kako ga prepoznati in preoblikovati.",
     "image":"blog-notranji.webp"},
    {"slug":"odpornost-in-proznost-celostna-notranja-moc", "title":"Odpornost in prožnost: Kako graditi notranjo moč celostno",
     "summary":"Odpornost ni le miselna trdnost – vključuje telo, čustva, misli in odnose. Kako celostno graditi notranjo moč.",
     "image":"blog-odpornost.webp"},
]

def page_blog_index():
    cards = "\n".join(
        f"""      <a class="blog-card" href="{p['slug']}/">
        <div class="blog-card-image"><img src="../assets/images/{p['image']}" alt=""></div>
        <div class="blog-card-body">
          <h3>{p['title']}</h3>
        </div>
      </a>"""
        for p in POSTS
    )
    body = f"""<section class="page-header">
  <div class="container">
    <h1>Blog</h1>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="blog-grid">
{cards}
    </div>
  </div>
</section>"""

    page = head(
        "Blog - Tea Knez Coaching",
        "Misli o samorefleksiji, samozavesti, odnosih, vodenju in notranji rasti. Praktični vpogledi za jasen razmislek in zrele odločitve.",
        "https://www.teaknez.com/blog", 1
    ) + header("blog", 1) + body + footer(1)
    write("blog/index.html", page)


# ---------- BLOG POSTS ----------
def render_blog_post(slug, title, lead, image, body_html, prev_post=None, next_post=None):
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
    <h1>{title}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>

<div class="post-image"><img src="../../assets/images/{image}" alt=""></div>

<article class="post-body">
{body_html}
</article>
{nav}"""

    page = head(
        f"{title} - Tea Knez",
        lead,
        f"https://www.teaknez.com/blog/{slug}", 2
    ) + header("blog", 2) + body + footer(2)
    write(f"blog/{slug}/index.html", page)


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
        prev_post=None,
        next_post=POSTS[1],
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
        prev_post=POSTS[0],
        next_post=POSTS[2],
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
        prev_post=POSTS[1],
        next_post=POSTS[3],
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
        prev_post=POSTS[2],
        next_post=POSTS[4],
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
        prev_post=POSTS[3],
        next_post=POSTS[5],
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
        prev_post=POSTS[4],
        next_post=POSTS[6],
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
        prev_post=POSTS[5],
        next_post=POSTS[7],
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
        prev_post=POSTS[6],
        next_post=None,
    )


# ---------- CONTACT ----------
def page_contact():
    body = """<section class="section contact-intro">
  <div class="container">
    <div class="contact-header">
      <span class="eyebrow">Kontakt</span>
      <h1>Tukaj sem za <em>tvoje vprašanje</em>.</h1>
      <p>Odgovorim ti hitro in v najkrajšem možnem času.</p>
      <p>Če te kaj zaposluje, povprašuješ, ali bi rada uskladila spoznavno srečanje, mi piši — z veseljem se ti oglasim in najdeva čas za pogovor.</p>
    </div>
    <div class="contact-badges">
      <div class="contact-badge">
        <div class="contact-badge-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="16" r="12"/><path d="M16 9v7l5 3"/></svg>
        </div>
        <div>
          <strong>Hitri odgovor</strong>
          <span>Odgovorim ti v 1-2 delovnih dneh.</span>
        </div>
      </div>
      <div class="contact-badge">
        <div class="contact-badge-icon" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="14" width="18" height="14" rx="2"/><path d="M11 14V9a5 5 0 0 1 10 0v5"/></svg>
        </div>
        <div>
          <strong>Diskretnost</strong>
          <span>Vsebina sporočila ostane med nama.</span>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="contact-grid">
      <div class="contact-form-wrap">
        <span class="contact-block-eyebrow">Pošlji sporočilo</span>
        <form class="contact-form" action="https://api.web3forms.com/submit" method="POST" data-web3forms>
          <input type="hidden" name="access_key" value="e78b399d-a62e-494f-b90b-519f4b7f7a48">
          <input type="hidden" name="subject" value="Novo povpraševanje s teaknez.com">
          <input type="hidden" name="from_name" value="teaknez.com - kontaktni obrazec">
          <input type="checkbox" name="botcheck" style="display:none;" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="field">
            <label for="name">Ime in priimek</label>
            <input id="name" name="name" type="text" required autocomplete="name">
          </div>
          <div class="field">
            <label for="email">E-naslov</label>
            <input id="email" name="email" type="email" required autocomplete="email">
          </div>
          <div class="field">
            <label for="message">Sporočilo (neobvezno)</label>
            <textarea id="message" name="message" placeholder="Napiši na kratko, kaj te zanima…"></textarea>
          </div>
          <label class="field-check">
            <input type="checkbox" name="consent" required>
            <span>Strinjam se z obdelavo podatkov v skladu s <a href="politika-zasebnosti.html">pogoji</a>.</span>
          </label>
          <div class="h-captcha" data-sitekey="50b2fe65-b00b-4b9e-ad62-3ba471098be2"></div>
          <button type="submit" class="btn btn-primary">Pošlji sporočilo →</button>
          <div class="form-status" role="status" aria-live="polite"></div>
        </form>
        <script src="https://js.hcaptcha.com/1/api.js" async defer></script>
      </div>
      <div class="contact-steps-wrap">
        <span class="contact-block-eyebrow">Kaj se zgodi naprej</span>
        <ol class="contact-steps">
          <li>
            <span class="contact-step-num">01</span>
            <div>
              <strong>Pregledam tvoje sporočilo</strong>
              <p>Si vzamem čas, da razumem, kaj te trenutno zaposluje in kakšno podporo iščeš.</p>
            </div>
          </li>
          <li>
            <span class="contact-step-num">02</span>
            <div>
              <strong>Odgovorim ti</strong>
              <p>V 1-2 delovnih dneh ti pišem nazaj in predlagam termin za uvodni pogovor.</p>
            </div>
          </li>
          <li>
            <span class="contact-step-num">03</span>
            <div>
              <strong>Razmišljiva o možnostih</strong>
              <p>Na brezplačnem uvodnem klicu skupaj raziščeva, kako bi ti coaching lahko služil.</p>
            </div>
          </li>
        </ol>
        <p class="contact-signature">— Se veselim tvojega sporočila</p>
      </div>
    </div>
  </div>
</section>
"""
    page = head(
        "Kontakt - Tea Knez Coaching",
        "Piši mi za rezervacijo brezplačnega uvodnega srečanja. Coaching online, 60 minut, prilagojeno tvojemu tempu.",
        "https://www.teaknez.com/kontakt", 0
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
        "https://www.teaknez.com/politika-zasebnosti", 0
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
        "https://www.teaknez.com/piskotki", 0
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
      <p>Zaposlene se po porodniškem dopustu pogosto vračajo s spremenjeno identiteto, drugačnimi prioritetami in novimi pričakovanji do dela. Notranje doživljanje prehoda vpliva na samozavest, fokus, energijo — ter na občutek pripadnosti delovnemu okolju.</p>
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
      <p>Coaching ustvari prostor, kjer lahko zaposlena sama razišče, kar v tem trenutku najbolj potrebuje — prioritete, identitetne spremembe, samozavest, komunikacijo, postavljanje meja, odločitve, ki ji omogočijo trajnostno reintegracijo.</p>
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
        <p>Coaching podpora zaposlenim, ki se po porodniškem dopustu vračajo na delo. Naslavlja prehod celostno — od identitetnih sprememb in samozavesti do trajnostnega usklajevanja novih življenjskih in poklicnih vlog.</p>
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
        <p class="offering-note">Coaching proces sledi potrebam, ciljem in izzivom posameznice — ne vnaprej določenemu kurikulumu.</p>
      </article>

      <article class="offering-block">
        <span class="offering-label">Skupinska podpora</span>
        <h3>Seminar za vodje in HR</h3>
        <p class="offering-sub">Kako podpreti zaposleno ob vračanju po porodniškem dopustu — 2-urni interaktivni seminar</p>
        <p>Vodjem in HR strokovnjakom ponuja praktičen okvir za bolj podporno vodenje zaposlenih v prehodnem obdobju. Skupaj raziščemo dinamiko vračanja, najpogostejše izzive in konkretne pristope k komunikaciji in podpori — od check-in pogovorov do postavljanja realističnih pričakovanj.</p>
      </article>

      <article class="offering-block">
        <span class="offering-label">Profesionalna podpora</span>
        <h3>Coaching za zaposlene</h3>
        <p class="offering-sub">Individualni coaching onkraj reintegracije</p>
        <p>Coaching za zaposlene in strokovnjake, ki želijo bolj zavestno navigirati svojo profesionalno pot. Najpogostejše teme: karierni razvoj, samozavest, komunikacija, prehodi v vodstvene vloge, postavljanje meja in usklajevanje profesionalne in osebne vloge.</p>
        <p class="offering-note">Coaching proces sledi potrebam in ciljem posameznika — ne vnaprej določenim temam.</p>
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
    <p class="cta-end-lead">Vsaka organizacija ima drugačne potrebe in kontekst. Uvodni pogovor je raziskovalen — skupaj prepoznava, katera oblika podpore bi vašim zaposlenim in vodjem najbolje služila.</p>
    <button type="button" class="btn btn-primary" data-open-modal="contact-modal">Dogovorimo se za uvodni pogovor</button>
  </div>
</section>"""

    body += "\n" + contact_modal(0, subject="Povpraševanje – reintegracijski coaching")
    page = head(
        "Reintegracijski coaching za zaposlene po porodniškem dopustu - Tea Knez",
        "Coaching za zaposlene ob vračanju po porodniškem dopustu in podpora organizacijam. Seminar za vodje in HR. Individualni coaching za zaposlene in strokovnjake.",
        "https://www.teaknez.com/podpora-vracanju.html", 0
    ) + header("services", 0) + body + footer(0)
    write("podpora-vracanju.html", page)




# ---------- Sitemap & robots ----------
def page_sitemap():
    urls = [
        "https://www.teaknez.com/",
        "https://www.teaknez.com/za-posameznice.html",
        "https://www.teaknez.com/za-podjetja.html",
        "https://www.teaknez.com/podpora-vracanju.html",
        "https://www.teaknez.com/o-meni.html",
        "https://www.teaknez.com/blog/",
        "https://www.teaknez.com/kontakt.html",
        "https://www.teaknez.com/politika-zasebnosti.html",
        "https://www.teaknez.com/piskotki.html",
    ] + [f"https://www.teaknez.com/blog/{p['slug']}/" for p in POSTS]
    body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        body += f"  <url><loc>{u}</loc></url>\n"
    body += "</urlset>\n"
    write("sitemap.xml", body)
    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: https://www.teaknez.com/sitemap.xml\n")


# ---------- Build ----------
if __name__ == "__main__":
    page_index()
    page_about()
    page_za_posameznice()
    page_za_podjetja()
    page_blog_index()
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
    print("\nBuild complete.")
