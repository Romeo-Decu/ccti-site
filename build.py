"""Generează site-ul static ccti.ro (EN implicit, RO în /ro/) dintr-o singură sursă de conținut.

Rulare: python build.py  →  scrie paginile HTML, sitemap.xml și robots.txt în directorul curent.
Fără dependențe externe. Conținutul e în content.py; aici sunt doar șabloanele.
"""

import html
import json
from pathlib import Path

from content import (ARTICLES, BASE, CONTACT, DIRECTIONS, HOME, LAB, ORG, PRODUCTS, SCENARIOS,
                     SYNERGETIC, T, UI)

OUT = Path(__file__).parent
PAGES: list[tuple[str, str]] = []  # (url, lastmod) pentru sitemap


def e(text: str) -> str:
    return html.escape(text, quote=True)


def url_for(lang: str, path: str) -> str:
    return f"{BASE}/{'ro/' if lang == 'ro' else ''}{path}"


def page(lang: str, path: str, title: str, description: str, body: str, *,
         alternate: bool = True, jsonld: list | None = None, depth: int = 0) -> None:
    """Scrie o pagină completă. `path` e relativ la rădăcina limbii (ex.: products/aero-360.html)."""
    root = "../" * (depth + (1 if lang == "ro" else 0))
    canonical = url_for(lang, path)
    links = [f'<link rel="canonical" href="{canonical}">']
    if alternate:
        links += [
            f'<link rel="alternate" hreflang="en" href="{url_for("en", path)}">',
            f'<link rel="alternate" hreflang="ro" href="{url_for("ro", path)}">',
            f'<link rel="alternate" hreflang="x-default" href="{url_for("en", path)}">',
        ]
    ld = "".join(
        f'<script type="application/ld+json">{json.dumps(item, ensure_ascii=False)}</script>'
        for item in (jsonld or [])
    )
    other = "ro" if lang == "en" else "en"
    switch = (
        f'<a class="lang" href="{url_for(other, path)}" hreflang="{other}">{other.upper()}</a>'
        if alternate else ""
    )
    nav = "".join(
        f'<a href="{root}{"ro/" if lang == "ro" and not href.startswith("insights") else ""}{href}">{e(label[lang])}</a>'
        for href, label in UI["nav"]
    )
    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{''.join(links)}
<meta property="og:type" content="website">
<meta property="og:site_name" content="CCTI">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}/logo.png">
<meta property="og:locale" content="{'ro_RO' if lang == 'ro' else 'en_US'}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{root}logo.png">
<link rel="stylesheet" href="{root}style.css">
{ld}
</head>
<body>
<header><div class="wrap nav">
  <a class="brand" href="{root}{'ro/' if lang == 'ro' else ''}"><img src="{root}logo.png" alt="CCTI logo">CCTI</a>
  <nav>{nav}</nav>
  {switch}
</div></header>
<main>
{body}
</main>
<footer><div class="wrap">© 2026 CCTI · {e(UI['slogan'])} · <a href="{root}{'ro/' if lang == 'ro' else ''}#contact">{e(UI['contact'][lang])}</a></div></footer>
</body>
</html>
"""
    base = OUT / "ro" if lang == "ro" else OUT
    if not path:
        target = base / "index.html"
    elif path.endswith("/"):
        target = base / path / "index.html"
    else:
        target = base / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    PAGES.append((canonical, "2026-11-02"))


def org_ld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ResearchOrganization",
        "name": "CCTI — Center for Research in Thermodynamics and Informatics",
        "legalName": ORG["legal_name"],
        "alternateName": ["CCTI", "Centrul de Cercetări în Termodinamică și Informatică"],
        "slogan": UI["slogan"],
        "url": BASE + "/",
        "logo": BASE + "/logo.png",
        "email": ORG["email"],
        "foundingDate": "2018-07-12",
        "address": {
            "@type": "PostalAddress", "streetAddress": ORG["street"],
            "addressLocality": "Măgurele", "addressRegion": "Ilfov",
            "postalCode": "077125", "addressCountry": "RO",
        },
        "identifier": [
            {"@type": "PropertyValue", "propertyID": "CUI", "value": ORG["cui"]},
            {"@type": "PropertyValue", "propertyID": "Trade Register", "value": ORG["reg"]},
            {"@type": "PropertyValue", "propertyID": "EU PIC", "value": ORG["pic"]},
        ],
        "duns": ORG["duns"],
        "taxID": ORG["cui"],
        "naics": "541715",
        "knowsAbout": ["thermodynamics", "informatics", "clean energy", "robotics for hostile environments",
                       "climate technologies", "air purification", "innovation strategy"],
        "founder": {"@type": "Person", "name": "Romeo Decu", "sameAs": ORG["founder_links"]},
        "sameAs": ORG["same_as"],
    }


def card(head: str, text: str, tag: str = "", href: str = "") -> str:
    title = f'<a href="{href}">{e(head)}</a>' if href else e(head)
    return (f'<div class="card">{f"<span class=tag>{e(tag)}</span>" if tag else ""}'
            f'<h3>{title}</h3><p>{e(text)}</p></div>')


def home(lang: str) -> None:
    pre = "" if lang == "ro" else ""
    h = HOME
    directions = "".join(
        f'<div class="card"><div class="num">{e(d["n"])}</div><div class="eyebrow">{e(d["brand"])}</div>'
        f'<h3>{e(d["title"][lang])}</h3><p>{e(d["text"][lang])}</p></div>' for d in DIRECTIONS
    )
    focus = "".join(card(f["title"][lang], f["text"][lang]) for f in h["focus"])
    products = "".join(
        card(p["name"], p["short"][lang], f'{p["domain"][lang]} · {p["stage"][lang]}', f'products/{p["slug"]}.html')
        for p in PRODUCTS
    )
    lab = "".join(card(item["title"][lang], item["text"][lang]) for item in LAB["principles"])
    evidence = "".join(
        f'<li>{e(item["text"][lang])}{"".join(f" · <a href={chr(34)}{link}{chr(34)}>{e(label)}</a>" for label, link in item["links"])}</li>'
        for item in h["evidence"]
    )
    contacts = "".join(
        f'<a class="btn{" ghost" if i else ""}" href="mailto:{ORG["email"]}?subject={e(c["subject"])}">{e(c["label"][lang])}</a>'
        for i, c in enumerate(CONTACT)
    )
    body = f"""
<div class="wrap hero">
  <div>
    <div class="eyebrow">{e(T['name'][lang])}</div>
    <h1>{e(h['h1'][lang])}</h1>
    <p class="lead">{e(h['lead'][lang])}</p>
    <p class="position">{e(h['position'])}</p>
  </div>
  <img src="{'../' if lang == 'ro' else ''}logo.png" alt="CCTI — {e(UI['slogan'])}">
</div>
<section id="directions"><div class="wrap">
  <h2>{e(h['dir_h'][lang])}</h2><p class="sub">{e(h['dir_sub'][lang])}</p>
  <div class="grid">{directions}</div>
</div></section>
<section id="focus" class="alt"><div class="wrap">
  <h2>{e(h['focus_h'][lang])}</h2><p class="sub">{e(h['focus_sub'][lang])}</p>
  <div class="grid">{focus}</div>
</div></section>
<section id="products"><div class="wrap">
  <h2>{e(h['prod_h'][lang])}</h2><p class="sub">{e(h['prod_sub'][lang])}</p>
  <div class="grid five">{products}</div>
</div></section>
<section id="services" class="alt"><div class="wrap">
  <h2>Synergetic Solutions</h2>
  <p class="position">{e(SYNERGETIC['tagline'])}</p>
  <p class="sub">{e(SYNERGETIC['home_lead'][lang])}</p>
  <div class="grid five">{''.join(f'<div class="card"><div class="num">{i:02d}</div><h3>{e(st["title"])}</h3></div>' for i, st in enumerate(SYNERGETIC['stages'], 1))}</div>
  <a class="btn" href="synergetic-solutions.html">{e(UI['more'][lang])}</a>
  <a class="btn ghost" href="{'../' if lang == 'ro' else ''}insights/">{e(UI['insights'][lang])}</a>
</div></section>
<section id="lab" class="dark"><div class="wrap">
  <h2>{e(LAB['title'][lang])}</h2><p class="sub">{e(LAB['sub'][lang])}</p>
  <div class="grid">{lab}</div>
</div></section>
<section id="evidence"><div class="wrap">
  <h2>{e(h['ev_h'][lang])}</h2><ul class="evidence">{evidence}</ul>
</div></section>
<section id="contact" class="alt"><div class="wrap">
  <h2>{e(h['contact_h'][lang])}</h2><p class="sub">{e(h['contact_sub'][lang])}</p>
  <dl>
    <dt>{e(T['legal'][lang])}</dt><dd>{e(ORG['legal_name'])}</dd>
    <dt>{e(T['activity'][lang])}</dt><dd>{e(T['caen'][lang])}</dd>
    <dt>{e(T['address'][lang])}</dt><dd>{e(ORG['street'])}, 077125 Măgurele, Ilfov, România</dd>
    <dt>CUI · {e(T['reg'][lang])}</dt><dd>{ORG['cui']} · {ORG['reg']}</dd>
    <dt>EU PIC · D-U-N-S</dt><dd>{ORG['pic']} · {ORG['duns']}</dd>
    <dt>Email</dt><dd><a href="mailto:{ORG['email']}">{ORG['email']}</a></dd>
    <dt>{e(T['social'][lang])}</dt><dd>{' · '.join(f'<a href="{u}">{n}</a>' for n, u in ORG['social'])}</dd>
  </dl>
  <div>{contacts}</div>
</div></section>
"""
    title = "CCTI — Expanding Horizons | " + T["name"][lang]
    page(lang, "", title, h["meta"][lang], body, jsonld=[org_ld()])


def product(lang: str, p: dict) -> None:
    rows = "".join(
        f'<dt>{e(label[lang])}</dt><dd>{e(p[key][lang])}</dd>'
        for key, label in UI["product_fields"]
    )
    links = " · ".join(f'<a href="{u}">{e(n)}</a>' for n, u in p["links"])
    ev = "".join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in p.get("evidence", []))
    body = f"""
<div class="wrap page">
  <div class="eyebrow">{e(p['domain'][lang])} · {e(p['stage'][lang])}</div>
  <h1>{e(p['name'])}</h1>
  <p class="lead">{e(p['short'][lang])}</p>
  <dl class="sheet">{rows}</dl>
  {f'<h2>{e(UI["public"][lang])}</h2><ul class="evidence">{ev}</ul>' if ev else ''}
  <p class="links">{links}</p>
  <a class="btn" href="mailto:{ORG['email']}?subject={e('Product collaboration — ' + p['name'])}">{e(UI['collab'][lang])}</a>
  <a class="btn ghost" href="../#products">{e(UI['back'][lang])}</a>
</div>"""
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"],
          "description": p["short"]["en"], "brand": {"@type": "Organization", "name": "CCTI"},
          "manufacturer": {"@type": "Organization", "name": ORG["legal_name"]},
          "url": url_for(lang, f"products/{p['slug']}.html"), "sameAs": [u for _, u in p["links"]]}
    page(lang, f"products/{p['slug']}.html", f"{p['name']} — CCTI", p["meta"][lang], body,
         jsonld=[ld], depth=1)


def synergetic(lang: str) -> None:
    s = SYNERGETIC
    stages = "".join(
        f'<div class="card"><div class="num">{i:02d}</div><h3>{e(st["title"])}</h3>'
        f'<p><strong>{e(UI["we_do"][lang])}</strong> {e(st["do"][lang])}</p>'
        f'<p><strong>{e(UI["result"][lang])}</strong> {e(st["result"][lang])}</p></div>'
        for i, st in enumerate(s["stages"], 1)
    )
    body = f"""
<div class="wrap page">
  <div class="eyebrow">Synergetic Solutions · by CCTI</div>
  <h1>{e(s['h1'])}</h1>
  <p class="lead">{e(s['sub'])}</p>
  <p class="position">{e(s['tagline'])}</p>
  {''.join(f'<p>{e(par)}</p>' for par in s['intro'][lang])}
  <h2>{e(s['strategy_h'][lang])}</h2>
  {''.join(f'<p>{e(par)}</p>' for par in s['strategy'][lang])}
  <h2>{e(s['stages_h'][lang])}</h2><p class="sub">{e(s['stages_sub'][lang])}</p>
  <div class="grid">{stages}</div>
  <a class="btn" href="mailto:{ORG['email']}?subject={e(CONTACT[2]['subject'])}">{e(CONTACT[2]['label'][lang])}</a>
  <a class="btn ghost" href="{'../' if lang == 'ro' else ''}insights/">{e(UI['insights'][lang])}</a>
</div>"""
    ld = {"@context": "https://schema.org", "@type": "ProfessionalService",
          "name": "Synergetic Solutions by CCTI", "slogan": "Beyond Advice",
          "provider": {"@type": "Organization", "name": ORG["legal_name"], "url": BASE + "/"},
          "areaServed": "Worldwide", "url": url_for(lang, "synergetic-solutions.html"),
          "serviceType": [st["title"] for st in s["stages"]]}
    page(lang, "synergetic-solutions.html", s["meta_title"], s["meta"][lang], body, jsonld=[ld])


def insights() -> None:
    def row(item, kind):
        return (f'<li><span class="code">[{e(item["code"])}]</span> '
                f'<a href="{item["slug"]}.html">{e(item["title"])}</a>'
                f'<span class="muted"> — {e(item["dek"])}</span></li>')
    body = f"""
<div class="wrap page">
  <div class="eyebrow">Synergetic Solutions · Insights</div>
  <h1>Insights</h1>
  <p class="lead">Short technical briefs and intervention scenarios: how CCTI thinks about a problem before it proposes a solution.</p>
  <h2>I · Technical briefs</h2><ul class="index">{''.join(row(a, 'brief') for a in ARTICLES)}</ul>
  <h2>II · Intervention scenarios</h2>
  <p class="sub">Illustrative scenarios, not client case studies. They show how we would approach a type of problem; they describe no specific client and report no results.</p>
  <ul class="index">{''.join(row(s, 'scenario') for s in SCENARIOS)}</ul>
</div>"""
    page("en", "insights/", "Insights — Synergetic Solutions by CCTI",
         "Technical briefs on LLM governance, recursive language models, hybrid RAG-RLM pipelines and innovation resistance, plus illustrative intervention scenarios.",
         body, alternate=False, depth=1)
    for item in [*ARTICLES, *SCENARIOS]:
        parts = "".join(
            f'<h2>{e(h)}</h2>' + "".join(f'<p>{e(p)}</p>' for p in ps) for h, ps in item["sections"]
        )
        refs = "".join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in item.get("refs", []))
        note = ('<p class="note">Illustrative scenario. It describes how CCTI would approach this type of problem; '
                'it is not a report of a past engagement.</p>' if item in SCENARIOS else "")
        body = f"""
<article class="wrap page">
  <div class="eyebrow">[{e(item['code'])}] · {e(item['audience'])}</div>
  <h1>{e(item['title'])}</h1>
  <p class="lead">{e(item['dek'])}</p>
  {note}{parts}
  {f'<h2>References</h2><ul class="evidence">{refs}</ul>' if refs else ''}
  <a class="btn ghost" href="./">← Insights</a>
</article>"""
        ld = {"@context": "https://schema.org", "@type": "TechArticle" if item in ARTICLES else "Article",
              "headline": item["title"], "description": item["dek"], "inLanguage": "en",
              "author": {"@type": "Organization", "name": "CCTI"},
              "publisher": {"@type": "Organization", "name": ORG["legal_name"], "logo": BASE + "/logo.png"},
              "datePublished": "2026-11-02", "url": f"{BASE}/insights/{item['slug']}.html"}
        page("en", f"insights/{item['slug']}.html", f"{item['title']} — CCTI Insights", item["dek"], body,
             alternate=False, jsonld=[ld], depth=1)


def main() -> None:
    for lang in ("en", "ro"):
        home(lang)
        synergetic(lang)
        for p in PRODUCTS:
            product(lang, p)
    insights()
    sitemap = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in PAGES)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print(f"{len(PAGES)} pagini generate")


if __name__ == "__main__":
    main()
