from pathlib import Path
from urllib.parse import urlparse
from html.parser import HTMLParser
import re

ROOT = Path(".")
DOMAIN = "https://freelancehiringhub.com"

EXCLUDE_PARTS = {".git", ".vercel", "node_modules"}

def excluded(path):
    return any(part in EXCLUDE_PARTS for part in path.parts)

html_files = sorted(
    p for p in ROOT.rglob("*.html")
    if not excluded(p)
)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.description = None
        self.canonical = None
        self.links = []
        self.logo = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "title":
            self.in_title = True

        elif tag == "meta":
            if attrs.get("name", "").lower() == "description":
                self.description = attrs.get("content", "").strip()

        elif tag == "link":
            if "canonical" in attrs.get("rel", "").lower():
                self.canonical = attrs.get("href", "").strip()

        elif tag == "a":
            href = attrs.get("href")
            if href:
                self.links.append(href.strip())

        elif tag == "img":
            src = attrs.get("src", "")
            classes = attrs.get("class", "")
            if "brand-logo" in classes or "freelance-hiring-hub-logo" in src:
                self.logo = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data

def route_for_file(path):
    if path.name != "index.html":
        return "/" + path.as_posix().lstrip("./")

    parent = path.parent.as_posix()

    if parent == ".":
        return "/"

    return "/" + parent.strip("/") + "/"

def target_exists(href):
    if not href:
        return True

    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return True

    parsed = urlparse(href)

    # External link
    if parsed.scheme in ("http", "https"):
        if parsed.netloc not in ("freelancehiringhub.com", "www.freelancehiringhub.com"):
            return True
        path = parsed.path
    else:
        path = parsed.path

    if not path:
        return True

    # Ignore query/fragment
    path = path.split("?")[0].split("#")[0]

    if not path.startswith("/"):
        return True

    local = ROOT / path.lstrip("/")

    # /foo/ -> /foo/index.html
    if path.endswith("/"):
        return (local / "index.html").exists()

    # direct file
    if local.exists():
        return True

    # extensionless route -> route/index.html
    if "." not in Path(path).name:
        return (local / "index.html").exists()

    return False


records = []
broken_links = []

for f in html_files:
    text = f.read_text(errors="ignore")

    parser = Parser()
    try:
        parser.feed(text)
    except Exception as e:
        print(f"PARSER ERROR: {f}: {e}")

    title = parser.title.strip()

    records.append({
        "file": f,
        "route": route_for_file(f),
        "title": title,
        "description": parser.description,
        "canonical": parser.canonical,
        "logo": parser.logo,
        "trustless_blocks": text.count("TRUSTLESS STRUCTURED PAYMENT"),
        "tool_callouts": text.count("CONTEXTUAL BUYER TOOL"),
    })

    for href in parser.links:
        if not target_exists(href):
            broken_links.append((f.as_posix(), href))


print("=" * 72)
print("FREELANCE HIRING HUB — LOCAL SITE AUDIT")
print("=" * 72)

print(f"\nHTML pages: {len(html_files)}")
print(f"Tool HTML pages: {len([f for f in html_files if 'tools' in f.parts])}")


def report(label, rows):
    print(f"\n{label}: {len(rows)}")
    for row in rows[:100]:
        print(" -", row)
    if len(rows) > 100:
        print(f" ... {len(rows) - 100} more")


missing_titles = [
    r["file"].as_posix()
    for r in records
    if not r["title"]
]

missing_descriptions = [
    r["file"].as_posix()
    for r in records
    if not r["description"]
]

missing_canonicals = [
    r["file"].as_posix()
    for r in records
    if not r["canonical"]
]

missing_logo = [
    r["file"].as_posix()
    for r in records
    if not r["logo"]
]

report("Missing titles", missing_titles)
report("Missing meta descriptions", missing_descriptions)
report("Missing canonicals", missing_canonicals)
report("Missing brand/logo markup", missing_logo)


# Duplicate titles
title_map = {}
for r in records:
    if r["title"]:
        title_map.setdefault(r["title"], []).append(r["file"].as_posix())

duplicate_titles = {
    title: files
    for title, files in title_map.items()
    if len(files) > 1
}

print(f"\nDuplicate titles: {len(duplicate_titles)}")
for title, files in list(duplicate_titles.items())[:50]:
    print(f' - "{title}"')
    for f in files:
        print("    ", f)


# Duplicate canonicals
canonical_map = {}
for r in records:
    if r["canonical"]:
        canonical_map.setdefault(r["canonical"], []).append(r["file"].as_posix())

duplicate_canonicals = {
    canonical: files
    for canonical, files in canonical_map.items()
    if len(files) > 1
}

print(f"\nDuplicate canonicals: {len(duplicate_canonicals)}")
for canonical, files in list(duplicate_canonicals.items())[:50]:
    print(" -", canonical)
    for f in files:
        print("    ", f)


# Canonical mismatch
canonical_mismatch = []

for r in records:
    expected = DOMAIN + r["route"]
    actual = r["canonical"]

    if actual and actual != expected:
        canonical_mismatch.append(
            f'{r["file"].as_posix()} | expected {expected} | got {actual}'
        )

report("Canonical mismatches", canonical_mismatch)


# Broken internal links
print(f"\nBroken internal links: {len(broken_links)}")

seen = set()
for source, href in broken_links:
    key = (source, href)

    if key in seen:
        continue

    seen.add(key)
    print(f" - {source} -> {href}")


# Sitemap
sitemap = Path("sitemap.xml")
sitemap_urls = set()

if sitemap.exists():
    xml = sitemap.read_text(errors="ignore")
    sitemap_urls = set(re.findall(r"<loc>(.*?)</loc>", xml))

expected_urls = {
    DOMAIN + r["route"]
    for r in records
    if r["file"].name == "index.html"
}

missing_from_sitemap = sorted(expected_urls - sitemap_urls)
extra_in_sitemap = sorted(sitemap_urls - expected_urls)

report("Index routes missing from sitemap", missing_from_sitemap)
report("Sitemap URLs without local index.html", extra_in_sitemap)


# Duplicate inserted blocks
duplicate_trustless = [
    f'{r["file"].as_posix()} ({r["trustless_blocks"]})'
    for r in records
    if r["trustless_blocks"] > 1
]

duplicate_tool_callouts = [
    f'{r["file"].as_posix()} ({r["tool_callouts"]})'
    for r in records
    if r["tool_callouts"] > 1
]

report("Pages with duplicate Trustless blocks", duplicate_trustless)
report("Pages with duplicate buyer-tool callouts", duplicate_tool_callouts)


# Summary
problems = (
    len(missing_titles)
    + len(missing_descriptions)
    + len(missing_canonicals)
    + len(duplicate_canonicals)
    + len(canonical_mismatch)
    + len(set(broken_links))
    + len(missing_from_sitemap)
    + len(duplicate_trustless)
    + len(duplicate_tool_callouts)
)

print("\n" + "=" * 72)

if problems == 0:
    print("AUDIT RESULT: CLEAN")
else:
    print(f"AUDIT RESULT: {problems} issue(s) worth reviewing")

print("=" * 72)
