"""Markdown → HTML → tagged PDF via WeasyPrint. Output is PDF/UA-1 where supported."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

import markdown as md_lib
from ds_common.logging import get_logger

log = get_logger(__name__)

MD_EXTENSIONS = ["tables", "toc", "attr_list", "fenced_code", "sane_lists", "md_in_html"]


def render_pdf(md_path: Path | None, out_path: Path) -> Path:
    if md_path is None or not md_path.exists():
        raise FileNotFoundError(f"Cannot render PDF: source markdown missing at {md_path}")

    md_text = md_path.read_text()
    body_html = md_lib.markdown(md_text, extensions=MD_EXTENSIONS)
    css_path = resources.files("site_dossier.render").joinpath("templates/dossier.css")
    css_text = css_path.read_text()

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Site Dossier</title>
</head>
<body>
{body_html}
</body>
</html>
"""

    # WeasyPrint is heavy; import lazily so importing the package stays cheap.
    try:
        from weasyprint import CSS, HTML
    except Exception as exc:
        log.warning("pdf.weasyprint_unavailable", error=str(exc))
        raise

    HTML(
        string=full_html, base_url=str(md_path.parent)
    ).write_pdf(
        target=str(out_path),
        stylesheets=[CSS(string=css_text)],
        pdf_variant="pdf/ua-1",
    )
    return out_path
