"""Offline fidelity and link checks against stored official HTML snapshots."""
from __future__ import annotations

import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit
import zipfile

from bs4 import BeautifulSoup
from markdown_it import MarkdownIt

from sync_docs import ROOT, canonical, digest, dump, extract, read_json, asset_url

RENDERER = MarkdownIt("commonmark", {"html": True}).enable("table")


def normalized(text):
    return re.sub(r"\s+", "", text)


def without_frontmatter(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)


def rendered(text):
    return BeautifulSoup(RENDERER.render(without_frontmatter(text)), "html.parser")


def native_slug(text):
    text = text.lower()
    return re.sub(r"[^\w\-\s]", "", text, flags=re.UNICODE).replace(" ", "-")


def main():
    manifest = read_json(ROOT / ".sync/manifest.json", {})
    nav = read_json(ROOT / ".sync/navigation.json", [])
    sync_report = read_json(ROOT / ".sync/report.json", {})
    failures, stats, warnings = [], [], []
    def check(condition, message):
        if not condition:
            failures.append(message)
    check(bool(manifest.get("pages")), "Empty page manifest")
    check(not sync_report.get("errors"), "Latest online sync has errors")
    check(all(p["url"] in manifest.get("pages", {}) for p in nav), "Official navigation coverage incomplete")
    for url, meta in manifest.get("pages", {}).items():
        name = meta["path"]
        try:
            raw = (ROOT / meta["snapshot"]).read_bytes()
            md_path = ROOT / name
            md_bytes = md_path.read_bytes()
            check(digest(raw) == meta["raw_sha256"], f"{name}: raw hash mismatch")
            check(digest(md_bytes) == meta["markdown_sha256"], f"{name}: Markdown hash mismatch")
            _, source = extract(raw)
            check(digest(str(source).encode("utf-8")) == meta["body_sha256"], f"{name}: body hash mismatch")
            body = without_frontmatter(md_bytes.decode("utf-8")).lstrip()
            # The generated provenance banner is outside the source article.
            check(body.startswith("> 官方文档镜像"), f"{name}: provenance banner missing")
            body = body.split("\n\n", 1)[1]
            target = rendered(body)
            source_heads = [(h.name, h.get_text()) for h in source.find_all(re.compile(r"^h[1-6]$"))]
            target_heads = [(h.name, h.get_text()) for h in target.find_all(re.compile(r"^h[1-6]$"))]
            check(source_heads == target_heads, f"{name}: heading content / order mismatch")
            source_code = [p.get_text().replace("\r\n", "\n").rstrip("\n") for p in source.select("pre")]
            target_code = [p.get_text().replace("\r\n", "\n").rstrip("\n") for p in target.select("pre")]
            check(source_code == target_code, f"{name}: code block content / order mismatch")
            def table_cells(soup):
                return [[[normalized(c.get_text()) for c in row.find_all(["th", "td"], recursive=False)]
                         for row in table.find_all("tr")] for table in soup.select("table")]
            check(table_cells(source) == table_cells(target), f"{name}: table cells / order mismatch")
            src_text, dst_text = normalized(source.get_text()), normalized(target.get_text())
            if src_text != dst_text:
                pos = next((i for i, (a, b) in enumerate(zip(src_text, dst_text)) if a != b), min(len(src_text), len(dst_text)))
                check(False, f"{name}: visible text mismatch at {pos}: {src_text[max(0,pos-30):pos+60]!r} != {dst_text[max(0,pos-30):pos+60]!r}")
            src_images = source.select("img[src]")
            dst_images = target.select("img[src]")
            check(len(src_images) == len(dst_images), f"{name}: image count mismatch")
            for src, dst in zip(src_images, dst_images):
                key = asset_url(urljoin(url, src["src"]))
                asset = manifest["assets"].get(key, {})
                check(asset.get("status") == "ok", f"{name}: image not downloaded: {key}")
                check((md_path.parent / unquote(dst["src"])).resolve() == (ROOT / asset.get("path", "")).resolve(),
                      f"{name}: image order / path mismatch")
                check(src.get("alt", "") == dst.get("alt", ""), f"{name}: image alt mismatch")
            for src in source.select("a[href]"):
                key = asset_url(urljoin(url, src["href"]))
                if key in manifest["assets"]:
                    local = "../" + manifest["assets"][key].get("path", "")
                    check(any(a["href"] == local for a in target.select("a[href]")), f"{name}: attachment link missing: {key}")
            stats.append({"path": name, "headings": len(source_heads), "code_blocks": len(source_code),
                          "tables": len(source.select("table")), "images": len(src_images),
                          "source_visible_characters": len(src_text)})
        except Exception as exc:
            check(False, f"{name}: {type(exc).__name__}: {exc}")

    for url, meta in manifest.get("assets", {}).items():
        try:
            check(meta.get("status") == "ok", f"Asset status failed: {url}")
            path = ROOT / meta["path"]
            data = path.read_bytes()
            check(bool(data), f"Empty asset: {path.name}")
            check(len(data) == meta["bytes"] and digest(data) == meta["sha256"], f"Asset size / hash mismatch: {path.name}")
            if path.suffix.lower() == ".zip":
                with zipfile.ZipFile(path) as archive:
                    check(archive.testzip() is None, f"Corrupt ZIP: {path.name}")
            elif path.suffix.lower() == ".png":
                check(data.startswith(b"\x89PNG\r\n\x1a\n"), f"Invalid PNG header: {path.name}")
            elif path.suffix.lower() in (".jpg", ".jpeg"):
                check(data.startswith(b"\xff\xd8\xff"), f"Invalid JPEG header: {path.name}")
        except Exception as exc:
            check(False, f"Asset {url}: {exc}")

    # Parse Markdown rather than regex matching code examples as links.
    docs = {}
    for path in ROOT.rglob("*.md"):
        if any(part in (".git", ".venv", ".sync") for part in path.relative_to(ROOT).parts):
            continue
        docs[path.resolve()] = rendered(path.read_text(encoding="utf-8"))
    anchors = {}
    for path, soup in docs.items():
        anchors[path] = {a["id"] for a in soup.select("[id]")}
        counts = {}
        for h in soup.find_all(re.compile(r"^h[1-6]$")):
            slug = native_slug(h.get_text())
            count = counts.get(slug, 0)
            anchors[path].add(slug + (f"-{count}" if count else ""))
            counts[slug] = count + 1
    checked_links = 0
    for path, soup in docs.items():
        for node in soup.select("a[href], img[src]"):
            ref = node.get("href", node.get("src"))
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc:
                continue
            local = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            check(local.is_relative_to(ROOT.resolve()), f"{path.name}: local link escapes repository: {ref}")
            check(local.exists(), f"{path.name}: missing local target: {ref}")
            if parsed.fragment and local in anchors:
                check(unquote(parsed.fragment) in anchors[local], f"{path.name}: missing anchor: {ref}")
            checked_links += 1
    # validation.json is linked by the report, including on the first run.
    from datetime import datetime, timezone
    report = {"checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "status": "passed" if not failures else "failed", "pages": stats,
              "totals": {"pages": len(stats), "assets": len(manifest.get("assets", {})),
                         "markdown_files": len(docs), "local_links": checked_links,
                         **{k: sum(p[k] for p in stats) for k in ("headings", "code_blocks", "tables", "images")}},
              "failures": failures, "warnings": warnings,
              "limits": ["No live WorkBuddy execution or API correctness validation", "Images checked by hash and signature, not OCR", "External links not requested"]}
    dump(ROOT / ".sync/validation.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    # Establish the output path before checking a report link to it.
    if not (ROOT / ".sync/validation.json").exists():
        dump(ROOT / ".sync/validation.json", {"status": "pending"})
    sys.exit(main())
