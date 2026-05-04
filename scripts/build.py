#!/usr/bin/env python3
"""Build the Visual Crime & Justice Resource site.

- Converts /guides/*.md to HTML pages with shared header, nav, footer.
- Generates downloadable PDFs of each guide using the same HTML + print CSS.
- Writes index.html and about.html.
- Stamps every page with a "Last updated" date.
"""

from __future__ import annotations

import datetime as _dt
import html as _html
import re
from pathlib import Path

import markdown  # type: ignore
from weasyprint import HTML, CSS  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
GUIDES_DIR = ROOT / "guides"
ASSETS_DIR = ROOT / "assets"
PDF_DIR = ROOT / "pdfs"
OUT_DIR = ROOT  # GitHub Pages serves from repo root

UPDATED = _dt.date.today().isoformat()

NAV = [
    ("index.html", "Home"),
    ("guide-1-journalists.html", "Guide 1 · Journalists"),
    ("guide-2-law-enforcement.html", "Guide 2 · Law Enforcement"),
    ("guide-3-public.html", "Guide 3 · Public"),
    ("scenario-pack.html", "Scenarios"),
    ("about.html", "About"),
]


def page(title: str, body_html: str, current: str, description: str) -> str:
    nav_html = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>'
        for href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_html.escape(title)} — Visual Crime &amp; Justice Resource</title>
  <meta name="description" content="{_html.escape(description)}">
  <meta name="theme-color" content="#f68212">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <a class="skip-link" href="#main">Skip to main content</a>
  <header class="site" role="banner">
    <div class="inner">
      <div class="brand">CrimRxiv Consortium</div>
      <h1><a href="index.html">Visual Crime &amp; Justice Resource</a></h1>
    </div>
  </header>
  <nav class="primary" role="navigation" aria-label="Primary">
    <ul>{nav_html}</ul>
  </nav>
  <main id="main" role="main">
    <article>
      {body_html}
    </article>
  </main>
  <footer class="site" role="contentinfo">
    <p>Last updated: <time datetime="{UPDATED}">{UPDATED}</time></p>
    <p>Open access. Licensed under
       <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>.
       Free to use, share, and adapt with attribution to Tara Abrahams and Scott Jacques
       (supported by <a href="https://www.crimrxiv.com/">CrimRxiv Consortium</a>).</p>
    <p>Source on
       <a href="https://github.com/crimconsortium/visual-crime-justice">GitHub</a>.</p>
  </footer>
</body>
</html>
"""


def md_to_html(md_text: str) -> tuple[str, str]:
    """Return (html_body, first_h1_title)."""
    md = markdown.Markdown(extensions=["extra", "toc", "sane_lists"])
    body = md.convert(md_text)
    # Pull out first H1 to use as title; remove from body to avoid duplicate
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.IGNORECASE | re.DOTALL)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "Untitled"
    return body, title


def build_guide(md_path: Path, out_name: str, description: str) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    body_html, title = md_to_html(md_text)
    body_html = (
        f'<p class="meta">Last updated {UPDATED} · '
        f'<a href="pdfs/{out_name.replace(".html", ".pdf")}">Download PDF</a></p>'
        + body_html
    )
    html = page(title, body_html, current=out_name, description=description)
    (OUT_DIR / out_name).write_text(html, encoding="utf-8")
    # PDF — same HTML, baseUrl points to repo root so CSS resolves
    pdf_html = html.replace('href="assets/style.css"', f'href="{ASSETS_DIR}/style.css"')
    pdf_path = PDF_DIR / out_name.replace(".html", ".pdf")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=pdf_html, base_url=str(ROOT)).write_pdf(
        str(pdf_path),
        stylesheets=[CSS(filename=str(ASSETS_DIR / "style.css"))],
    )
    print(f"  built {out_name} + PDF")


def build_index() -> None:
    body = f"""
<h1>Visual Crime &amp; Justice Resource</h1>
<p class="meta">Last updated {UPDATED}</p>
<p>An open-access, evidence-based practitioner resource on the ethical and evidentiary
use of images in crime, policing, and journalism. Free to use, share, and adapt under
<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
Produced by Tara Abrahams and Scott Jacques, supported by <a href="https://www.crimrxiv.com/">CrimRxiv Consortium</a>.</p>

<div class="callout">
  Written for three audiences: journalists and photojournalists, law enforcement and
  public safety professionals, and the general public. Updated quarterly with new
  peer-reviewed research, policy, and case practice.
</div>

<h2>Guides</h2>
<div class="cards">
  <div class="card">
    <h3>Guide 1 — Journalists &amp; Photojournalists</h3>
    <p>Ethical use of images in crime reporting: victims, bodycam footage, citizen
       video, and AI-generated imagery.</p>
    <p class="actions">
      <a href="guide-1-journalists.html">Read</a>
      <a href="pdfs/guide-1-journalists.pdf">PDF</a>
    </p>
  </div>
  <div class="card">
    <h3>Guide 2 — Law Enforcement</h3>
    <p>Visual evidence in policing: BWC policy and practice, citizen recording,
       crime-scene imagery, and footage release.</p>
    <p class="actions">
      <a href="guide-2-law-enforcement.html">Read</a>
      <a href="pdfs/guide-2-law-enforcement.pdf">PDF</a>
    </p>
  </div>
  <div class="card">
    <h3>Guide 3 — General Public</h3>
    <p>How crime images shape public understanding — and how to read them with more
       care.</p>
    <p class="actions">
      <a href="guide-3-public.html">Read</a>
      <a href="pdfs/guide-3-public.pdf">PDF</a>
    </p>
  </div>
  <div class="card">
    <h3>Scenario Pack</h3>
    <p>Eight realistic scenarios with discussion questions and model responses for
       newsroom, agency, and classroom use.</p>
    <p class="actions">
      <a href="scenario-pack.html">Read</a>
      <a href="pdfs/scenario-pack.pdf">PDF</a>
    </p>
  </div>
</div>

<h2>How this resource is built</h2>
<p>Every quarter, we review new peer-reviewed articles, policy documents, journalism
ethics guidelines, legal rulings, and notable case studies, then update each guide and
the scenario pack. The full source — including a research log of sources consulted — is
public on <a href="https://github.com/crimconsortium/visual-crime-justice">GitHub</a>.</p>

<h2>Guiding principles</h2>
<ul>
  <li>Accuracy over completeness.</li>
  <li>Flag uncertainty explicitly.</li>
  <li>Never reproduce copyrighted material.</li>
  <li>Always link to primary sources.</li>
  <li>Optimize for real-world utility for practitioners.</li>
</ul>
"""
    html = page(
        "Home",
        body,
        current="index.html",
        description=(
            "Open-access guides on the ethical and evidentiary use of images in crime, "
            "policing, and journalism. By Tara Abrahams and Scott Jacques, supported by "
            "CrimRxiv Consortium."
        ),
    )
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")
    print("  built index.html")


def build_about() -> None:
    body = f"""
<h1>About this resource</h1>
<p class="meta">Last updated {UPDATED}</p>

<p>The <strong>Visual Crime &amp; Justice Resource</strong> is an open-access,
evidence-based practitioner resource produced by Tara Abrahams and Scott Jacques,
supported by the <a href="https://www.crimrxiv.com/">CrimRxiv Consortium</a>. It is
written for three audiences: law enforcement and public safety professionals,
journalists and photojournalists who cover crime, and the general public.</p>

<h2>Why we built it</h2>
<p>Visual evidence — body-worn camera video, bystander recordings, crime-scene
photographs, news images, and now AI-generated content — has become central to how
the public understands crime and how the justice system processes it. The research
on how that imagery is interpreted is rich but often siloed by discipline. This
resource brings the practical implications together in plain language, with citations
to primary sources.</p>

<h2>How it is updated</h2>
<p>Each quarter, the maintainers (a) search for new peer-reviewed articles, policy
documents, journalism ethics guidance, legal rulings, and notable case studies;
(b) update each guide and the scenario pack to incorporate new findings; (c)
rebuild the site; and (d) commit changes to the
<a href="https://github.com/crimconsortium/visual-crime-justice">public repository</a>
with a summary of what changed and why.</p>

<h2>License</h2>
<p>All content is released under
<a href="https://creativecommons.org/licenses/by/4.0/" rel="license">Creative Commons
Attribution 4.0</a>. You may use, share, and adapt this material with attribution to
Tara Abrahams and Scott Jacques (supported by the CrimRxiv Consortium) and a link
back to this site.</p>

<h2>Contact &amp; contributions</h2>
<p>Open an issue or pull request on
<a href="https://github.com/crimconsortium/visual-crime-justice">GitHub</a> to
suggest sources, propose corrections, or contribute new scenarios.</p>
"""
    html = page(
        "About",
        body,
        current="about.html",
        description="About the Visual Crime & Justice Resource and how it is maintained.",
    )
    (OUT_DIR / "about.html").write_text(html, encoding="utf-8")
    print("  built about.html")


def main() -> None:
    print("Building site…")
    build_index()
    build_about()
    build_guide(
        GUIDES_DIR / "guide-1-journalists.md",
        "guide-1-journalists.html",
        "Ethical use of images in crime reporting for journalists and photojournalists.",
    )
    build_guide(
        GUIDES_DIR / "guide-2-law-enforcement.md",
        "guide-2-law-enforcement.html",
        "Visual evidence and policing — BWC, citizen footage, and crime-scene imagery.",
    )
    build_guide(
        GUIDES_DIR / "guide-3-public.md",
        "guide-3-public.html",
        "How images shape public understanding of crime — a guide for everyone.",
    )
    build_guide(
        GUIDES_DIR / "scenario-pack.md",
        "scenario-pack.html",
        "Discussion scenarios for newsrooms, agencies, and classrooms.",
    )
    print("Done.")


if __name__ == "__main__":
    main()
