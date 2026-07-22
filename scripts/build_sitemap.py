#!/usr/bin/env python3
"""Rebuild sitemap only (also available via build_site.py)."""
from build_site import build_docs

if __name__ == "__main__":
    build_docs()
    print("sitemap + docs refreshed")
