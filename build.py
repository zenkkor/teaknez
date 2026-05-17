#!/usr/bin/env python3
"""Build static teaknez.com from extracted content."""
import os, re, html as ihtml
from pathlib import Path

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
<meta property="og:image" content="https://www.teaknez.com{asset.replace('..', '').lstrip('/')}/images/hero.png">
<link rel="icon" type="image/svg+xml" href="{asset}/images/favicon.svg">
<link rel="apple-touch-icon" href="{asset}/images/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset}/css/main.css">
</head>
<body>
"""

def header(active, depth=0):
    p = "../" * depth
    chev = '<svg class="chevron" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M3 5l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

    def link(label, href, key, extra=""):
        active_cls = " is-active" if active == key else ""
        return f'<a href="{href}" class="nav-link{active_cls}"{extra}>{label}</a>'

    dropdown_active = " is-active" if active == "services" else ""
    services_dropdown = f"""<li class="nav-item-dropdown" aria-expanded="false">
        <a href="{p}storitve.html" class="nav-link{dropdown_active}" aria-haspopup="true">
          Storitve {chev}
        </a>
        <ul class="dropdown-menu" role="menu">
          <li role="none"><a class="dropdown-link" role="menuitem" href="{p}storitve/osebni-coaching.html">
            <strong>Osebni coaching</strong>
            <span>Prostor za jasen razmislek in zrele odločitve.</span>
          </a></li>
          <li role="none"><a class="dropdown-link" role="menuitem" href="{p}storitve/karierni-in-poslovni-coaching.html">
            <strong>Karierni in poslovni coaching</strong>
            <span>Za prehode, premišljen naslednji korak in nove vloge.</span>
          </a></li>
          <li role="none"><a class="dropdown-link" role="menuitem" href="{p}storitve/coaching-za-podjetja.html">
            <strong>Coaching za podjetja</strong>
            <span>Kultura zaupanja, zavestnega vodenja in odgovornosti.</span>
          </a></li>
          <li role="none"><hr class="dropdown-divider"></li>
          <li role="none"><a class="dropdown-link dropdown-link-all" role="menuitem" href="{p}storitve.html">
            <strong>Vse storitve →</strong>
          </a></li>
        </ul>
      </li>"""

    return f"""<a href="#main" class="skip-link">Preskoči na vsebino</a>
<header class="site-header">
  <div class="container">
    <a href="{p}index.html" class="site-logo" aria-label="Tea Knez Coaching - domov">
      <span>Tea Knez<small class="tag">Coaching</small></span>
    </a>
    <nav class="site-nav" id="site-nav" aria-label="Glavna navigacija">
      <ul class="nav-list">
        <li>{link("Domov", p + "index.html", "home")}</li>
        {services_dropdown}
        <li>{link("Blog", p + "blog/", "blog")}</li>
        <li>{link("O meni", p + "o-meni.html", "about")}</li>
      </ul>
      <a href="{p}kontakt.html" class="nav-cta">Piši mi!</a>
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
        <p>Osebni, karierni in poslovni coaching. Prostor za jasen razmislek, zrele odločitve in trajne spremembe.</p>
      </div>
      <div class="footer-col">
        <h4>Storitve</h4>
        <ul>
          <li><a href="{p}storitve/osebni-coaching.html">Osebni coaching</a></li>
          <li><a href="{p}storitve/karierni-in-poslovni-coaching.html">Karierni in poslovni</a></li>
          <li><a href="{p}storitve/coaching-za-podjetja.html">Za podjetja</a></li>
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
      <span>© 2026 Integra, Tea Knez s.p.</span>
      <span><a href="mailto:tea@teaknez.com">tea@teaknez.com</a></span>
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
    ("V poslu sem dolgo dvomil vase, čeprav sem bil strokovno samozavesten. Coaching mi je dal strateško jasnost in pogum za pomembne odločitve.",
     "Luka", "osebni trener"),
    ("Navajena sem biti ves čas ‘vidna’, redko pa sem si dovolila prostor za razmislek. Naučila sem se postaviti jasnejše meje in začela ustvarjati z več notranjega miru.",
     "Maja", "influencerka"),
]

def testimonials_section():
    cards = "\n".join(
        f"""    <article class="testimonial">
      <blockquote>»{q}«</blockquote>
      <cite><strong>{name}</strong>{role}</cite>
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
    body = """<section class="hero">
  <div class="container">
    <div class="hero-grid">
      <div>
        <h1>Notranja jasnost.<br><em>Zrele odločitve.</em><br>Trajne spremembe.</h1>
        <p class="hero-lead">Pomagam ti umiriti notranji hrup, razjasniti prioritete in sprejemati odločitve, ki so skladne s tem, kdo si.</p>
        <a href="kontakt.html" class="btn btn-primary">Piši mi!</a>
      </div>
      <div class="hero-image-wrap">
        <div class="hero-image"><img src="assets/images/hero.png" alt="Tea Knez - coaching" loading="eager"></div>
      </div>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="reasons">
      <div>
        <span class="eyebrow">Mogoče</span>
        <h2>Mogoče si tukaj, ker…</h2>
      </div>
      <ul class="reasons-list">
        <li>stojiš pred pomembno odločitvijo in želiš več jasnosti</li>
        <li>čutiš, da zmoreš več, a nekaj ostaja neizrečeno</li>
        <li>si v prehodu in iščeš smer, ki je res skladna s tabo</li>
        <li>želiš več miru, samozavesti in notranje stabilnosti</li>
        <li>navzven deluješ samozavestno, znotraj pa iščeš ravnovesje</li>
      </ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split">
      <div class="split-image"><img src="assets/images/coaching-section.png" alt="Coaching - prostor za razmislek"></div>
      <div>
        <span class="eyebrow">Kaj je coaching</span>
        <p>Coaching ni svetovanje in ni terapija. Je <strong>strukturiran, zaupen proces</strong>, ki te podpira pri bolj jasnem in zavestnem razmišljanju. Namesto da iščeš odgovore zunaj, začneš <strong>razumevati sebe, svoje vzorce in svoje odločitve</strong>.</p>
        <p>Postopoma oblikuješ <strong>korake, ki so res v skladu s tabo</strong>.</p>
        <p>Coaching ne daje rešitev. Ustvari prostor, kjer lahko <em>odgovore odkriješ sam</em>.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="outcomes">
      <span class="eyebrow">Kaj se spremeni?</span>
      <h2>Kaj se spremeni?</h2>
      <p>Sčasoma opaziš, da:</p>
      <ul>
        <li>odločitve sprejemaš bolj mirno in z manj notranjega hrupa.</li>
        <li>jasneje komuniciraš svoje meje in pričakovanja.</li>
        <li>prevzemaš odgovornost brez pretiranega pritiska.</li>
        <li>deluješ bolj skladno s tem, kar ti je zares pomembno.</li>
        <li>gradiš stabilnost, ki ni odvisna od zunanjih okoliščin.</li>
      </ul>
      <p class="outcomes-final">In kar je najpomembneje: imaš več jasnosti, kako naprej - na način, ki je tvoj.</p>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Moj pristop</span>
    </div>
    <div class="cards">
      <div class="card">
        <div class="card-icon">I.</div>
        <h3>Coaching z globino in strukturo</h3>
        <p>Ne ponujam hitrih rešitev. Delava sistemično - raziskujeva širšo sliko, odnose, dinamike in nezavedne vzorce. Hkrati ostajava zelo konkretna: cilji so jasni, koraki izvedljivi, napredek merljiv.</p>
      </div>
      <div class="card">
        <div class="card-icon">II.</div>
        <h3>So-ustvarjanje, ne svetovanje</h3>
        <p>Ne dajem nasvetov. Postavljam vprašanja, ki odpirajo perspektivo. Izzivam s spoštovanjem. Podprem te, da sam/a prideš do odločitev, ki so skladne s tvojo identiteto, vrednotami in vlogo, ki jo živiš.</p>
      </div>
      <div class="card">
        <div class="card-icon">III.</div>
        <h3>Toplina, jasnost in pogum</h3>
        <p>Moj stil je neposreden, a empatičen. Ustvarjam prostor zaupanja, kjer lahko razmišljaš na glas, preizkušaš ideje in krepiš notranjo stabilnost. Ko je potrebno, odprem tudi zahtevne teme - z občutkom in jasnostjo.</p>
      </div>
    </div>
  </div>
</section>
""" + testimonials_section() + """
<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Blog</span>
      <h2>Prostor za refleksijo</h2>
      <p>Praktični vpogledi in misli, ki ti pomagajo graditi jasnost, notranjo moč in osebno rast.</p>
    </div>
    <div class="blog-grid">
      <a class="blog-card" href="blog/vracanje-s-porodniskega-dopusta/">
        <div class="blog-card-image"><img src="assets/images/blog-vracanje.png" alt=""></div>
        <div class="blog-card-body">
          <h3>Vračanje s porodniškega dopusta: ko se vrneš drugačna</h3>
        </div>
      </a>
      <a class="blog-card" href="blog/kako-preprečiti-izgorelost-v-podjetjih-kultura-ravnovesja-ne-žrtvovanja/">
        <div class="blog-card-image"><img src="assets/images/blog-izgorelost.png" alt=""></div>
        <div class="blog-card-body">
          <h3>Kako preprečiti izgorelost v podjetjih: kultura ravnovesja, ne žrtvovanja</h3>
        </div>
      </a>
      <a class="blog-card" href="blog/kako-premagati-sindrom-vsiljivca-(imposter-syndrome)/">
        <div class="blog-card-image"><img src="assets/images/blog-sindrom.png" alt=""></div>
        <div class="blog-card-body">
          <h3>Kako premagati sindrom vsiljivca (imposter syndrome)</h3>
        </div>
      </a>
    </div>
    <div class="section-foot">
      <a href="blog/" class="btn btn-secondary">Preberi več</a>
    </div>
  </div>
</section>
"""

    page = head(
        "Tea Knez - Osebni, karierni in poslovni coaching",
        "Pomagam ti umiriti notranji hrup, razjasniti prioritete in sprejemati odločitve, ki so skladne s tem, kdo si. Osebni, karierni in poslovni coaching.",
        "https://www.teaknez.com/", 0
    ) + header("home", 0) + body + footer(0)
    write("index.html", page)


# ---------- ABOUT ----------
def page_about():
    body = """<section class="page-header">
  <div class="container">
    <span class="eyebrow">O meni</span>
    <h1>O meni</h1>
    <p class="lead">Večina ljudi ne potrebuje več informacij. Potrebuje prostor, da lahko jasno razmisli.</p>
  </div>
</section>

<section class="container">
  <div class="about-intro">
    <div class="split-image portrait"><img src="assets/images/about-tea.png" alt="Tea Knez"></div>
    <div>
      <p>Sem <strong>Tea</strong>, coachinja in podjetnica, predvsem pa ženska in mama. V svoji karieri sem delovala v okoljih, kjer so odločitve pomembne, odgovornost velika in odnosi kompleksni. Prav tam sem od blizu spoznala, kako hitro lahko jasnost zamegli pritisk - in kako dragocen je prostor za premišljen razmislek.</p>
      <p>Vedno me je zanimalo, kaj ljudi zares premakne, ne le navzven, ampak navznoter. Kaj ustvarja notranjo stabilnost, iz katere lahko delujemo bolj zrelo.</p>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="split">
      <div>
        <span class="eyebrow">Moj pristop</span>
        <h2>Moj pristop</h2>
        <p>Coaching zame ni svetovanje, temveč <strong>strukturiran proces razmisleka</strong>.</p>
        <p>Ustvarjam <strong>varen, a zahteven prostor</strong>, kjer raziščeš širšo sliko - odnose, dinamike in svoje vzorce odločanja. Verjamem, da ima vsak človek v sebi vse vire in odgovore, včasih potrebujemo le <strong>prisotnost in jasnost</strong>, da jih prepoznamo.</p>
        <p>Moje delo temelji na poslušanju, natančnih vprašanjih in spoštovanju tvojega procesa. Cilj ni hitra rešitev, temveč zrela odločitev.</p>
      </div>
      <div class="split-image portrait"><img src="assets/images/tea-portrait.png" alt="Tea Knez - portret"></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head" style="text-align:left;max-width:780px;margin-left:0;">
      <span class="eyebrow">Moja pot</span>
      <h2>Moja pot</h2>
    </div>
    <div style="max-width:780px;">
      <p>Skozi svojo kariero sem opravljala in opravljam različne vloge: pravnica, mediatorka, vodja ekip in podjetnica. Delo z ljudmi v zahtevnih situacijah me je naučilo, da sprememba ni stvar motivacije, temveč razumevanja.</p>
      <p>Iz teh izkušenj je naravno zrasla moja pot v coaching - kot nadaljevanje zanimanja za odnose, odgovornost in razvoj potenciala.</p>
      <p>Moj pristop pa ne oblikujejo le profesionalne izkušnje, temveč tudi moja vloga žene in mame, kjer se vsak dan znova učim, kako pomembni so <strong>prisotnost, razumevanje in prostor za resničen premislek.</strong></p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="credentials">
      <h3>Izobrazba in certifikati</h3>
      <ul class="credentials-list">
        <li>NLP Mojster Praktik &amp; Coach (INLPTA)</li>
        <li>Life Coach Practitioner (Academy of Applied Psychology)</li>
        <li>Mediator (Inštitut za mediacijo Concordia)</li>
      </ul>
      <h3>Coaching akreditacije</h3>
      <ul class="credentials-list">
        <li>Organizacijska coachinja (Kreativlab d.o.o.)</li>
        <li>EIA EMCC - individualna akreditacija</li>
        <li>ACC ICF - v pridobivanju</li>
      </ul>
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Vrednote</span>
      <h2>Vrednote, ki me vodijo</h2>
    </div>
    <div class="values">
      <div class="value">
        <h3>Prisotnost</h3>
        <p>V vsakem srečanju sem polno zbrana, pozorna in odprta. Verjamem, da se spremembe začnejo takrat, ko se človek res počuti slišanega.</p>
      </div>
      <div class="value">
        <h3>Rast</h3>
        <p>Ne ponujam rešitev namesto tebe. Verjamem, da že nosiš v sebi vse odgovore. Jaz sem tu, da ti pomagam, da jih (ponovno) odkriješ.</p>
      </div>
      <div class="value">
        <h3>Zaupanje</h3>
        <p>Temelj coachinga je iskrenost in spoštovanje meja. Tvoja izkušnja je tvoja, jaz sem tu, da jo podpiram brez sodbe.</p>
      </div>
    </div>
  </div>
</section>

<section class="cta-end">
  <div class="container">
    <h2>Želiš raziskati več?</h2>
    <a href="kontakt.html" class="btn btn-primary">Piši mi!</a>
  </div>
</section>"""

    page = head(
        "O meni - Tea Knez",
        "Sem Tea Knez, coachinja, mediatorka in podjetnica. Spoznaj moj pristop, vrednote in pot, ki vodi v ustvarjanje prostora za zrele odločitve.",
        "https://www.teaknez.com/o-meni", 0
    ) + header("about", 0) + body + footer(0)
    write("o-meni.html", page)


# ---------- SERVICES HUB ----------
def page_services_hub():
    body = """<section class="page-header">
  <div class="container">
    <span class="eyebrow">Storitve</span>
    <h1>Storitve</h1>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="services-grid">
      <a class="service-card" href="storitve/osebni-coaching.html">
        <div class="service-card-image"><img src="assets/images/service-osebni.png" alt=""></div>
        <div class="service-card-body">
          <h3>Osebni coaching</h3>
          <p>Strukturiran in zaupen prostor za razmislek. Za jasnost odločitev, zaupanje vase in več ravnovesja v vsakdanu.</p>
          <span class="service-card-more">Spoznaj proces</span>
        </div>
      </a>
      <a class="service-card" href="storitve/karierni-in-poslovni-coaching.html">
        <div class="service-card-image"><img src="assets/images/service-karierni.png" alt=""></div>
        <div class="service-card-body">
          <h3>Karierni in poslovni coaching</h3>
          <p>Za posameznike v prehodih: vrnitev na delo, menjava službe, nova vloga ali drugačen način vodenja kariere.</p>
          <span class="service-card-more">Spoznaj proces</span>
        </div>
      </a>
      <a class="service-card" href="storitve/coaching-za-podjetja.html">
        <div class="service-card-image"><img src="assets/images/service-podjetja.png" alt=""></div>
        <div class="service-card-body">
          <h3>Coaching za podjetja</h3>
          <p>Razvoj vodij, ekip in ključnih posameznikov. Kultura zaupanja, zavestnega vodenja in skupne odgovornosti.</p>
          <span class="service-card-more">Spoznaj proces</span>
        </div>
      </a>
    </div>
  </div>
</section>"""

    page = head(
        "Storitve - Tea Knez Coaching",
        "Osebni, karierni in poslovni coaching ter coaching za podjetja. Spoznaj tri oblike sodelovanja in izberi tisto, ki najbolj ustreza tvoji situaciji.",
        "https://www.teaknez.com/storitve", 0
    ) + header("services", 0) + body + footer(0)
    write("storitve.html", page)


# ---------- SERVICE DETAIL TEMPLATE ----------
def service_detail(slug, title, lead, intro_paragraphs, bullets_intro, bullets, benefits_intro, benefits, image, meta_pills, head_desc):
    bullets_html = ""
    if bullets:
        items = "\n".join(f"      <li>{b}</li>" for b in bullets)
        bullets_html = f"<p>{bullets_intro}</p>\n    <ul>\n{items}\n    </ul>\n"
    intro_html = "\n    ".join(f"<p>{p}</p>" for p in intro_paragraphs)
    meta_html = "\n      ".join(f'<span class="service-meta-item">{p}</span>' for p in meta_pills)
    benefits_html = "\n".join(
        f"""      <div class="card">
        <div class="card-icon">{i+1}.</div>
        <h3>{b['title']}</h3>
        <p>{b['text']}</p>
      </div>"""
        for i, b in enumerate(benefits)
    )
    body = f"""<section class="container">
  <div class="service-hero">
    <div>
      <span class="eyebrow">Storitev</span>
      <h1>{title}</h1>
      <p class="lead">{lead}</p>
      <div class="service-meta">
      {meta_html}
      </div>
    </div>
    <div class="service-hero-image"><img src="../assets/images/{image}" alt=""></div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="service-body">
      {intro_html}
      {bullets_html}
    </div>
  </div>
</section>

<section class="section section-cream">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Kaj pridobiš</span>
      <h2>Kaj pridobiš</h2>
      <p>{benefits_intro}</p>
    </div>
    <div class="cards">
{benefits_html}
    </div>
  </div>
</section>
""" + testimonials_section() + """
<section class="cta-end">
  <div class="container">
    <h2>Želiš raziskati več?</h2>
    <a href="../kontakt.html" class="btn btn-primary">Piši mi!</a>
  </div>
</section>"""

    page = head(
        f"{title} - Tea Knez",
        head_desc,
        f"https://www.teaknez.com/storitve/{slug}", 1
    ) + header("services", 1) + body + footer(1)
    write(f"storitve/{slug}.html", page)


def page_osebni():
    service_detail(
        slug="osebni-coaching",
        title="Osebni coaching",
        lead="Osebni coaching ti pomaga razjasniti misli, prepoznati vzorce in delovati z več notranje stabilnosti.",
        intro_paragraphs=[
            'Osebni coaching je <strong>strukturiran in zaupen prostor za razmislek</strong>. Ni svetovanje ali terapija, temveč proces, v katerem raziskuješ svoje misli, odločitve in notranje vzorce. Skozi usmerjena vprašanja postopoma prepoznavaš, kaj te ustavlja, kaj potrebuješ in kako lahko deluješ bolj skladno s sabo.',
            'Postane bolj jasno, kaj je zate zares pomembno in kako želiš naprej. Coaching ti pomaga graditi <strong>notranjo stabilnost, jasnost in samozavest pri odločitvah</strong>.',
            'Srečanja potekajo online, trajajo 60 minut in so prilagojena tvojemu tempu.',
        ],
        bullets_intro="",
        bullets=[],
        benefits_intro="Postopno gradiš jasnost, zaupanje vase in notranjo stabilnost.",
        benefits=[
            {"title": "Jasnost odločitev", "text": "Lažje razumeš, kaj je zate res pomembno, in sprejemaš bolj premišljene odločitve."},
            {"title": "Zaupanje vase", "text": "Okrepiš notranjo stabilnost in začneš delovati z več samozavesti."},
            {"title": "Ravnovesje", "text": "V vsakdan vneseš več miru, prisotnosti in občutek, da si v stiku s sabo."},
        ],
        image="service-osebni.png",
        meta_pills=["60 min srečanja", "Online", "Tvoj tempo"],
        head_desc="Osebni coaching s Teo Knez. Strukturiran in zaupen prostor za razmislek, jasnost odločitev in več ravnovesja v vsakdanu."
    )


def page_karierni():
    service_detail(
        slug="karierni-in-poslovni-coaching",
        title="Karierni in poslovni coaching",
        lead="Karierni in poslovni coaching ti pomaga razjasniti smer, okrepiti samozavest pri odločanju in graditi vlogo, ki je skladna s tvojimi vrednotami.",
        intro_paragraphs=[
            'Ko se znajdeš na točki spremembe, ne potrebuješ še enega nasveta - potrebuješ jasnost.',
            'Coaching je namenjen posameznikom, ki razmišljajo o naslednjem koraku: vrnitev na delo, menjava službe, nova vloga ali drugačen način vodenja kariere.',
            'Coaching ti ponudi <strong>strukturiran in zaupen prostor</strong>, kjer lahko razmisliš širše. O svojih vrednotah, ambicijah in realnih možnostih. Ne iščeš idealne rešitve, ampak smer, ki je skladna s tabo.',
            'Srečanja trajajo 60 minut in potekajo online. Proces temelji na profesionalnih standardih, zaupnosti in spoštovanju tvojega tempa.',
        ],
        bullets_intro="Prehodi prinesejo vprašanja:",
        bullets=[
            "Kje sem danes?",
            "Kaj mi je v tej fazi res pomembno?",
            "Kakšno vlogo želim graditi?",
        ],
        benefits_intro="Raziščeš svoje vrednote, okrepiš zavedanje in ustvariš kariero v ravnovesju s sabo.",
        benefits=[
            {"title": "Jasnost smeri", "text": "Razumeš, kaj ti je v tej fazi kariere in življenja zares pomembno."},
            {"title": "Samozavest pri odločitvah", "text": "Odločitve sprejemaš z več notranje gotovosti in manj dvoma."},
            {"title": "Zrel premik", "text": "Ne ostaneš v razmišljanju, temveč narediš premišljen korak naprej."},
        ],
        image="service-karierni.png",
        meta_pills=["60 min srečanja", "Online", "Zaupno"],
        head_desc="Karierni in poslovni coaching s Teo Knez. Strukturiran prostor za jasno smer, premišljene odločitve in zrele karierne premike."
    )


def page_podjetja():
    service_detail(
        slug="coaching-za-podjetja",
        title="Coaching za podjetja",
        lead="Ustvari kulturo zaupanja, sodelovanja in zavestnega vodenja. Coaching za podjetja spodbuja rast posameznikov in ekip, krepi komunikacijo ter pomaga, da delo postane prostor navdiha, povezanosti in skupnega razvoja.",
        intro_paragraphs=[
            'Gradite kulturo zaupanja, odgovornosti in zavestnega vodenja. Coaching za podjetja je namenjen organizacijam, ki želijo sistematično vlagati v razvoj vodij, ekip in ključnih posameznikov. V kompleksnem poslovnem okolju postajajo komunikacija, čustvena inteligenca in sposobnost sodelovanja ključni dejavniki uspeha.',
            'Skozi strukturiran coaching proces ustvarjamo prostor za refleksijo, jasnejše odločanje in bolj zavestno vodenje. Poudarek je na odgovornosti, medsebojnem zaupanju ter krepitvi kulture, kjer posamezniki delujejo skladno s skupnimi cilji in vrednotami.',
            'Srečanja potekajo online ali v živo, individualno ali v manjših skupinah. Proces temelji na profesionalnih standardih ICF ter spoštovanju zaupnosti in etike.',
        ],
        bullets_intro="Coaching podpira organizacije pri:",
        bullets=[
            "razvoju vodstvenih kompetenc",
            "izboljšanju timske dinamike",
            "navigiranju sprememb",
            "krepitvi notranje motivacije in zavzetosti",
        ],
        benefits_intro="Razvijajte kulturo zaupanja, sodelovanja in notranje motivacije v svojem podjetju.",
        benefits=[
            {"title": "Zavestno vodenje", "text": "Vodje krepijo sposobnost jasne komunikacije, odgovornega odločanja in stabilnega delovanja v zahtevnih situacijah."},
            {"title": "Sodelovanje in zaupanje", "text": "Ekipe razvijajo odprt dialog, več medsebojnega razumevanja in skupno odgovornost za rezultate."},
            {"title": "Trajnostni razvoj potencialov", "text": "Organizacija gradi temelje za dolgoročno rast, večjo odpornost in večjo zavzetost zaposlenih."},
        ],
        image="service-podjetja.png",
        meta_pills=["Individualno ali skupinsko", "Online ali v živo", "Skladno z ICF standardi"],
        head_desc="Coaching za podjetja. Razvoj vodij, ekip in kulture zaupanja. Profesionalno strukturiran proces v skladu z ICF standardi."
    )


# ---------- BLOG INDEX ----------
POSTS = [
    {"slug":"vracanje-s-porodniskega-dopusta", "title":"Vračanje s porodniškega dopusta: ko se vrneš drugačna",
     "summary":"Kako podpreti vračanje s porodniškega dopusta? O izzivih, prehodu in vlogi coachinga za posameznice in podjetja.",
     "image":"blog-vracanje.png"},
    {"slug":"kako-preprečiti-izgorelost-v-podjetjih-kultura-ravnovesja-ne-žrtvovanja", "title":"Kako preprečiti izgorelost v podjetjih: kultura ravnovesja, ne žrtvovanja",
     "summary":"Kultura zaupanja in ravnovesja namesto preobremenjenosti. Ustvari delovno okolje, kjer ljudje resnično zmorejo rasti.",
     "image":"blog-izgorelost.png"},
    {"slug":"kako-premagati-sindrom-vsiljivca-(imposter-syndrome)", "title":"Kako premagati sindrom vsiljivca (imposter syndrome)",
     "summary":"O dvomu vase, ki te želi zaščititi. Spoznaj, kako prepoznati ta glas in verjeti, da si že zdaj dovolj.",
     "image":"blog-sindrom.png"},
    {"slug":"ko-mir-v-sebi-postane-pomembnejši-od-tega-da-imaš-prav", "title":"Ko mir v sebi postane pomembnejši od tega, da imaš prav",
     "summary":"O notranji svobodi, ko mir izbereš pred dokazovanjem. Nauči se slišati sebe, ne potrebe po potrditvi.",
     "image":"blog-mir.png"},
    {"slug":"samozavest-ni-nekaj-kar-imas", "title":"Samozavest ni nekaj, kar imaš – ampak nekaj, kar gradiš",
     "summary":"Samozavest ni lastnost, s katero se rodiš – je pot, ki jo gradiš skozi drobne izbire in notranji dialog.",
     "image":"blog-samozavest.png"},
    {"slug":"avtenticno-vodenje-moc-resnicnega-stika", "title":"Avtentično vodenje: Moč resničnega stika",
     "summary":"Avtentično vodenje ne temelji na popolnosti, temveč na iskrenosti in povezanosti. Kako voditi z resničnostjo.",
     "image":"blog-avtenticno.png"},
    {"slug":"notranji-kritik-kako-ga-prepoznati-in-spremeniti-v-zaveznika", "title":"Notranji kritik: Kako ga prepoznati in spremeniti v zaveznika",
     "summary":"Notranji kritik pogosto ovira našo rast, a lahko postane vir učenja. Kako ga prepoznati in preoblikovati.",
     "image":"blog-notranji.png"},
    {"slug":"odpornost-in-proznost-celostna-notranja-moc", "title":"Odpornost in prožnost: Kako graditi notranjo moč celostno",
     "summary":"Odpornost ni le miselna trdnost – vključuje telo, čustva, misli in odnose. Kako celostno graditi notranjo moč.",
     "image":"blog-odpornost.png"},
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
    <span class="eyebrow">Blog</span>
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
        "blog-vracanje.png",
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
        "blog-izgorelost.png",
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
        "blog-sindrom.png",
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
        "blog-mir.png",
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
        "blog-samozavest.png",
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
        "blog-avtenticno.png",
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
        "blog-notranji.png",
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
        "blog-odpornost.png",
        body,
        prev_post=POSTS[6],
        next_post=None,
    )


# ---------- CONTACT ----------
def page_contact():
    body = """<section class="page-header">
  <div class="container">
    <span class="eyebrow">Kontakt</span>
    <h1>Začni svoje potovanje</h1>
    <p class="lead">Včasih že en pogovor prinese več jasnosti. Piši mi za rezervacijo prvega brezplačnega uvodnega srečanja, kjer skupaj pogledava, kje si in kam želiš.</p>
  </div>
</section>

<section class="container">
  <div class="contact-single">
    <form class="contact-form" action="https://api.web3forms.com/submit" method="POST" data-web3forms>
      <input type="hidden" name="access_key" value="e78b399d-a62e-494f-b90b-519f4b7f7a48">
      <input type="hidden" name="subject" value="Novo povpraševanje s teaknez.com">
      <input type="hidden" name="from_name" value="teaknez.com - kontaktni obrazec">
      <input type="checkbox" name="botcheck" style="display:none;" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="field">
        <label for="name">Ime*</label>
        <input id="name" name="name" type="text" required autocomplete="name">
      </div>
      <div class="field">
        <label for="email">Email*</label>
        <input id="email" name="email" type="email" required autocomplete="email">
      </div>
      <div class="field">
        <label for="message">Sporočilo</label>
        <textarea id="message" name="message" placeholder="Napiši na kratko, kaj te vodi tukaj…"></textarea>
      </div>
      <label class="field-check">
        <input type="checkbox" name="consent" required>
        <span>Strinjam se s <a href="politika-zasebnosti.html">Pogoji.</a></span>
      </label>
      <div class="h-captcha" data-captcha="true"></div>
      <button type="submit" class="btn btn-primary">Piši mi</button>
      <div class="form-status" role="status" aria-live="polite"></div>
    </form>
    <script src="https://js.hcaptcha.com/1/api.js" async defer></script>
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


# ---------- Sitemap & robots ----------
def page_sitemap():
    urls = [
        "https://www.teaknez.com/",
        "https://www.teaknez.com/o-meni.html",
        "https://www.teaknez.com/storitve.html",
        "https://www.teaknez.com/storitve/osebni-coaching.html",
        "https://www.teaknez.com/storitve/karierni-in-poslovni-coaching.html",
        "https://www.teaknez.com/storitve/coaching-za-podjetja.html",
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
    page_services_hub()
    page_osebni()
    page_karierni()
    page_podjetja()
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
    page_sitemap()
    print("\nBuild complete.")
