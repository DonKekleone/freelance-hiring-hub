from pathlib import Path
from datetime import date
from xml.sax.saxutils import escape

ROOT = Path(".")
DOMAIN = "https://freelancehiringhub.com"
TODAY = date.today().isoformat()

exclude_parts = {
    ".git",
    ".vercel",
    "node_modules",
}

urls = []

for f in ROOT.rglob("index.html"):
    if any(part in exclude_parts for part in f.parts):
        continue

    parent = f.parent.as_posix()

    if parent == ".":
        url = DOMAIN + "/"
    else:
        url = DOMAIN + "/" + parent.strip("/") + "/"

    urls.append(url)

urls = sorted(set(urls), key=lambda x: (x.count("/"), x))

xml = ['<?xml version="1.0" encoding="UTF-8"?>']
xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

for url in urls:
    xml.append("  <url>")
    xml.append(f"    <loc>{escape(url)}</loc>")
    xml.append(f"    <lastmod>{TODAY}</lastmod>")
    xml.append("  </url>")

xml.append("</urlset>")

Path("sitemap.xml").write_text("\n".join(xml) + "\n")

print(f"Built sitemap.xml with {len(urls)} URLs.")
