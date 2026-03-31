#!/usr/bin/env python3
"""
build.py — Parses README.md and renders index.html via a Jinja2 template.

README format expected:
  ## Personal Blogs
  | Name | Tags |
  | --- | --- |
  | [Author Name](https://url) | tag1, tag2 |

  ## Company Blogs
  * [Company Name](https://url)
"""

import re
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT     = Path(__file__).parent.parent   # repo root
README   = ROOT / "README.md"
TEMPLATE = "template.html"               # relative to scripts/
OUTPUT   = ROOT / "index.html"


# ── Parsers ────────────────────────────────────────────────────────────────

def parse_markdown_link(text: str) -> tuple[str, str]:
    """Extract (label, url) from a Markdown link like [Label](url)."""
    m = re.search(r'\[([^\]]+)\]\(([^)]+)\)', text.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return text.strip(), ""


def parse_personal_blogs(readme: str) -> list[dict]:
    section = re.search(
        r'##\s+Personal Blogs\s*\n(.*?)(?=\n##|\Z)',
        readme, re.DOTALL | re.IGNORECASE,
    )
    if not section:
        print("WARNING: '## Personal Blogs' section not found in README")
        return []

    blogs = []
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[\s\-|]+\|$", line):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
        name, url = parse_markdown_link(cols[0])
        if not name or not url:
            continue
        tags = [t.strip().lower() for t in cols[1].split(",") if t.strip()]
        blogs.append({"name": name, "url": url, "tags": tags})

    return blogs


def parse_company_blogs(readme: str) -> list[dict]:
    section = re.search(
        r'##\s+Company Blogs\s*\n(.*?)(?=\n##|\Z)',
        readme, re.DOTALL | re.IGNORECASE,
    )
    if not section:
        print("WARNING: '## Company Blogs' section not found in README")
        return []

    companies = []
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line.startswith("*") and not line.startswith("-"):
            continue
        name, url = parse_markdown_link(line)
        if name and url:
            companies.append({"name": name, "url": url})

    return companies


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if not README.exists():
        print(f"ERROR: {README} not found", file=sys.stderr)
        sys.exit(1)

    readme_text = README.read_text(encoding="utf-8")

    personal  = parse_personal_blogs(readme_text)
    companies = parse_company_blogs(readme_text)
    all_tags  = sorted({t for b in personal for t in b["tags"]})

    print(f"  ✓ Parsed {len(personal)} personal blogs")
    print(f"  ✓ Parsed {len(companies)} company blogs")
    print(f"  ✓ Collected {len(all_tags)} unique tags")

    # Jinja2 environment — templates live in scripts/
    env = Environment(
        loader=FileSystemLoader(str(Path(__file__).parent)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template(TEMPLATE)

    html = template.render(
        personal_blogs=personal,
        company_blogs=companies,
        all_tags=all_tags,
        stats={
            "personal":  len(personal),
            "companies": len(companies),
            "topics":    len(all_tags),
        },
    )

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  ✓ Written → {OUTPUT}")


if __name__ == "__main__":
    main()
