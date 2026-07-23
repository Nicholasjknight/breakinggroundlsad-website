#!/usr/bin/env python3
"""Create a clearer web hero asset from the downloaded About-page IMG_0078 source."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
HERO = ROOT / "assets" / "images" / "hero"
SOURCE = HERO / "IMG_0078-source.jpg"
OUT = HERO / "IMG_0078-hero.jpg"
SCALED = HERO / "IMG_0078-scaled.jpg"


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(
            f"Missing {SOURCE.name}. Download with a browser User-Agent:\n"
            "  Invoke-WebRequest -Uri https://breakinggroundlsad.com/wp-content/uploads/2025/10/IMG_0078.jpg "
            f"-OutFile '{SOURCE}' -Headers @{{'User-Agent'='Mozilla/5.0'}}"
        )

    im = Image.open(SOURCE).convert("RGB")
    print("source", im.size)

    w, h = im.size
    max_edge = 2400
    if max(w, h) > max_edge:
        scale = max_edge / max(w, h)
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        print("resized", im.size)

    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Color(im).enhance(1.05)
    im = ImageEnhance.Sharpness(im).enhance(1.25)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=120, threshold=2))

    im.save(OUT, "JPEG", quality=90, optimize=True, progressive=True)
    im.save(SCALED, "JPEG", quality=90, optimize=True, progressive=True)
    print("wrote", OUT.name, OUT.stat().st_size, im.size)


if __name__ == "__main__":
    main()
