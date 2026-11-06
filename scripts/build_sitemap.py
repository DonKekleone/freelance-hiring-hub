from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape

ROOT = Path(".")
DOMAIN = "https://freelancehiringhub.com"

exclude_parts = {".git", ".vercel", "node_modules"}

rows = []

for f in ROOT.rglob("index.html"):
    if any(part in exclude_parts for part in f.parts):
        continue
    parent = f.parent.as_posix()
    if parent == ".":
        url = DOMAIN + "/"
    else:
        url = DOMAIN + "/" + parent.strip("/") + "/"
    lastmod = datetime.fromtimestamp(f.stat().st_mtime).date().isoformat()
    rows.append((url, lastmod))

rows = sorted(set(rows), key=lambda x: (x[0].count("/"), x[0]))

xml = ['<?xml version="1.0" encoding="UTF-8"?>']
xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
for url, lastmod in rows:
    xml.append("  <url>")
    xml.append(f"    <loc>{escape(url)}</loc>")
    xml.append(f"    <lastmod>{lastmod}</lastmod>")
    xml.append("  </url>")
xml.append("</urlset>")

Path("sitemap.xml").write_text("\n".join(xml) + "\n")
print(f"Built sitemap.xml with {len(rows)} URLs.")
