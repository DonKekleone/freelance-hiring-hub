from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = Path(".")
DOMAIN = "freelancehiringhub.com"

IGNORE_PARTS = {
    ".git",
    ".vercel",
    "node_modules",
}

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return

        href = dict(attrs).get("href")

        if href:
            self.links.append(href)

def should_skip(path):
    return any(part in IGNORE_PARTS for part in path.parts)

def resolve_internal(href):
    if href.startswith("#"):
        return None

    if href.startswith("mailto:") or href.startswith("tel:"):
        return None

    parsed = urlparse(href)

    if parsed.scheme in {"http", "https"}:
        if parsed.netloc not in {DOMAIN, "www." + DOMAIN}:
            return None
        href = parsed.path

    if not href.startswith("/"):
        return None

    clean = href.split("#", 1)[0].split("?", 1)[0]

    if not clean:
        return None

    return clean

def target_exists(route):
    if route == "/":
        return Path("index.html").exists()

    path = Path(route.lstrip("/"))

    if path.suffix:
        return path.exists()

    return (path / "index.html").exists()

planned_file = Path("planned_routes.txt")

planned = set()

if planned_file.exists():
    planned = {
        line.strip()
        for line in planned_file.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

broken = []
planned_links = []

for html_file in ROOT.rglob("*.html"):
    if should_skip(html_file):
        continue

    parser = LinkParser()

    try:
        parser.feed(html_file.read_text())
    except Exception as e:
        print(f"Could not parse {html_file}: {e}")
        continue

    for href in parser.links:
        route = resolve_internal(href)

        if route and not target_exists(route):
            if route in planned:
                planned_links.append((str(html_file), href))
            else:
                broken.append((str(html_file), href))

if planned_links:
    print(f"\nPlanned routes referenced: {len(planned_links)}")

if broken:
    print(f"\nBROKEN internal links: {len(broken)}\n")

    for source, href in broken:
        print(f"{source} -> {href}")

    raise SystemExit(1)

print("No accidental broken internal links.")
