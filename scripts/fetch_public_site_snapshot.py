"""Fetch a safe public snapshot of one website URL for offline review.

This is intentionally not a scanner. It fetches:
- the exact URL provided;
- robots.txt and sitemap.xml on the same origin;
- CSS/JS/image metadata explicitly linked from the fetched HTML.

It does not brute-force paths, scan ports, submit forms, authenticate, or call
private/admin endpoints.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "output" / "external-site-snapshot"


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.assets: list[dict[str, str]] = []
        self.forms: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.meta: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key.lower(): value or "" for key, value in attrs}
        if tag == "script" and attr.get("src"):
            self.assets.append({"tag": tag, "url": attr["src"], "rel": "script"})
        elif tag == "link" and attr.get("href"):
            rel = attr.get("rel", "")
            self.assets.append({"tag": tag, "url": attr["href"], "rel": rel})
            self.links.append({"href": attr["href"], "rel": rel, "text": ""})
        elif tag == "img" and attr.get("src"):
            self.assets.append({"tag": tag, "url": attr["src"], "rel": "image"})
        elif tag == "form":
            self.forms.append({"action": attr.get("action", ""), "method": attr.get("method", "GET").upper()})
        elif tag == "a" and attr.get("href"):
            self.links.append({"href": attr["href"], "rel": attr.get("rel", ""), "text": ""})
        elif tag == "meta":
            item = {key: attr.get(key, "") for key in ["name", "property", "content"] if attr.get(key)}
            if item:
                self.meta.append(item)


def _safe_slug(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc or parsed.path
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", host).strip("_")
    return slug or "site"


def _fetch(url: str, *, timeout: int) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "vpp-public-site-snapshot/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            headers = dict(response.headers.items())
            return {
                "ok": True,
                "url": url,
                "final_url": response.geturl(),
                "status": response.status,
                "headers": headers,
                "body": body,
                "error": "",
            }
    except HTTPError as exc:
        return {"ok": False, "url": url, "status": exc.code, "headers": dict(exc.headers.items()), "body": b"", "error": f"HTTP {exc.code}"}
    except URLError as exc:
        return {"ok": False, "url": url, "status": None, "headers": {}, "body": b"", "error": f"URL error: {exc.reason}"}
    except Exception as exc:
        return {"ok": False, "url": url, "status": None, "headers": {}, "body": b"", "error": f"{type(exc).__name__}: {exc}"}


def _same_origin(base_url: str, url: str) -> bool:
    base = urlparse(base_url)
    target = urlparse(url)
    return (base.scheme, base.netloc) == (target.scheme, target.netloc)


def _asset_filename(index: int, url: str, content_type: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name or f"asset_{index}"
    name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name)
    if "." not in name:
        if "javascript" in content_type:
            name += ".js"
        elif "css" in content_type:
            name += ".css"
        elif "html" in content_type:
            name += ".html"
        else:
            name += ".bin"
    return f"{index:03d}_{name}"


def build_snapshot(url: str, output_dir: Path, timeout: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    page = _fetch(url, timeout=timeout)
    manifest: dict[str, Any] = {
        "snapshot_type": "public_site_snapshot",
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "start_url": url,
        "safe_scope": "exact URL + same-origin linked assets only",
        "page": {key: page.get(key) for key in ["ok", "url", "final_url", "status", "headers", "error"] if key in page},
        "assets": [],
        "forms": [],
        "links": [],
        "meta": [],
    }

    if not page["ok"]:
        return manifest

    content_type = page["headers"].get("Content-Type", "")
    body = page["body"]
    (output_dir / "index.raw").write_bytes(body)
    if "html" in content_type.lower() or body[:200].lstrip().lower().startswith(b"<!doctype") or b"<html" in body[:500].lower():
        html = body.decode("utf-8", errors="replace")
        (output_dir / "index.html").write_text(html, encoding="utf-8")
        parser = AssetParser()
        parser.feed(html)
        manifest["forms"] = parser.forms
        manifest["links"] = parser.links[:500]
        manifest["meta"] = parser.meta[:200]

        urls: list[tuple[str, str, str]] = []
        for asset in parser.assets:
            absolute = urljoin(page["final_url"], asset["url"])
            if _same_origin(page["final_url"], absolute):
                urls.append((absolute, asset["tag"], asset["rel"]))

        for extra in ["robots.txt", "sitemap.xml"]:
            urls.append((urljoin(page["final_url"], "/" + extra), "well-known", extra))

        seen = set()
        asset_index = 1
        for asset_url, tag, rel in urls:
            if asset_url in seen:
                continue
            seen.add(asset_url)
            fetched = _fetch(asset_url, timeout=timeout)
            asset_info = {key: fetched.get(key) for key in ["ok", "url", "final_url", "status", "headers", "error"] if key in fetched}
            asset_info["tag"] = tag
            asset_info["rel"] = rel
            if fetched["ok"]:
                asset_content_type = fetched["headers"].get("Content-Type", "")
                filename = _asset_filename(asset_index, asset_url, asset_content_type)
                (output_dir / filename).write_bytes(fetched["body"])
                asset_info["file"] = filename
                asset_info["bytes"] = len(fetched["body"])
                asset_index += 1
            manifest["assets"].append(asset_info)

    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch safe public website snapshot")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or (OUTPUT_ROOT / _safe_slug(args.url))
    manifest = build_snapshot(args.url, output_dir, args.timeout)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"snapshot_status={'OK' if manifest['page'].get('ok') else 'FAILED'}")
    print(f"page_status={manifest['page'].get('status')}")
    print(f"assets={len(manifest.get('assets', []))}")
    print(f"forms={len(manifest.get('forms', []))}")
    print(f"links={len(manifest.get('links', []))}")
    print(f"output_dir={output_dir.relative_to(PROJECT_ROOT)}")
    print(f"manifest={manifest_path.relative_to(PROJECT_ROOT)}")
    return 0 if manifest["page"].get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
