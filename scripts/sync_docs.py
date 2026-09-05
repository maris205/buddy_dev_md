"""Mirror the public Chinese WorkBuddy documentation. Python 3.10+.

Fetches only the official navigation, linked documentation and referenced assets.
Does not execute downloaded scripts, examples, archives or page JavaScript.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit, quote
from urllib.request import getproxies

import requests
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://open.workbuddy.cn"
ENTRY = BASE + "/docs"
SCHEMA = 1


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = data.encode("utf-8") if isinstance(data, str) else data
    if not path.exists() or path.read_bytes() != blob:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(blob)
        tmp.replace(path)


def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def canonical(url):
    p = urlsplit(urljoin(ENTRY + "/", url))
    path = re.sub(r"^/zh/docs(?=/|$)", "/docs", p.path).rstrip("/")
    if p.hostname == "open.workbuddy.cn" and (path == "/docs" or path.startswith("/docs/")):
        if path == "/docs":
            path = "/docs/what-is-open-platform"
        return BASE + path
    return None


def slug_of(url):
    slug = unquote(urlsplit(url).path.removeprefix("/docs/")).replace("/", "--")
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
        raise ValueError(f"Unsupported document path: {url}")
    return slug


def flight(soup):
    chunks = []
    for script in soup.find_all("script"):
        match = re.search(r"self\.__next_f\.push\((\[.*\])\)", script.string or "", re.S)
        if match:
            value = json.loads(match.group(1))
            if len(value) > 1 and isinstance(value[1], str):
                chunks.append(value[1])
    stream = "".join(chunks)
    records, image_types = {}, set()
    wire, offset = stream.encode("utf-8"), 0
    while offset < len(wire):
        match = re.match(rb"([0-9a-f]+):", wire[offset:])
        if not match:
            end = wire.find(b"\n", offset)
            if end < 0:
                break
            offset = end + 1
            continue
        key = match[1].decode("ascii")
        start = offset + match.end()
        if wire[start:start + 1] == b"T":
            comma = wire.index(b",", start)
            size = int(wire[start + 1:comma], 16)
            offset = comma + 1 + size
            records[key] = wire[comma + 1:offset].decode("utf-8")
            continue
        end = wire.find(b"\n", start)
        if end < 0:
            end = len(wire)
        rest = wire[start:end].decode("utf-8")
        offset = end + 1
        try:
            if rest.startswith("I"):
                value = json.JSONDecoder().raw_decode(rest[1:])[0]
                if isinstance(value, list) and value[-1] == "DocImage":
                    image_types.add("$L" + key)
            else:
                records[key] = json.JSONDecoder().raw_decode(rest)[0]
        except (ValueError, IndexError):
            continue  # Flight metadata / text records are not JSON trees.
    return stream, records, image_types


def walk(value, records, stack=()):
    if isinstance(value, str):
        match = re.fullmatch(r"\$(?:L)?([0-9a-f]+)", value)
        if match and match[1] in records and match[1] not in stack:
            yield from walk(records[match[1]], records, stack + (match[1],))
    elif isinstance(value, list):
        yield value
        for child in value:
            yield from walk(child, records, stack)
    elif isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child, records, stack)


def navigation(soup):
    stream, _, _ = flight(soup)
    match = re.search(r'"groups":', stream)
    if not match:
        raise ValueError("Official navigation not found; site format may have changed")
    groups = json.JSONDecoder().raw_decode(stream[match.end():])[0]
    result = []
    for group in groups:
        for node in walk(group.get("children", []), {}):
            if isinstance(node, dict) and "href" in node and "title" in node:
                url = canonical(node["href"])
                if url:
                    result.append({"url": url, "title": node["title"], "group": group["title"],
                                   "headings": node.get("headings", [])})
    if not result:
        raise ValueError("Empty navigation")
    return list({p["url"]: p for p in result}.values())


def extract(raw):
    soup = BeautifulSoup(raw, "html.parser")
    content = soup.select_one('[class*="prose-docs_root"]')
    if content is None or content.find("h1") is None:
        raise ValueError("Document body / h1 missing")
    _, records, image_types = flight(soup)
    roots = []
    for value in records.values():
        for node in walk(value, {}):
            if isinstance(node, dict) and "prose-docs_root" in node.get("className", ""):
                roots.append(node)
    placeholders = content.select("span.animate-pulse")
    images = []
    if placeholders:
        if len(roots) != 1:
            raise ValueError(f"Expected one Flight article root, got {len(roots)}")
        for node in walk(roots[0], records):
            if (isinstance(node, list) and len(node) == 4 and node[0] == "$"
                    and isinstance(node[1], str) and node[1] in image_types):
                images.append(node[3])
        if len(images) != len(placeholders):
            raise ValueError(f"Image mismatch: {len(placeholders)} placeholders / {len(images)} image nodes")
        for placeholder, props in zip(placeholders, images):
            img = soup.new_tag("img", src=props["src"], alt=props.get("alt", ""))
            placeholder.replace_with(img)
    for node in content.select("button, script, style"):
        node.decompose()
    return soup, content


class Converter(MarkdownConverter):
    def convert_br(self, el, text, parent_tags):
        return "<br>" if el.find_parent(["td", "th"]) else "  \n"


def markdown(content):
    # Protect code bytes and explicit source anchors from Markdown escaping.
    soup = BeautifulSoup(str(content), "html.parser")
    saved = {}
    def protect(node, text):
        key = f"WBPROTECTEDBLOCK{len(saved):05d}END"
        saved[key] = text
        node.replace_with(soup.new_string(key))
    for pre in list(soup.select("pre")):
        code = pre.find("code") or pre
        lang = next((c[9:] for c in code.get("class", []) if c.startswith("language-")), "")
        source = code.get_text().replace("\r\n", "\n").rstrip("\n")
        fence = "`" * max(3, max((len(x) + 1 for x in re.findall(r"`+", source)), default=3))
        protect(pre, f"\n\n{fence}{lang}\n{source}\n{fence}\n\n")
    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        if heading.get("id"):
            key = f"WBPROTECTEDBLOCK{len(saved):05d}END"
            saved[key] = '\n\n<a id="' + html.escape(heading["id"], quote=True) + '"></a>\n\n'
            heading.insert_before(soup.new_string(key))
    # Preserve merged cells as HTML; ordinary tables stay Markdown.
    for table in list(soup.select("table")):
        if table.select("[colspan], [rowspan]"):
            for node in [table, *table.find_all(True)]:
                node.attrs = {k: v for k, v in node.attrs.items() if k in ("colspan", "rowspan", "href", "src", "alt")}
            protect(table, "\n\n" + str(table) + "\n\n")
    result = Converter(heading_style="ATX", bullets="-", escape_underscores=False,
                       strip=["span"]).convert(str(soup))
    for key, text in saved.items():
        result = result.replace(key, text)
    # Do not normalize blank lines inside source code blocks.
    return result.strip() + "\n"


def asset_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path, p.query, ""))


def is_asset(url):
    return bool(re.search(r"\.(png|jpe?g|gif|webp|svg|avif|zip|pdf|json|txt|md|ya?ml|xlsx?|docx?|pptx?|mp4|woff2?)$", urlsplit(url).path, re.I))


class Fetcher:
    def __init__(self, delay):
        self.session = requests.Session()
        self.session.proxies.update(getproxies())
        self.session.headers["User-Agent"] = "buddy-dev-md/1.0 (public documentation archival)"
        self.delay = delay

    def get(self, url, previous=None):
        headers = {}
        if previous:
            if previous.get("etag"):
                headers["If-None-Match"] = previous["etag"]
            if previous.get("last_modified"):
                headers["If-Modified-Since"] = previous["last_modified"]
        for attempt in range(3):
            time.sleep(self.delay)
            try:
                response = self.session.get(url, headers=headers, timeout=(15, 45))
                response.raise_for_status()
                return response
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(1 + attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Rebuild from saved snapshots without network")
    parser.add_argument("--refresh-assets", action="store_true", help="Revalidate existing images and attachments")
    parser.add_argument("--delay", type=float, default=0.15, help="Delay between HTTP requests")
    args = parser.parse_args()
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    old = read_json(ROOT / ".sync/manifest.json", {"pages": {}, "assets": {}})
    fetcher = Fetcher(args.delay)
    errors, anomalies, changes = [], [], []
    if args.offline:
        raw_entry = (ROOT / ".sync/raw/_index.html").read_bytes()
    else:
        raw_entry = fetcher.get(ENTRY).content
        write(ROOT / ".sync/raw/_index.html", raw_entry)
    nav = navigation(BeautifulSoup(raw_entry, "html.parser"))
    dump(ROOT / ".sync/navigation.json", nav)
    pages, assets = {}, {}
    queue = list(nav)
    seen = set()
    content_map = {}
    while queue:
        item = queue.pop(0)
        url = item["url"]
        if url in seen:
            continue
        seen.add(url)
        slug = slug_of(url)
        raw_path = ROOT / f".sync/raw/{slug}.html"
        prior = old["pages"].get(url, {})
        try:
            response = None
            if args.offline:
                raw = raw_path.read_bytes()
            else:
                response = fetcher.get(url, prior if raw_path.exists() else None)
                raw = raw_path.read_bytes() if response.status_code == 304 else response.content
            soup, content = extract(raw)
            body_hash = digest(str(content).encode("utf-8"))
            # Keep the prior full snapshot if semantic body is unchanged.
            if not args.offline and (not raw_path.exists() or prior.get("body_sha256") != body_hash):
                write(raw_path, raw)
            raw = raw_path.read_bytes()
            headings = [{"level": int(h.name[1]), "text": h.get_text(), "id": h.get("id")}
                        for h in content.find_all(re.compile(r"^h[1-6]$"))]
            meta = dict(item, path=f"docs/{slug}.md", snapshot=f".sync/raw/{slug}.html",
                        first_fetched_at=prior.get("first_fetched_at", now),
                        content_fetched_at=prior.get("content_fetched_at", now) if prior.get("body_sha256") == body_hash else now,
                        last_checked_at=prior.get("last_checked_at", now) if args.offline else now,
                        raw_sha256=digest(raw), body_sha256=body_hash, headings=headings,
                        status="ok", official_updated_at=None,
                        etag=response.headers.get("ETag", prior.get("etag")) if response is not None else prior.get("etag"),
                        last_modified=response.headers.get("Last-Modified", prior.get("last_modified")) if response is not None else prior.get("last_modified"))
            if not prior:
                changes.append({"url": url, "change": "added"})
            elif prior.get("body_sha256") != body_hash:
                changes.append({"url": url, "change": "changed"})
            for anchor in content.select("a[href]"):
                absolute = urljoin(url, anchor["href"])
                target = canonical(absolute)
                if target and target not in seen and not any(p["url"] == target for p in queue):
                    queue.append({"url": target, "title": anchor.get_text(strip=True) or slug_of(target), "group": "正文发现"})
                label = anchor.get_text(strip=True)
                if label.startswith("https://") and label != unquote(absolute):
                    anomalies.append({"page": url, "kind": "url_label_target_mismatch", "label": label, "href": absolute})
                if urlsplit(absolute).hostname == "skill.md":
                    anomalies.append({"page": url, "kind": "filename_linked_as_domain", "label": label, "href": absolute})
            pages[url] = meta
            content_map[url] = content
            print(f"PAGE {len(pages):02d} {slug}", flush=True)
        except Exception as exc:
            errors.append({"type": "page", "url": url, "error": str(exc)})
            print(f"ERROR {slug}: {exc}", flush=True)

    for url, content in content_map.items():
        refs = [(node, "src") for node in content.select("img[src]")]
        refs += [(node, "href") for node in content.select("a[href]") if is_asset(urljoin(url, node["href"]))]
        for node, attr in refs:
            source = asset_url(urljoin(url, node[attr]))
            if source not in assets:
                prior = old["assets"].get(source, {})
                basename = unquote(urlsplit(source).path.split("/")[-1])
                basename = re.sub(r"[^a-zA-Z0-9._-]", "_", basename)[-110:] or "asset.bin"
                relative = f"assets/{digest(source.encode())[:12]}-{basename}"
                path = ROOT / relative
                try:
                    if not path.exists() or (args.refresh_assets and not args.offline):
                        if args.offline:
                            raise ValueError("Asset absent in offline mode")
                        response = fetcher.get(source, prior if path.exists() else None)
                        if response.status_code != 304:
                            if "text/html" in response.headers.get("Content-Type", ""):
                                raise ValueError("Asset URL returned HTML")
                            write(path, response.content)
                        checked = now
                        content_type = response.headers.get("Content-Type", prior.get("content_type"))
                        etag = response.headers.get("ETag", prior.get("etag"))
                        modified = response.headers.get("Last-Modified", prior.get("last_modified"))
                    else:
                        checked = prior.get("last_checked_at", now)
                        content_type, etag, modified = (prior.get(k) for k in ("content_type", "etag", "last_modified"))
                    assets[source] = {"path": relative, "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size,
                                      "last_checked_at": checked, "content_type": content_type,
                                      "etag": etag, "last_modified": modified, "status": "ok"}
                    print(f"ASSET {len(assets):02d} {basename}", flush=True)
                except Exception as exc:
                    assets[source] = {"status": "failed", "error": str(exc)}
                    errors.append({"type": "asset", "url": source, "page": url, "error": str(exc)})
            if assets[source]["status"] == "ok":
                node[attr] = "../" + assets[source]["path"]
        for anchor in content.select("a[href]"):
            absolute = urljoin(url, anchor["href"])
            target = canonical(absolute)
            if target and target in pages:
                fragment = urlsplit(absolute).fragment
                anchor["href"] = slug_of(target) + ".md" + ("#" + fragment if fragment else "")
            elif not anchor["href"].startswith("../assets/"):
                anchor["href"] = absolute
        meta = pages[url]
        body = markdown(content)
        header = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in {
            "title": meta["title"], "source_url": url, "source_type": "official-mirror",
            "group": meta["group"], "fetched_at": meta["content_fetched_at"],
            "official_updated_at": None, "source_sha256": meta["body_sha256"],
            "tags": ["workbuddy", "official", slug_of(url)]}.items()) + "\n---\n\n"
        banner = f"> 官方文档镜像 · [原文]({url}) · [文档目录](../wiki/index.md) · [开发路线](../wiki/development-map.md)\n\n"
        write(ROOT / meta["path"], header + banner + body)
        meta["markdown_sha256"] = digest((ROOT / meta["path"]).read_bytes())

    # Preserve failed / removed snapshots on disk, but never mark them current.
    removed = sorted(set(old["pages"]) - seen)
    report = {"checked_at": now, "mode": "offline" if args.offline else "online",
              "scope": "Public Chinese official navigation + linked /docs pages; no login or external-site recursion",
              "navigation_pages": len(nav), "discovered_pages": len(seen), "successful_pages": len(pages),
              "successful_assets": sum(a["status"] == "ok" for a in assets.values()),
              "errors": errors, "source_anomalies": anomalies, "changes": changes, "removed_from_discovery": removed}
    if not args.offline:
        dump(ROOT / ".sync/report.json", report)
    dump(ROOT / ".sync/manifest.json", {"schema_version": SCHEMA, "pages": pages, "assets": assets})
    generate_indexes(nav, pages, assets, report, args.offline)
    print(json.dumps({k: report[k] for k in ("navigation_pages", "successful_pages", "successful_assets", "errors")}, ensure_ascii=False))
    return 1 if errors else 0


def generate_indexes(nav, pages, assets, report, offline):
    lines = ["# WorkBuddy 文档索引", "", "> 根据官网目录自动生成；原文见各页面的 source_url。", "",
             "- [开发路线与能力关系](development-map.md)", "- [同步与完整性报告](../SYNC_REPORT.md)",
             "- [原文待核对事项](source-notes.md)", "", "## 官方目录", ""]
    group = None
    for meta in pages.values():
        if meta["group"] != group:
            group = meta["group"]
            lines.extend([f"### {group}", ""])
        lines.append(f'- [{meta["title"]}](../{meta["path"]})')
    lines.extend(["", "## 按章节检索", ""])
    for meta in pages.values():
        lines.extend([f'### {meta["title"]}', ""])
        lines.extend(f'- [{h["text"]}](../{meta["path"]}#{quote(h["id"])})' for h in meta["headings"] if h["level"] == 2 and h["id"])
        lines.append("")
    write(ROOT / "wiki/index.md", "\n".join(lines).rstrip() + "\n")
    rows = ["# 图片与附件索引", "", "自动提取自官方正文。文件保持原始字节；不运行附件中的程序。", "",
            "| 本地文件 | 大小 | 来源 |", "| --- | ---: | --- |"]
    for source, meta in assets.items():
        if meta["status"] == "ok":
            name = Path(meta["path"]).name
            rows.append(f'| [{name}](../{meta["path"]}) | {meta["bytes"]:,} B | [原始文件]({source}) |')
    write(ROOT / "assets/README.md", "\n".join(rows) + "\n")
    if offline:
        return
    notes = ["# 原文待核对事项", "", "以下是自动检查发现的链接异常，属于原网页内容；镜像保留原样。开发时请结合接口标题、参数表和平台实际行为核对。", "",
             "检查范围是链接文字与目标的差异，以及文件名被识别为域名；这不是完整的官方文档技术审校。", "",
             "| 页面 | 类型 | 原文链接文字 | 原文目标 |", "| --- | --- | --- | --- |"]
    for issue in report["source_anomalies"]:
        page = pages.get(issue["page"])
        label = issue["label"].replace("|", "\\|")
        local = "../" + page["path"] if page else issue["page"]
        notes.append(f'| [{page["title"] if page else "原文"}]({local}) | `{issue["kind"]}` | {label} | `{issue["href"]}` |')
    notes.extend(["", "`filename_linked_as_domain` 表示原文将 `SKILL.md` 链接成了 HTTP 域名，它不作为可下载的技能附件。", "",
                  "返回 [文档索引](index.md) · [开发对象关系](development-map.md) · [同步报告](../SYNC_REPORT.md)。"])
    write(ROOT / "wiki/source-notes.md", "\n".join(notes) + "\n")
    lines = ["# 同步报告", "", f'最近在线检查：`{report["checked_at"]}`。', "",
             "范围：官网中文文档目录，以及正文新发现的本站 `/docs` 页面；下载正文图片和附件。外部协议站点、控制台和登录后内容不在全量范围内。", "",
             f'- 官方目录：{report["navigation_pages"]} 篇。', f'- 发现页面：{report["discovered_pages"]} 篇；成功：{report["successful_pages"]} 篇。',
             f'- 已保存图片/附件：{report["successful_assets"]} 个。', f'- 抓取失败：{len(report["errors"])} 项。',
             f'- 本次新增/正文变更：{len(report["changes"])} 项。',
             f'- 从目录及正文发现范围消失：{len(report["removed_from_discovery"])} 项；旧文件保留，未自动删除。', "",
             "正文哈希用于判断实质更新，完整 HTML 快照用于复核；页面未提供明确的官方更新时间，因此 `official_updated_at` 为 null。HTTP Last-Modified 仅为传输元数据。", "",
             "页面每次在线同步均检查；已下载资源默认按 URL 缓存，使用 `--refresh-assets` 检查原 URL 下资源是否更新。", "",
             "- [机器可读抓取报告](.sync/report.json)", "- [页面与资源哈希清单](.sync/manifest.json)",
             "- [离线完整性校验](.sync/validation.json)", "- [原文待核对事项](wiki/source-notes.md)", "", "## 失败清单", ""]
    lines += [f'- `{e["url"]}`：{e["error"]}' for e in report["errors"]] or ["无。"]
    write(ROOT / "SYNC_REPORT.md", "\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
