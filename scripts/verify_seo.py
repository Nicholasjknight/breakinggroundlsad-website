#!/usr/bin/env python3
"""Verify indexable pages exist and match sitemap.xml."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://breakinggroundlsad.com"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

REQUIRED = [
    "index.html",
    "about/index.html",
    "contact/index.html",
    "demolition/index.html",
    "land-clearing/index.html",
    "tree-removal/index.html",
    "stump-removal/index.html",
    "mobile-home-demolition/index.html",
    "pricing/index.html",
    "terms-of-service/index.html",
    "payment-deposit-policy/index.html",
    "sitemap.xml",
    "robots.txt",
    "CNAME",
    "header.html",
    "footer.html",
]


def url_to_file(url: str) -> Path:
    path = url.replace(DOMAIN, "").rstrip("/")
    if path == "" or path == "/":
        return ROOT / "index.html"
    return ROOT / path.lstrip("/") / "index.html"


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")

    sitemap = ROOT / "sitemap.xml"
    tree = ET.parse(sitemap)
    locs = [el.text for el in tree.findall(".//sm:loc", NS) if el.text]
    if len(locs) < 70:
        errors.append(f"sitemap has only {len(locs)} URLs; expected >= 70")

    for loc in locs:
        f = url_to_file(loc)
        if not f.exists():
            errors.append(f"sitemap URL missing file: {loc} -> {f.relative_to(ROOT)}")
        else:
            text = f.read_text(encoding="utf-8")
            if 'rel="canonical"' not in text and "rel='canonical'" not in text:
                errors.append(f"missing canonical: {loc}")
            if "application/ld+json" not in text:
                errors.append(f"missing JSON-LD: {loc}")
            # Banned claims
            lowered = text.lower()
            for banned in ("licensed demolition contractor", "fully licensed", "florida's leading", "no job is too large"):
                if banned in lowered:
                    errors.append(f"banned phrase '{banned}' in {loc}")

    # Count area pages
    area_pages = list((ROOT / "areas").glob("*/index.html"))
    if len(area_pages) < 45:
        errors.append(f"only {len(area_pages)} area pages; expected >= 45")

    print(f"sitemap URLs: {len(locs)}")
    print(f"area pages: {len(area_pages)}")
    if errors:
        print("FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
