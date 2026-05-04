# Image Ethics in Crime & Justice

Open-access, evidence-based practitioner resource on the ethical and evidentiary use of images in crime, policing, and journalism. Produced by Tara Abrahams and Scott Jacques, supported by [CrimRxiv Consortium](https://www.crimrxiv.com/).

**Site:** https://crimconsortium.github.io/visual-crime-justice/
**License:** [CC BY 4.0](LICENSE)

## What's here

- `guides/` — Source markdown for the four practitioner guides
- `assets/` — Site CSS
- `scripts/build.py` — Builds HTML pages and downloadable PDFs
- `pdfs/` — Generated PDFs (committed for direct download)
- `*.html` — Built site, served by GitHub Pages from repo root
- `research_log.md` — Sources reviewed for the most recent update cycle

## Update cycle

The maintainers refresh this resource quarterly:

1. Search for new peer-reviewed research, policy, ethics guidance, legal rulings, and case studies
2. Update each guide and the scenario pack
3. Rebuild the site (`python scripts/build.py`)
4. Commit and push with a summary of changes

## Build locally

```bash
pip install markdown weasyprint
python scripts/build.py
```

## Contributing

Open an issue or pull request to suggest sources, propose corrections, or contribute new scenarios.
