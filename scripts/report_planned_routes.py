from pathlib import Path
from html.parser import HTMLParser
from collections import Counter, defaultdict
from urllib.parse import urlparse

ROOT = Path(".")
PLANNED_FILE = Path("planned_routes.txt")

IGNORE = {
    ".git",
    ".vercel",
    "node_modules",
}

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return

        href = dict(attrs).get("href")

        if href:
            self.links.append(href)

planned = {
    line.strip()
    for line in PLANNED_FILE.read_text().splitlines()
    if line.strip() and not line.strip().startswith("#")
}

counts = Counter()
sources = defaultdict(set)

for html_file in ROOT.rglob("*.html"):
    if any(part in IGNORE for part in html_file.parts):
        continue

    parser = Parser()

    try:
        parser.feed(html_file.read_text())
    except Exception:
        continue

    for href in parser.links:
        parsed = urlparse(href)

        if parsed.scheme in {"http", "https"}:
            continue

        route = parsed.path

        if route in planned:
            counts[route] += 1
            sources[route].add(str(html_file))

print("\nPLANNED ROUTE PRIORITY")
print("=" * 72)

referenced = []

for route in planned:
    if counts[route]:
        referenced.append(route)

for route in sorted(
    referenced,
    key=lambda r: (-counts[r], r)
):
    print(f"{counts[route]:>3} refs  {route}")

print("\nUNREFERENCED PLANNED ROUTES")
print("=" * 72)

unreferenced = sorted(
    route
    for route in planned
    if counts[route] == 0
)

for route in unreferenced:
    print(route)

print()
print(f"Planned routes total:      {len(planned)}")
print(f"Referenced planned routes: {len(referenced)}")
print(f"Unreferenced planned:      {len(unreferenced)}")
print(f"Total planned references:  {sum(counts.values())}")
