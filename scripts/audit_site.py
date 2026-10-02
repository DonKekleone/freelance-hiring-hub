from pathlib import Path
from html.parser import HTMLParser
from collections import defaultdict

ROOT = Path(".")

IGNORE = {
    ".git",
    ".vercel",
    "node_modules",
}

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.title = ""
        self.in_title = False

        self.h1_count = 0
        self.h1_text = []
        self.in_h1 = False

        self.description = None
        self.canonical = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "title":
            self.in_title = True

        if tag == "h1":
            self.h1_count += 1
            self.in_h1 = True

        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "").strip()

        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "").strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

        if tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data

        if self.in_h1:
            self.h1_text.append(data)

pages = []

for html_file in ROOT.rglob("index.html"):
    if any(part in IGNORE for part in html_file.parts):
        continue

    parser = AuditParser()

    try:
        parser.feed(html_file.read_text())
    except Exception as e:
        print(f"PARSE ERROR: {html_file}: {e}")
        continue

    title = parser.title.strip()
    h1 = " ".join(
        " ".join(parser.h1_text).split()
    )

    pages.append({
        "file": str(html_file),
        "title": title,
        "description": parser.description,
        "canonical": parser.canonical,
        "h1_count": parser.h1_count,
        "h1": h1,
    })

issues = []

for page in pages:
    f = page["file"]

    if not page["title"]:
        issues.append((f, "missing title"))

    if not page["description"]:
        issues.append((f, "missing meta description"))

    if not page["canonical"]:
        issues.append((f, "missing canonical"))

    if page["h1_count"] == 0:
        issues.append((f, "missing H1"))

    elif page["h1_count"] > 1:
        issues.append(
            (f, f'{page["h1_count"]} H1 elements')
        )

titles = defaultdict(list)
canonicals = defaultdict(list)

for page in pages:
    if page["title"]:
        titles[page["title"]].append(page["file"])

    if page["canonical"]:
        canonicals[page["canonical"]].append(page["file"])

for title, files in titles.items():
    if len(files) > 1:
        issues.append((
            ", ".join(files),
            f'duplicate title: "{title}"'
        ))

for canonical, files in canonicals.items():
    if len(files) > 1:
        issues.append((
            ", ".join(files),
            f'duplicate canonical: {canonical}'
        ))

print()
print("SITE AUDIT")
print("=" * 72)
print(f"HTML pages checked: {len(pages)}")

if issues:
    print(f"Issues found:      {len(issues)}")
    print()

    for file, issue in issues:
        print(f"{issue}")
        print(f"  {file}")
else:
    print("Issues found:      0")
    print()
    print("Core title / description / canonical / H1 checks clean.")

print()
print("SECTION COUNTS")
print("=" * 72)

section_counts = defaultdict(int)

for page in pages:
    parts = Path(page["file"]).parts

    if len(parts) == 1:
        section = "/"
    else:
        section = parts[0]

    section_counts[section] += 1

for section, count in sorted(
    section_counts.items(),
    key=lambda x: (-x[1], x[0])
):
    print(f"{count:>3}  {section}")

