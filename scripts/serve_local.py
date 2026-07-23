#!/usr/bin/env python3
"""Local preview server matching GitHub Pages project-site paths."""
from __future__ import annotations

import argparse
import json
import socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
DEFAULT_BASE = (SITE.get("siteBase") or "").rstrip("/")


class PagesHandler(SimpleHTTPRequestHandler):
    base_path = DEFAULT_BASE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path: str) -> str:
        if self.base_path and (path == self.base_path or path.startswith(f"{self.base_path}/")):
            path = path[len(self.base_path) :] or "/"
        return super().translate_path(path)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")


def pick_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Breaking Ground site locally.")
    parser.add_argument("--port", type=int, default=8766, help="Preferred port (default: 8766)")
    args = parser.parse_args()

    port = pick_port(args.port)
    PagesHandler.base_path = DEFAULT_BASE
    server = ThreadingHTTPServer(("127.0.0.1", port), PagesHandler)

    base = DEFAULT_BASE or ""
    print(f"Serving {ROOT}")
    print(f"Open: http://127.0.0.1:{port}{base}/")
    if base:
        print(f"(GitHub Pages base path: {base})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
