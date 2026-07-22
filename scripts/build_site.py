#!/usr/bin/env python3
"""Generate all Breaking Ground static HTML pages from data/*.json."""
from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = date.today().isoformat()

SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SERVICES = json.loads((DATA / "services.json").read_text(encoding="utf-8"))
PROJECTS = json.loads((DATA / "projects.json").read_text(encoding="utf-8"))
AREAS = json.loads((DATA / "service-areas.json").read_text(encoding="utf-8"))
FORM = SITE.get("formspreeEndpoint", "https://formspree.io/f/REPLACE_WITH_FORMSPREE_ID")
DOMAIN = SITE["domain"].rstrip("/")
BASE = (SITE.get("siteBase") or "").rstrip("/")
PHONE = SITE["phone"]
PHONE_TEL = SITE["phoneTel"]
EMAIL = SITE["email"]
NAME = SITE["name"]
SHORT = SITE["shortName"]
LEGAL = SITE["legalName"]
LOGO = SITE["logo"]
OG = SITE["defaultOgImage"]


def p(path: str) -> str:
    """Prefix siteBase for GitHub project Pages preview; empty on custom domain."""
    if not path.startswith("/"):
        path = "/" + path
    return f"{BASE}{path}" if BASE else path


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if BASE and rel.endswith((".html",)):
        # Rewrite root-absolute URLs for project Pages hosting
        content = content.replace('href="/', f'href="{BASE}/')
        content = content.replace("href='/", f"href='{BASE}/")
        content = content.replace('src="/', f'src="{BASE}/')
        content = content.replace("src='/", f"src='{BASE}/")
        content = content.replace('content="/', f'content="{BASE}/')
        content = content.replace('url(/', f"url({BASE}/")
        content = content.replace(
            'action="https://formspree.io',
            'action="https://formspree.io',
        )
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)


def estimate_form(default_service: str = "") -> str:
    opts = "\n".join(
        f'<option value="{esc(s["navLabel"])}"{" selected" if s["navLabel"] == default_service else ""}>{esc(s["navLabel"])}</option>'
        for s in SERVICES
    )
    return f"""
<form class="form-grid" data-bg-form method="POST" action="{esc(FORM)}" enctype="multipart/form-data">
  <input type="hidden" name="_next" value="{DOMAIN}/thank-you/" />
  <input type="hidden" name="_subject" value="New estimate request — Breaking Ground" />
  <input type="hidden" name="page" value="" />
  <label>Name<input name="name" required autocomplete="name" /></label>
  <label>Phone<input name="phone" type="tel" required autocomplete="tel" /></label>
  <label>Email<input name="email" type="email" autocomplete="email" /></label>
  <label>Job location / city<input name="job_location" required /></label>
  <label>Service needed
    <select name="service" required>
      <option value="">Select a service</option>
      {opts}
      <option value="Other">Other</option>
    </select>
  </label>
  <label>Project details<textarea name="message" placeholder="Structure type, acreage, access notes…"></textarea></label>
  <label>Best time to call<input name="best_time" /></label>
  <label>Can we text you for photos?
    <select name="can_text_photos" required>
      <option value="Yes">Yes</option>
      <option value="No">No</option>
    </select>
  </label>
  <label>Photos (optional)<input name="photos" type="file" accept="image/*" multiple /></label>
  <button class="btn btn-primary" type="submit">Request Free Estimate</button>
  <p class="form-note">Estimates are free and informational. Final pricing is confirmed in writing before work begins.</p>
</form>"""


def schema_business(extra: list | None = None) -> str:
    graph = [
        {
            "@type": ["Organization", "LocalBusiness", "HomeAndConstructionBusiness"],
            "@id": f"{DOMAIN}/#business",
            "name": SHORT,
            "legalName": LEGAL,
            "url": DOMAIN,
            "telephone": PHONE_TEL,
            "email": EMAIL,
            "foundingDate": SITE["foundingYear"],
            "description": SITE["tagline"],
            "image": DOMAIN + OG,
            "logo": {"@type": "ImageObject", "url": DOMAIN + LOGO},
            "priceRange": SITE["priceRange"],
            "openingHours": SITE["hours"],
            "address": {
                "@type": "PostalAddress",
                **SITE["address"],
            },
            "geo": {
                "@type": "GeoCoordinates",
                **SITE["geo"],
            },
            "areaServed": "Florida",
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": PHONE_TEL,
                "email": EMAIL,
                "contactType": "customer service",
                "areaServed": "US-FL",
                "availableLanguage": "English",
            },
        }
    ]
    if extra:
        graph.extend(extra)
    payload = {"@context": "https://schema.org", "@graph": graph}
    return f'<script type="application/ld+json">\n{json.dumps(payload, indent=2)}\n</script>'


def head(
    title: str,
    description: str,
    canonical: str,
    *,
    og_image: str | None = None,
    breadcrumbs: list[tuple[str, str]] | None = None,
    extra_schema: list | None = None,
) -> str:
    img = DOMAIN + (og_image or OG)
    can = canonical if canonical.startswith("http") else DOMAIN + canonical
    crumbs = breadcrumbs or [("Home", "/")]
    crumb_schema = {
        "@type": "BreadcrumbList",
        "@id": can + "#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u}
            for i, (n, u) in enumerate(crumbs)
        ],
    }
    extras = list(extra_schema or [])
    extras.append(crumb_schema)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(can)}" />
  <link rel="sitemap" type="application/xml" title="Sitemap" href="{DOMAIN}/sitemap.xml" />
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
  <meta name="author" content="{esc(LEGAL)}" />
  <meta name="geo.region" content="US-FL" />
  <meta name="geo.placename" content="Kathleen, Florida" />
  <meta name="geo.position" content="{SITE['geo']['latitude']};{SITE['geo']['longitude']}" />
  <meta name="ICBM" content="{SITE['geo']['latitude']}, {SITE['geo']['longitude']}" />
  <meta name="theme-color" content="#0f172a" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{esc(can)}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:image" content="{esc(img)}" />
  <meta property="og:site_name" content="{esc(SHORT)}" />
  <meta property="og:locale" content="en_US" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />
  <meta name="twitter:image" content="{esc(img)}" />
  <link rel="icon" href="/favicon.ico" sizes="any" />
  <link rel="icon" type="image/png" sizes="192x192" href="/assets/icons/cropped-Logo-Square-192x192.png" />
  <link rel="apple-touch-icon" href="/assets/icons/cropped-Logo-Square-192x192.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/css/style.css" />
  {schema_business(extras)}
</head>
<body>
  <div id="site-header-include"></div>
"""


def foot() -> str:
    return """
  <div id="site-footer-include"></div>
  <script src="/includes.js" defer></script>
  <script src="/assets/js/main.js" defer></script>
</body>
</html>
"""


def page_hero(h1: str, crumbs_html: str, image: str, lead: str = "") -> str:
    lead_html = f"<p class=\"hero-lead\">{esc(lead)}</p>" if lead else ""
    return f"""
  <section class="page-hero">
    <div class="page-hero__media"><img src="{esc(image)}" alt="" width="1600" height="900" /></div>
    <div class="page-hero__overlay"></div>
    <div class="page-hero__copy">
      <div class="breadcrumbs">{crumbs_html}</div>
      <h1>{esc(h1)}</h1>
      {lead_html}
    </div>
  </section>"""


def related_links(current: str = "") -> str:
    """Dense internal linking block used across content pages."""
    service_links = [
        ("/demolition/", "Demolition"),
        ("/mobile-home-demolition/", "Mobile Home Demolition"),
        ("/shed-barn-removal/", "Shed & Barn Removal"),
        ("/land-clearing/", "Land Clearing"),
        ("/tree-removal/", "Tree Removal"),
        ("/stump-removal/", "Stump Removal"),
        ("/pond-drainage/", "Pond & Drainage"),
        ("/grading-site-preparation/", "Grading & Site Prep"),
        ("/storm-debris-cleanup/", "Storm Cleanup"),
    ]
    extra_links = [
        ("/projects/", "Project Gallery"),
        ("/pricing/", "Pricing Guide"),
        ("/service-areas/", "Service Areas"),
        ("/areas/kathleen-fl/", "Kathleen"),
        ("/areas/lakeland-fl/", "Lakeland"),
        ("/areas/plant-city-fl/", "Plant City"),
        ("/areas/brooksville-fl/", "Brooksville"),
        ("/areas/tampa-fl/", "Tampa"),
        ("/about/", "About Us"),
        ("/contact/", "Request Estimate"),
    ]
    items = []
    for href, label in service_links + extra_links:
        if href.rstrip("/") == current.rstrip("/"):
            continue
        items.append(f'<a href="{esc(href)}">{esc(label)}</a>')
    grid = "\n".join(f"<div>{a}</div>" for a in items[:18])
    return f"""
<aside class="related-links reveal">
  <h3>Explore related pages</h3>
  <p>Jump to another service, city, or project page on this site.</p>
  <div class="related-links-grid">{grid}</div>
</aside>
"""


def cta_band(headline: str, blurb: str, service: str = "") -> str:
    return f"""
  <section class="cta-band">
    <div class="container cta-band-grid">
      <div>
        <p class="section-eyebrow">Free Estimates</p>
        <h2>{esc(headline)}</h2>
        <p>{esc(blurb)}</p>
        <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {esc(PHONE)}</a>
      </div>
      <div class="form-card">
        <h3>Request an Estimate</h3>
        {estimate_form(service)}
      </div>
    </div>
  </section>"""


def crumb(items: list[tuple[str, str]]) -> str:
    parts = []
    for i, (label, url) in enumerate(items):
        if i < len(items) - 1:
            parts.append(f'<a href="{esc(url)}">{esc(label)}</a>')
        else:
            parts.append(f"<span>{esc(label)}</span>")
    return " / ".join(parts)


# ── Content builders ──────────────────────────────────────────────


def service_body(svc: dict) -> str:
    slug = svc["slug"]
    bodies = {
        "demolition": """
<p>Breaking Ground focuses on <strong>smaller demolition and structure removal</strong> for homeowners, investors, and property managers across Central Florida. We take down mobile homes, sheds, barns, decks, and similar light structures, then haul the debris so your lot is ready for the next chapter.</p>
<p>We are an owner-operated father-and-son crew based in Kathleen. Andrew brings decades of heavy-equipment experience; Guy handles project coordination and customer communication. You work directly with the people running the machines — not a call center.</p>
<p>Permit requirements vary by property, structure, and jurisdiction. Polk County and many Florida cities require a demolition permit for structure removal. We evaluate each project individually and coordinate required permitting based on the scope of work. We do not perform asbestos abatement; if regulated materials are discovered, work pauses until qualified specialty contractors handle them.</p>
<h3>What we demolish and remove</h3>
<ul>
<li>Mobile homes and manufactured homes (singlewide and doublewide)</li>
<li>Sheds, barns, and outbuildings</li>
<li>Decks, porches, and carports attached to light structures</li>
<li>Storm-damaged or fire-damaged light structures (case by case)</li>
<li>Debris piles left after prior teardown attempts</li>
</ul>
<h3>What this service is not</h3>
<p>We do not market unrestricted commercial high-rise demolition or large engineered building teardown as a general contracting specialty. If your project involves a complex occupied structure, hazardous materials, or specialized engineering, we will say so clearly and help you understand next steps.</p>
<h3>Our typical process</h3>
<ol>
<li>Phone or form estimate with photos and site details</li>
<li>On-site walk-through when needed</li>
<li>Written scope covering teardown, haul-off, and grading expectations</li>
<li>Utility disconnect confirmation and permit coordination as required</li>
<li>Demolition, debris removal, and final cleanup</li>
</ol>
""",
        "mobile-home-demolition": """
<p>Mobile home and manufactured home removal is our priority service. Aging parks, inherited lots, storm-damaged units, and rebuild sites across Florida often start with a clean, complete demo and haul-off — and that is exactly the work we are built for.</p>
<p>Whether you have a vacant singlewide in Polk County or a doublewide that needs to come down before new construction, Breaking Ground brings equipment, hauling capacity, and owner-level accountability to the job.</p>
<p>Florida continues to see elevated teardown and redevelopment activity. Property owners clearing older housing stock for rebuilds or land sales need a crew that can remove the structure, manage debris, and leave a usable pad — without overpromising on scopes we do not perform.</p>
<h3>What affects mobile home demo pricing</h3>
<ul>
<li>Singlewide vs doublewide vs multi-section</li>
<li>Access roads, trees, and neighboring structures</li>
<li>Foundation type (pier, block, slab)</li>
<li>Attached porches, carports, and decks</li>
<li>Utility disconnect status</li>
<li>Disposal fees and haul distance</li>
<li>Permit and notification requirements in your city or county</li>
</ul>
<p>Ballpark ranges on our <a href="/pricing/">pricing page</a> help set expectations. Every job still needs a written estimate after we understand the site.</p>
<h3>Permits and utilities</h3>
<p>Most Florida jurisdictions require a demolition permit for manufactured home removal. Utility disconnection (electric, water, sewer/septic) must be confirmed before teardown. We discuss who pulls permits and who coordinates disconnects before work starts so responsibilities are clear.</p>
""",
        "shed-barn-removal": """
<p>Outdated sheds, leaning barns, and unused outbuildings take up space and create liability. Breaking Ground removes these structures, hauls the debris, and cleans the footprint so you can reclaim the yard or prepare for a new build.</p>
<p>Backyard access is often the hard part. We plan equipment selection around gates, fences, and overhead lines so the job finishes without unnecessary property damage.</p>
<h3>Common projects</h3>
<ul>
<li>Residential storage sheds and workshops</li>
<li>Agricultural barns and lean-tos</li>
<li>Carports and detached covered structures</li>
<li>Collapsed or storm-damaged outbuildings</li>
</ul>
<p>If concrete pads or footings need removal, we discuss that as a separate line item so your scope stays transparent.</p>
""",
        "land-clearing": """
<p>Need a wooded lot opened for a home site, driveway, or pasture? Breaking Ground provides residential and light-commercial land clearing, brush removal, and lot cleanup throughout Polk County and nearby Central Florida communities.</p>
<p>We clear vegetation, remove underbrush, and help get ground ready for the next step — whether that is grading, a building pad, or simply usable open land. Project photos from Brooksville and surrounding areas show the kind of dense Florida scrub we regularly handle.</p>
<p>For specialized forestry mulching programs in core Auburndale and Winter Haven markets, we may refer complementary partners when that approach better fits the property. Our strength is equipment-driven clearing combined with demolition and haul-off when structures are also in the way.</p>
<h3>Land clearing services</h3>
<ul>
<li>Residential lot clearing</li>
<li>Brush and overgrowth removal</li>
<li>Fence-line and trail opening</li>
<li>Build-site vegetation removal</li>
<li>Debris haul-off after clearing</li>
</ul>
""",
        "tree-removal": """
<p>From unwanted backyard trees to storm-fallen timber, Breaking Ground provides tree removal and equipment-assisted cleanup for Central Florida properties. We focus on practical removals where heavy equipment can safely access the work zone.</p>
<p>Hazardous trees over occupied structures or crane-assisted specialty removals may require additional partners. We will tell you honestly when a job needs different equipment or a climbing crew.</p>
<h3>Tree work we perform</h3>
<ul>
<li>Full tree removal with equipment support</li>
<li>Fallen tree cleanup after storms</li>
<li>Lot clearing tree removal tied to build prep</li>
<li>Log and brush haul-off</li>
</ul>
""",
        "stump-removal": """
<p>Stump grinding leaves roots behind. When you need the stump and root ball gone so you can grade, plant, or build, excavation is the better answer. Breaking Ground specializes in stump excavation and removal throughout Lakeland, Kathleen, and Polk County.</p>
<p>Our project gallery includes large Lakeland stump excavations where grinding alone would not have delivered a clean result. We dig, extract, backfill expectations, and haul debris according to the written scope.</p>
""",
        "pond-drainage": """
<p>Breaking Ground provides pond cleanup support, ditch clearing, swale restoration, and drainage-related earthwork subject to site conditions and applicable permitting. We excavate and move dirt — we do not design engineered drainage systems or guarantee hydrological outcomes.</p>
<p>Projects that affect wetlands, alter surface-water flow, or involve public rights-of-way may require Environmental Resource Permits or local approvals. We evaluate each site and coordinate specialty requirements based on scope.</p>
<p>Safer framing for what we do: excavation support, cleanup, and earthwork — not “we know it all” drainage design.</p>
""",
        "grading-site-preparation": """
<p>After demolition or clearing, many properties need rough grading, fill placement, or a cleaner pad before the next contractor arrives. Breaking Ground provides grading and site preparation support for residential and light-commercial projects in Central Florida.</p>
<p>Scopes commonly include rough grade after structure removal, spreading fill, driveway prep, and shaping disturbed ground for drainage away from future building pads — always within the limits of the written estimate.</p>
""",
        "storm-debris-cleanup": """
<p>Hurricanes and seasonal storms leave yards buried in limbs, sheets of debris, and downed trees. Breaking Ground provides storm debris cleanup and haul-off for Polk County and Central Florida property owners who need a crew that shows up with equipment and leaves the site clear.</p>
<p>After major storm events, schedule can tighten quickly. Contact us early with photos so we can prioritize access, safety, and disposal logistics.</p>
""",
    }
    base = bodies.get(slug, f"<p>{esc(svc['meta'])}</p>")
    faqs = f"""
<div class="faq">
  <details open><summary>Do you offer free estimates?</summary><p>Yes. Estimates are free. Final pricing is confirmed in a written scope before work begins.</p></details>
  <details><summary>Do you handle permits?</summary><p>Permit requirements vary by jurisdiction and structure. We evaluate each project and coordinate required permitting based on the scope of work.</p></details>
  <details><summary>Where do you work?</summary><p>We are based in Kathleen and serve Central Florida routinely. Larger demolition and site jobs are considered statewide by project scope.</p></details>
  <details><summary>Are you a general contractor?</summary><p>No. We provide smaller demolition, structure removal, land clearing, and related site services as an owner-operated equipment company.</p></details>
</div>"""
    # Expand word count with process + CTA prose
    expand = f"""
<h3>Why property owners call {SHORT}</h3>
<p>Direct owner communication, real project photography, and a demolition-first mindset for the jobs Florida lots actually need — mobile homes, sheds, storm messes, and clearing that supports the next use of the land. Call <a href="tel:{PHONE_TEL}">{esc(PHONE)}</a> or use the form below.</p>
<p>Every estimate includes a clear description of what is included: teardown or clearing, debris handling, and what is excluded (such as hazardous material abatement or engineered design). That clarity protects both sides and keeps projects moving.</p>
<p>If your property needs both structure removal and land clearing, we can often combine scopes in one mobilization — reducing duplicate mobilizations and disposal trips. Ask about bundling when you request your estimate on our <a href="/contact/">contact page</a>, review <a href="/pricing/">pricing ranges</a>, or browse the <a href="/projects/">project gallery</a>.</p>
<p>Common next steps from this page: <a href="/mobile-home-demolition/">mobile home demolition</a>, <a href="/land-clearing/">land clearing</a>, <a href="/stump-removal/">stump removal</a>, <a href="/areas/lakeland-fl/">Lakeland</a>, <a href="/areas/kathleen-fl/">Kathleen</a>, and <a href="/service-areas/">all service areas</a>.</p>
{faqs}
"""
    return base + expand


def area_body(area: dict) -> str:
    short = area["shortName"]
    county = area["county"]
    angle = area.get("angle", "full")
    nearby = ", ".join(area.get("nearby", [])[:4])
    demo_lead = f"""
<p>Looking for <strong>mobile home demolition or light structure removal in {esc(short)}</strong>? Breaking Ground is an owner-operated crew based in Kathleen, Florida. We serve {esc(county)} and consider larger demolition jobs across the state by scope and schedule.</p>
<p>Florida property owners clearing aging manufactured homes, sheds, and outbuildings need a practical equipment crew — not marketing fluff. We provide written estimates, discuss permits, and haul debris so your {esc(short)} lot is ready for sale, rebuild, or cleanup.</p>
"""
    full_extra = f"""
<p>In addition to demolition, property owners in {esc(short)} also call us for land clearing, tree and stump removal, grading support, and storm debris cleanup. Demolition remains our lead specialty; clearing and earthwork are available when they fit the site.</p>
"""
    demo_only_note = f"""
<p>For {esc(short)}, our published focus is mobile-home and light-structure demolition plus related debris removal. Land clearing may be available as a secondary scope on the same property when it supports the demolition or lot reset.</p>
"""
    mid = full_extra if angle == "full" else demo_only_note
    return f"""
{demo_lead}
{mid}
<h3>Services commonly requested in {esc(short)}</h3>
<ul>
<li><a href="/mobile-home-demolition/">Mobile home demolition</a></li>
<li><a href="/demolition/">Small structure demolition</a></li>
<li><a href="/shed-barn-removal/">Shed and barn removal</a></li>
{"<li><a href='/land-clearing/'>Land clearing</a></li><li><a href='/stump-removal/'>Stump removal</a></li>" if angle == "full" else ""}
<li><a href="/storm-debris-cleanup/">Storm debris cleanup</a></li>
</ul>
<h3>Local context</h3>
<p>{esc(short)} sits in {esc(county)}. Nearby communities we also serve include {esc(nearby)}. Travel and scheduling for {esc(short)} jobs depend on project size — ask when you request your estimate.</p>
<p>Permit rules differ between cities and counties. Structure demolition often requires a local permit and utility disconnect confirmation. We review those requirements as part of scoping work in {esc(short)}.</p>
<h3>How to get started</h3>
<p>Send photos of the structure or lot, note gate widths and overhead lines, and tell us your goal (rebuild, sell, clean up). Call <a href="tel:{PHONE_TEL}">{esc(PHONE)}</a> or use the estimate form. Free estimates; written confirmation before work begins.</p>
<p>Breaking Ground Land Services and Demolition LLC was founded in 2024 by Guy and Andrew McMillen. Andrew has operated heavy equipment for decades. That experience shows up in how we plan access, sequence teardown, and leave sites cleaner than we found them.</p>
<div class="faq">
<details open><summary>Do you serve all of {esc(short)}?</summary><p>Yes — we consider jobs throughout {esc(short)} and surrounding {esc(county)}, subject to schedule and scope.</p></details>
<details><summary>Can you demolish a mobile home in {esc(short)}?</summary><p>Mobile home and manufactured home removal is our priority service. Share photos and location details for an estimate.</p></details>
<details><summary>Is land clearing available?</summary><p>{"Yes, land clearing and related site work are available in our Central Florida coverage area." if angle == "full" else "Land clearing may be offered as a secondary scope tied to demolition or lot reset. Ask when you request your estimate."}</p></details>
</div>
"""


# ── Page generators ───────────────────────────────────────────────


def build_home() -> None:
    tiles = "".join(
        f"""
        <a class="service-tile reveal" href="{esc(s['path'])}">
          <img src="{esc(s['heroImage'])}" alt="" loading="lazy" />
          <div class="service-tile__body">
            <h3>{esc(s['navLabel'])}</h3>
            <p>{esc(s['meta'][:110])}…</p>
          </div>
        </a>"""
        for s in SERVICES[:6]
    )
    projects = "".join(
        f"""
        <article class="project-card reveal">
          <a href="{esc(p['path'])}"><img src="{esc(p['image'])}" alt="{esc(p['h1'])}" loading="lazy" /></a>
          <div class="project-card__body">
            <p class="project-meta">{esc(p['city'])} · {esc(p['service'])}</p>
            <h3><a href="{esc(p['path'])}">{esc(p['h1'])}</a></h3>
            <p>{esc(p['summary'])}</p>
          </div>
        </article>"""
        for p in PROJECTS[:4]
    )
    html_out = (
        head(
            f"{SHORT} | Mobile Home Demolition & Land Services in Central Florida",
            "Owner-operated mobile home demolition, shed removal, land clearing, and site work based in Kathleen, FL. Free estimates.",
            "/",
            breadcrumbs=[("Home", "/")],
        )
        + f"""
  <section class="hero-stage">
    <div class="hero">
      <div class="hero__media"><img src="/assets/images/hero/IMG_8286-scaled.jpg" alt="Breaking Ground equipment on a Florida job site" width="1920" height="1080" fetchpriority="high" /></div>
      <div class="hero__overlay"></div>
      <div class="hero__copy">
        <p class="hero-eyebrow">Kathleen · Lakeland · Central Florida</p>
        <h1>Breaking Ground</h1>
        <p class="hero-lead">Mobile home demolition, light structure removal, and land services — father-and-son owned, equipment ready.</p>
        <div class="hero__actions">
          <a class="btn btn-primary" href="/contact/">Request Free Estimate</a>
          <a class="btn btn-ghost" href="tel:{PHONE_TEL}">{esc(PHONE)}</a>
        </div>
      </div>
    </div>
  </section>
  <section class="section-pad">
    <div class="container split">
      <div class="reveal">
        <p class="section-eyebrow">Owner Operated</p>
        <h2>Demolition-first site work for Florida lots</h2>
        <div class="prose">
          <p>Breaking Ground Land Services and Demolition LLC clears the obstacles standing between you and usable land — starting with mobile homes, sheds, and light structures, then finishing with haul-off, clearing, and grading support when the job calls for it.</p>
          <p>Based in Kathleen and serving Central Florida, with larger demolition jobs considered statewide by scope.</p>
        </div>
        <ul class="feature-list">
          <li><span class="mark">01</span><span>Priority: mobile home &amp; light structure demolition</span></li>
          <li><span class="mark">02</span><span>Father-and-son crew — talk directly to the owners</span></li>
          <li><span class="mark">03</span><span>Real project photos from Polk County &amp; beyond</span></li>
        </ul>
      </div>
      <div class="media-stage reveal"><img src="/assets/images/projects/IMG_8345-scaled.jpg" alt="Demolition and site work in progress" /></div>
    </div>
  </section>
  <section class="section-pad" style="background:#e2e8f0;">
    <div class="container">
      <p class="section-eyebrow">Services</p>
      <h2>What we take on</h2>
      <div class="service-grid">{tiles}</div>
      <p style="margin-top:1.5rem;"><a class="btn btn-dark" href="/services/">View all services</a>
      <a class="btn btn-primary" href="/mobile-home-demolition/" style="margin-left:0.5rem;">Mobile Home Demolition</a></p>
    </div>
  </section>
  <section class="section-pad">
    <div class="container">
      <p class="section-eyebrow">Projects</p>
      <h2>Recent work</h2>
      <div class="project-grid">{projects}</div>
      <p style="margin-top:1.5rem;"><a class="btn btn-dark" href="/projects/">Full project gallery</a>
      <a class="btn btn-primary" href="/areas/lakeland-fl/" style="margin-left:0.5rem;">Lakeland service area</a></p>
      {related_links("/")}
    </div>
  </section>
"""
        + cta_band(
            "Ready to clear the structure or the lot?",
            "Tell us about your mobile home, shed, or land clearing project. Free estimates for Central Florida and statewide-by-scope jobs.",
            "Mobile Home Demolition",
        )
        + foot()
    )
    write("index.html", html_out)


def build_about() -> None:
    body = f"""
{page_hero("About Breaking Ground", crumb([("Home","/"),("About","/about/")]), "/assets/images/projects/IMG_9164-scaled.jpg", "Father-and-son. Equipment-driven. Built in 2024 on decades of field experience.")}
<section class="section-pad"><div class="container split">
<div class="prose reveal">
<p class="section-eyebrow">Our Story</p>
<h2>Guy &amp; Andrew McMillen</h2>
<p>Guy McMillen started Breaking Ground Land Services and Demolition LLC with his father, Andrew McMillen, in 2024. Guy handles customer-facing operations and project coordination. Andrew brings heavy-equipment experience dating back to 1975, including prior ownership of a tree company and fieldwork involving land clearing, demolition support, underground utilities, and road construction environments.</p>
<p>The company is young. The experience behind the controls is not. We keep claims honest: founded in 2024, backed by decades of equipment work — never “serving Florida since 1975” under this LLC name.</p>
<p>We prioritize mobile home and light-structure demolition, then support land clearing, tree and stump work, grading, and storm cleanup for property owners who want a direct line to the crew.</p>
<div class="stat-row">
<div><strong>2024</strong><span>LLC founded</span></div>
<div><strong>1975</strong><span>Andrew’s equipment start</span></div>
<div><strong>2</strong><span>Owner-operators</span></div>
</div>
</div>
<div class="media-stage reveal"><img src="/assets/images/brand/Logo-Square-scaled-1024x1024.png" alt="Breaking Ground logo" style="object-fit:contain;background:#241811;padding:2rem;" /></div>
</div></section>
""" + related_links("/about/") + cta_band("Talk with the owners", "Call or send project photos for a free estimate.", "Demolition")
    write(
        "about/index.html",
        head(
            f"About Us | {SHORT}",
            "Meet Guy and Andrew McMillen — father-and-son owners of Breaking Ground Land Services and Demolition in Kathleen, Florida.",
            "/about/",
            breadcrumbs=[("Home", "/"), ("About", "/about/")],
        )
        + body
        + foot(),
    )


def build_contact() -> None:
    body = f"""
{page_hero("Request an Estimate", crumb([("Home","/"),("Contact","/contact/")]), "/assets/images/hero/IMG_9083-scaled.jpg")}
<section class="section-pad"><div class="container cta-band-grid">
<div class="prose">
<p class="section-eyebrow">Contact</p>
<h2>Tell us about the job</h2>
<p>Phone: <a href="tel:{PHONE_TEL}">{esc(PHONE)}</a><br/>Email: <a href="mailto:{EMAIL}">{esc(EMAIL)}</a></p>
<p>Based in Kathleen, Florida. Central Florida regularly; statewide by scope for larger demolition and site jobs.</p>
<p>Hours: Monday–Saturday, 7:00 a.m.–6:00 p.m.</p>
</div>
<div class="form-card"><h3>Estimate form</h3>{estimate_form()}</div>
</div></section>
"""
    write(
        "contact/index.html",
        head(
            f"Contact & Free Estimate | {SHORT}",
            f"Request a free estimate from Breaking Ground. Call {PHONE} or send project details online.",
            "/contact/",
            breadcrumbs=[("Home", "/"), ("Contact", "/contact/")],
        )
        + body
        + foot(),
    )


def build_services_hub() -> None:
    cards = "".join(
        f'<a class="service-tile reveal" href="{esc(s["path"])}"><img src="{esc(s["heroImage"])}" alt="" loading="lazy" /><div class="service-tile__body"><h3>{esc(s["navLabel"])}</h3><p>{esc(s["meta"][:120])}…</p></div></a>'
        for s in SERVICES
    )
    body = f"""
{page_hero("Services", crumb([("Home","/"),("Services","/services/")]), "/assets/images/projects/IMG_8495-scaled.jpg", "Demolition first — clearing and site work when the lot needs more.")}
<section class="section-pad"><div class="container"><div class="service-grid">{cards}</div>{related_links("/services/")}</div></section>
""" + cta_band("Not sure which service fits?", "Describe the property and we will help scope it.", "Demolition")
    write(
        "services/index.html",
        head(
            f"Demolition & Land Services | {SHORT}",
            "Mobile home demolition, shed removal, land clearing, stump excavation, and storm cleanup in Central Florida.",
            "/services/",
            breadcrumbs=[("Home", "/"), ("Services", "/services/")],
        )
        + body
        + foot(),
    )


def build_service_pages() -> None:
    for s in SERVICES:
        faq_schema = {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "Do you offer free estimates?",
                    "acceptedAnswer": {"@type": "Answer", "text": "Yes. Estimates are free and informational until confirmed in writing."},
                },
                {
                    "@type": "Question",
                    "name": f"Do you provide {s['navLabel']} in Central Florida?",
                    "acceptedAnswer": {"@type": "Answer", "text": f"Yes. Breaking Ground provides {s['navLabel']} from our Kathleen base across Central Florida, with larger jobs considered statewide by scope."},
                },
            ],
        }
        service_schema = {
            "@type": "Service",
            "name": s["navLabel"],
            "provider": {"@id": f"{DOMAIN}/#business"},
            "areaServed": "Florida",
            "url": DOMAIN + s["path"],
            "description": s["meta"],
        }
        body = f"""
{page_hero(s["h1"], crumb([("Home","/"),("Services","/services/"),(s["navLabel"], s["path"])]), s["heroImage"], s["meta"])}
<section class="section-pad"><div class="container split">
<div class="prose reveal">{service_body(s)}{related_links(s["path"])}</div>
<div class="media-stage reveal"><img src="{esc(s["heroImage"])}" alt="{esc(s["h1"])}" /></div>
</div></section>
""" + cta_band(f"Get a {s['navLabel'].lower()} estimate", "Share photos and your city for a faster response.", s["navLabel"])
        write(
            f"{s['slug']}/index.html",
            head(
                s["title"],
                s["meta"],
                s["path"],
                og_image=s["heroImage"],
                breadcrumbs=[("Home", "/"), ("Services", "/services/"), (s["navLabel"], s["path"])],
                extra_schema=[service_schema, faq_schema],
            )
            + body
            + foot(),
        )


def build_projects() -> None:
    cards = "".join(
        f"""<article class="project-card reveal"><a href="{esc(p['path'])}"><img src="{esc(p['image'])}" alt="" loading="lazy" /></a>
        <div class="project-card__body"><p class="project-meta">{esc(p['city'])} · {esc(p['service'])}</p>
        <h3><a href="{esc(p['path'])}">{esc(p['h1'])}</a></h3><p>{esc(p['summary'])}</p></div></article>"""
        for p in PROJECTS
    )
    write(
        "projects/index.html",
        head(
            f"Project Gallery | {SHORT}",
            "Before-and-after land clearing, stump excavation, shed demolition, and storm cleanup projects across Central Florida.",
            "/projects/",
            breadcrumbs=[("Home", "/"), ("Projects", "/projects/")],
        )
        + page_hero("Projects", crumb([("Home", "/"), ("Projects", "/projects/")]), PROJECTS[0]["image"])
        + f'<section class="section-pad"><div class="container"><div class="project-grid">{cards}</div>{related_links("/projects/")}</div></section>'
        + cta_band("Have a similar property?", "Send photos for a free estimate.")
        + foot(),
    )
    for p in PROJECTS:
        gallery = "".join(
            f'<div class="media-stage" style="margin-bottom:1rem;"><img src="{esc(img)}" alt="{esc(p["h1"])}" loading="lazy" /></div>'
            for img in p.get("images", [p["image"]])
        )
        body = f"""
{page_hero(p["h1"], crumb([("Home","/"),("Projects","/projects/"),(p["h1"], p["path"])]), p["image"])}
<section class="section-pad"><div class="container split">
<div class="prose">
<p class="project-meta">{esc(p["city"])} · <a href="{esc(p["servicePath"])}">{esc(p["service"])}</a></p>
<p>{esc(p["summary"])}</p>
<h3>Challenge</h3><p>{esc(p["challenge"])}</p>
<p>This project is part of our public portfolio for Breaking Ground Land Services and Demolition. Results vary by site access, vegetation, structure type, and disposal requirements.</p>
<p><a class="btn btn-primary" href="/contact/">Request a similar estimate</a>
<a class="btn btn-dark" href="{esc(p["servicePath"])}" style="margin-left:0.5rem;">{esc(p["service"])} service</a></p>
{related_links(p["path"])}
</div>
<div>{gallery}</div>
</div></section>
"""
        write(
            f"projects/{p['slug']}/index.html",
            head(
                p["title"],
                p["meta"],
                p["path"],
                og_image=p["image"],
                breadcrumbs=[("Home", "/"), ("Projects", "/projects/"), (p["h1"], p["path"])],
            )
            + body
            + foot(),
        )


def build_pricing() -> None:
    body = f"""
{page_hero("Pricing Guide", crumb([("Home","/"),("Pricing","/pricing/")]), "/assets/images/projects/IMG_8495-scaled.jpg", "Ballpark ranges for planning — every job needs a written estimate.")}
<section class="section-pad"><div class="container prose policy-wrap">
<p>These ranges reflect typical Central Florida residential and light-commercial work in 2026. Access, disposal fees, permits, hazardous materials, and attachments can move a project up or down. <strong>Nothing on this page is a bid.</strong></p>
<table class="price-table">
<thead><tr><th>Service</th><th>Typical planning range</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>Mobile home demolition (singlewide)</td><td>$3,000 – $6,500</td><td>Access, foundation, attachments vary</td></tr>
<tr><td>Mobile home demolition (doublewide)</td><td>$5,000 – $11,000</td><td>Multi-section and site constraints add cost</td></tr>
<tr><td>Shed / small outbuilding removal</td><td>$800 – $3,500</td><td>Size, concrete, haul distance</td></tr>
<tr><td>Barn / larger outbuilding</td><td>$2,500 – $8,000+</td><td>Quoted after walk-through</td></tr>
<tr><td>Stump excavation (per stump)</td><td>$250 – $1,200+</td><td>Diameter and root mass drive price</td></tr>
<tr><td>Residential land clearing</td><td>$2,000 – $8,000+/lot</td><td>Density, acreage, haul-off</td></tr>
<tr><td>Storm debris cleanup</td><td>Hourly or project bid</td><td>Volume and disposal fees</td></tr>
</tbody>
</table>
<p class="price-note">Disposal, landfill, and permit fees may be pass-through items. Asbestos or regulated materials are excluded and require specialty contractors if discovered.</p>
<h2>What we need for an accurate estimate</h2>
<ul>
<li>Address or city and gate/access notes</li>
<li>Photos of the structure or lot</li>
<li>Singlewide / doublewide / shed dimensions if known</li>
<li>Whether utilities are disconnected</li>
<li>Your end goal (rebuild, sell, clean up)</li>
</ul>
</div></section>
""" + related_links("/pricing/") + cta_band("Get your written estimate", "Free to request — binding only when confirmed in writing.")
    write(
        "pricing/index.html",
        head(
            f"Pricing Guide | {SHORT}",
            "Planning ranges for mobile home demolition, shed removal, stump excavation, and land clearing in Central Florida.",
            "/pricing/",
            breadcrumbs=[("Home", "/"), ("Pricing", "/pricing/")],
        )
        + body
        + foot(),
    )


def build_policies() -> None:
    policies = [
        (
            "privacy-policy",
            "Privacy Policy",
            f"""
<p>This Privacy Policy describes how {LEGAL} (“we,” “us”) collects and uses information through {DOMAIN}.</p>
<h2>Information we collect</h2>
<p>When you submit an estimate form or email us, we may collect your name, phone number, email address, job location, project details, and any photos you upload. We also receive standard server and analytics data such as IP address and pages visited if analytics tools are enabled.</p>
<h2>How we use information</h2>
<p>We use contact details to respond to estimate requests, schedule work, and communicate about projects. We do not sell personal information.</p>
<h2>Form processing</h2>
<p>Estimate forms may be processed by Formspree or a similar form provider acting as a processor on our behalf.</p>
<h2>Sharing</h2>
<p>We may share information with service providers who help us operate the website or deliver services (for example, email delivery). We may disclose information if required by law.</p>
<h2>Data retention</h2>
<p>We retain inquiry and project communications as needed for business and legal purposes.</p>
<h2>Contact</h2>
<p>Questions: <a href="mailto:{EMAIL}">{EMAIL}</a> or {PHONE}.</p>
""",
        ),
        (
            "terms-of-service",
            "Terms of Service",
            f"""
<p>These Terms of Service govern use of {DOMAIN}, operated by {LEGAL}.</p>
<h2>Website information is not a contract</h2>
<p>Content on this site is for general information about our demolition, clearing, and site services. It is <strong>not</strong> a binding contract, bid, warranty, or permit approval unless confirmed in a written estimate or signed agreement for a specific project.</p>
<h2>Estimates</h2>
<p>Free estimates are informational. Final pricing, scope, timelines, disposal fees, and responsibilities are confirmed in writing for each project.</p>
<h2>Services and limitations</h2>
<p>We provide smaller demolition and structure removal (including mobile homes, sheds, and similar light structures), land clearing, tree and stump work, grading support, and related site services. We are not marketing ourselves as a licensed general contractor for unrestricted building demolition. Permit requirements vary by jurisdiction.</p>
<h2>Hazardous materials</h2>
<p>We do not perform asbestos abatement. If regulated materials are identified or reasonably suspected, work may stop until qualified specialty contractors address them.</p>
<h2>Payment</h2>
<p>Payment terms, deposits, and progress payments are stated in the written agreement for each job. See also our <a href="/payment-deposit-policy/">Payment &amp; Deposit Policy</a>.</p>
<h2>Limitation of liability</h2>
<p>To the fullest extent permitted by Florida law, we are not liable for indirect or consequential damages arising from website use. Project liability is governed by the written service agreement, not these website terms.</p>
<p><em>These website terms are not a substitute for an attorney-reviewed construction contract.</em></p>
""",
        ),
        (
            "payment-deposit-policy",
            "Payment & Deposit Policy",
            f"""
<p>This policy explains how {LEGAL} typically handles deposits and payments. Specific terms in a written project agreement control if they differ.</p>
<h2>Estimates vs. invoices</h2>
<p>Website ranges and verbal discussions are not invoices. Work proceeds under a written scope and payment schedule.</p>
<h2>Deposits</h2>
<p>Projects may require a commencement deposit before mobilization. Deposits secure schedule and cover early costs such as permitting coordination, disposal arrangements, and crew allocation. Deposit amounts and refund conditions (if any) are stated in writing.</p>
<h2>Progress and final payment</h2>
<p>Larger jobs may use progress payments tied to milestones (for example, structure down, debris hauled, final grade). Final payment is due upon completion of the written scope unless otherwise agreed.</p>
<h2>Nonpayment</h2>
<p>We may suspend or stop work if payments are late under the agreement. You remain responsible for work performed, mobilization, disposal fees incurred, and permitted charges under Florida law.</p>
<h2>Change orders</h2>
<p>Extra work outside the written scope requires a change order and may require additional payment before that work proceeds.</p>
<h2>Disposal and third-party fees</h2>
<p>Landfill, transfer station, and certain permit fees may be billed as pass-through costs when disclosed in the estimate.</p>
<h2>Disputes</h2>
<p>Contact us promptly at {PHONE} or {EMAIL} to resolve billing questions. Keeping communication open prevents most payment disputes.</p>
""",
        ),
        (
            "image-use-policy",
            "Image Use Policy",
            f"""
<p>Photographs and videos on {DOMAIN} show real projects associated with {LEGAL} unless otherwise noted.</p>
<h2>Our use</h2>
<p>We may photograph job sites for documentation, safety, training, and marketing — including this website and social profiles — unless a property owner objects in writing before work begins.</p>
<h2>Your privacy</h2>
<p>We avoid publishing faces of non-employees and personal documents when practical. Address-level details may be generalized (city/county) on public pages.</p>
<h2>Third-party use</h2>
<p>Images are owned by us or used with permission. You may not scrape, republish, or commercially reuse site images without written permission.</p>
<h2>Requests</h2>
<p>To request removal of a project photo, email {EMAIL} with the page URL.</p>
""",
        ),
    ]
    for slug, title, content in policies:
        path = f"/{slug}/"
        write(
            f"{slug}/index.html",
            head(
                f"{title} | {SHORT}",
                f"{title} for {LEGAL}.",
                path,
                breadcrumbs=[("Home", "/"), (title, path)],
            )
            + page_hero(title, crumb([("Home", "/"), (title, path)]), OG)
            + f'<section class="section-pad"><div class="container prose policy-wrap">{content}</div></section>'
            + foot(),
        )


def build_service_areas() -> None:
    areas = AREAS["areas"]
    tier_a = [a for a in areas if a["tier"] == "A"]
    tier_b = [a for a in areas if a["tier"] == "B"]

    def links(items: list) -> str:
        return "".join(
            f'<a href="/areas/{esc(a["slug"])}/">{esc(a["shortName"])}</a>' for a in items
        )

    hub = f"""
{page_hero("Service Areas", crumb([("Home","/"),("Service Areas","/service-areas/")]), "/assets/images/projects/IMG_0249-scaled.jpg", AREAS["coverageDisclaimer"])}
<section class="section-pad"><div class="container">
<p class="section-eyebrow">Tier A — Local Core</p>
<h2>Kathleen, Lakeland &amp; nearby</h2>
<div class="area-grid">{links(tier_a)}</div>
<p class="section-eyebrow" style="margin-top:2.5rem;">Tier B — Statewide by Scope</p>
<h2>Mobile home &amp; light demolition focus</h2>
<div class="area-grid">{links(tier_b)}</div>
{related_links("/service-areas/")}
</div></section>
""" + cta_band("Working outside this list?", "Larger demolition jobs may still qualify — tell us the city.")
    write(
        "service-areas/index.html",
        head(
            f"Florida Service Areas | {SHORT}",
            "Based in Kathleen serving Central Florida; larger mobile home demolition and site jobs considered statewide by scope.",
            "/service-areas/",
            breadcrumbs=[("Home", "/"), ("Service Areas", "/service-areas/")],
        )
        + hub
        + foot(),
    )

    for a in areas:
        short = a["shortName"]
        angle = a.get("angle", "full")
        if angle == "demo":
            title = f"Mobile Home Demolition in {short}, FL | {SHORT}"
            h1 = f"Mobile Home & Light Demolition in {short}"
            meta = f"Mobile home demolition and light structure removal in {short}, {a['county']}. Owner-operated Breaking Ground — free estimates."
        else:
            title = f"Demolition & Land Services in {short}, FL | {SHORT}"
            h1 = f"Demolition & Land Services in {short}"
            meta = f"Mobile home demolition, shed removal, land clearing, and stump work in {short}, FL. Call {PHONE}."
        body = f"""
{page_hero(h1, crumb([("Home","/"),("Service Areas","/service-areas/"),(short, f"/areas/{a['slug']}/")]), "/assets/images/projects/IMG_8286-scaled.jpg", meta)}
<section class="section-pad"><div class="container split">
<div class="prose reveal">{area_body(a)}{related_links(f"/areas/{a['slug']}/")}</div>
<div class="form-card reveal"><h3>Estimate for {esc(short)}</h3>{estimate_form("Mobile Home Demolition")}</div>
</div></section>
"""
        write(
            f"areas/{a['slug']}/index.html",
            head(
                title,
                meta,
                f"/areas/{a['slug']}/",
                breadcrumbs=[("Home", "/"), ("Service Areas", "/service-areas/"), (short, f"/areas/{a['slug']}/")],
                extra_schema=[
                    {
                        "@type": "Service",
                        "name": f"Demolition services in {short}",
                        "provider": {"@id": f"{DOMAIN}/#business"},
                        "areaServed": short + ", FL",
                        "url": f"{DOMAIN}/areas/{a['slug']}/",
                    }
                ],
            )
            + body
            + foot(),
        )


def build_thank_you_404() -> None:
    write(
        "thank-you/index.html",
        head(
            f"Thank You | {SHORT}",
            "We received your estimate request.",
            "/thank-you/",
            breadcrumbs=[("Home", "/"), ("Thank You", "/thank-you/")],
        )
        + page_hero("Thank you", crumb([("Home", "/"), ("Thank You", "/thank-you/")]), OG, "We received your request and will respond soon.")
        + f'<section class="section-pad"><div class="container prose"><p>If it is urgent, call <a href="tel:{PHONE_TEL}">{esc(PHONE)}</a>.</p><p><a href="/">Return home</a></p></div></section>'
        + foot(),
    )
    write(
        "404.html",
        head("Page Not Found | " + SHORT, "The page you requested was not found.", "/", breadcrumbs=[("Home", "/")])
        + page_hero("Page not found", crumb([("Home", "/")]), OG)
        + '<section class="section-pad"><div class="container"><p><a class="btn btn-primary" href="/">Go home</a> <a class="btn btn-dark" href="/contact/">Contact us</a></p></div></section>'
        + foot(),
    )


def build_redirects() -> None:
    redirects = {
        "landscaping/index.html": "/pond-drainage/",
        "posts/index.html": "/projects/",
        "brooksville-land-clearing/index.html": "/projects/brooksville-land-clearing/",
        "hurricane-clean-up/index.html": "/projects/hurricane-cleanup/",
        "8-16-2024-better-than-stump-grinding/index.html": "/projects/lakeland-stump-excavation/",
        "stump-removal-in-lakeland/index.html": "/projects/lakeland-stump-excavation/",
        "12-30-25-shed-removal-near-me/index.html": "/projects/shed-removal/",
        "how-to-dig-a-pond/index.html": "/projects/pond-earthwork-support/",
    }
    for rel, dest in redirects.items():
        write(
            rel,
            f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8" />
<title>Redirecting…</title>
<link rel="canonical" href="{DOMAIN}{dest}" />
<meta http-equiv="refresh" content="0;url={dest}" />
<script>location.replace("{dest}");</script>
</head><body><p>Moved to <a href="{dest}">{dest}</a>.</p></body></html>
""",
        )


def build_robots_llms() -> None:
    write(
        "robots.txt",
        f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
""",
    )
    write(
        "llms.txt",
        f"""# {NAME}
> Owner-operated mobile home demolition, light structure removal, land clearing, and site work based in Kathleen, Florida.

Contact: {PHONE} | {EMAIL}
Site: {DOMAIN}

## Primary services
- Mobile home demolition: {DOMAIN}/mobile-home-demolition/
- Demolition: {DOMAIN}/demolition/
- Land clearing: {DOMAIN}/land-clearing/
- Stump removal: {DOMAIN}/stump-removal/

## Notes
- Founded 2024 (not a GC marketing unrestricted building demolition)
- Central Florida core; statewide by scope for larger jobs
""",
    )


def build_sitemap() -> None:
    urls = [
        "/",
        "/about/",
        "/contact/",
        "/services/",
        "/projects/",
        "/pricing/",
        "/service-areas/",
        "/privacy-policy/",
        "/terms-of-service/",
        "/payment-deposit-policy/",
        "/image-use-policy/",
        "/thank-you/",
    ]
    urls += [s["path"] for s in SERVICES]
    urls += [p["path"] for p in PROJECTS]
    urls += [f"/areas/{a['slug']}/" for a in AREAS["areas"]]
    body = '<?xml version="1.0" encoding="UTF-8"?>\n'
    body += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        pri = "1.0" if u == "/" else ("0.9" if u.count("/") <= 2 else "0.7")
        body += f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pri}</priority></url>\n"
    body += "</urlset>\n"
    write("sitemap.xml", body)
    return urls


def build_docs() -> None:
    urls = build_sitemap()
    site_urls = f"""# SITE-URLS — Breaking Ground

Domain: {DOMAIN}
Generated: {TODAY}

## Preserved WordPress canonicals
- `/` → home
- `/about/`
- `/contact/`
- `/demolition/`
- `/land-clearing/`
- `/tree-removal/`
- `/stump-removal/`

## Redirect map (HTML refresh + canonical)
| Old | New |
|-----|-----|
| `/landscaping/` | `/pond-drainage/` |
| `/posts/` | `/projects/` |
| `/brooksville-land-clearing/` | `/projects/brooksville-land-clearing/` |
| `/hurricane-clean-up/` | `/projects/hurricane-cleanup/` |
| `/8-16-2024-better-than-stump-grinding/` | `/projects/lakeland-stump-excavation/` |
| `/stump-removal-in-lakeland/` | `/projects/lakeland-stump-excavation/` |
| `/12-30-25-shed-removal-near-me/` | `/projects/shed-removal/` |
| `/how-to-dig-a-pond/` | `/projects/pond-earthwork-support/` |

Prefer Cloudflare 301s at DNS cutover when available.

## Indexable URL count
{len(urls)} URLs in sitemap.xml

## DNS cutover
Change only website A/CNAME. Preserve MX, SPF, DKIM, DMARC for Zoho email.
"""
    write("SITE-URLS.md", site_urls)

    imgs = sorted((ROOT / "assets" / "images").rglob("*"))
    lines = ["# IMAGE-INVENTORY", "", "Downloaded from breakinggroundlsad.com WordPress media.", ""]
    for p in imgs:
        if p.is_file():
            lines.append(f"- `{p.relative_to(ROOT).as_posix()}` ({p.stat().st_size // 1024} KB)")
    write("IMAGE-INVENTORY.md", "\n".join(lines) + "\n")

    write(
        "LAUNCH-CHECKLIST.md",
        f"""# Launch Checklist — {SHORT}

## Before DNS cutover
- [ ] Replace Formspree ID in `formspree.json` and `data/site.json`, then re-run `python scripts/build_site.py`
- [ ] Confirm Zoho email `info@breakinggroundlsad.com` receives Formspree notifications
- [ ] Client approves staging site on GitHub Pages
- [ ] Document current DNS (especially MX/SPF/DKIM/DMARC)

## DNS cutover
- [ ] Point only A/CNAME/AAAA for the website to GitHub Pages
- [ ] Do **not** replace the entire DNS zone blindly
- [ ] Preserve email records

## After cutover
- [ ] Confirm SSL
- [ ] Test contact form end-to-end
- [ ] Verify preserved URLs: /demolition/, /land-clearing/, /tree-removal/, /stump-removal/, /about/, /contact/
- [ ] Verify redirects from legacy post URLs
- [ ] Submit sitemap in Google Search Console
- [ ] Update Google Business Profile website link (client-owned)

## Out of scope reminders
No CRM, GBP automation, or dynamic review widgets in Phase 1.
""",
    )


def apply_base_to_chrome() -> None:
    """Rewrite root-absolute paths in shared chrome for project Pages."""
    if not BASE:
        return
    for name in ("header.html", "footer.html"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        text = text.replace('href="/', f'href="{BASE}/')
        text = text.replace('src="/', f'src="{BASE}/')
        path.write_text(text, encoding="utf-8")
        print("rewrote", name)


def main() -> None:
    build_home()
    build_about()
    build_contact()
    build_services_hub()
    build_service_pages()
    build_projects()
    build_pricing()
    build_policies()
    build_service_areas()
    build_thank_you_404()
    build_redirects()
    build_robots_llms()
    build_docs()
    apply_base_to_chrome()
    print("DONE")
    if BASE:
        print(f"Preview base: {BASE}/ -> https://nicholasjknight.github.io{BASE}/")


if __name__ == "__main__":
    main()
