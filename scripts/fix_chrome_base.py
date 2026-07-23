#!/usr/bin/env python3
"""Collapse repeated /breakinggroundlsad-website prefixes in header/footer."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "/breakinggroundlsad-website"
PAT = re.compile(rf"(?:{re.escape(BASE)})+")


def fix_text(text: str) -> str:
    # Collapse any run of BASE prefixes to a single BASE
    return PAT.sub(BASE, text)


def main() -> None:
    for name in ("header.html", "footer.html"):
        path = ROOT / name
        original = path.read_text(encoding="utf-8")
        fixed = fix_text(original)
        path.write_text(fixed, encoding="utf-8")
        print(f"{name}: {'changed' if fixed != original else 'unchanged'}")
        for line in fixed.splitlines():
            if "Logo-Square" in line:
                print(" ", line.strip())


if __name__ == "__main__":
    main()
