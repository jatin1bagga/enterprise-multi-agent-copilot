from pathlib import Path

import markdown2
from xhtml2pdf import pisa


def markdown_to_pdf(markdown_text: str, output_path: Path) -> None:
    html_body = markdown2.markdown(markdown_text, extras=["tables", "fenced-code-blocks"])
    html = f"""<html><head><meta charset="utf-8">
    <style>
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; }}
        h1 {{ color: #1a1a1a; }}
        h2 {{ color: #333333; margin-top: 1.2em; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 4px 8px; }}
    </style></head><body>{html_body}</body></html>"""

    with open(output_path, "wb") as f:
        result = pisa.CreatePDF(html, dest=f)
    if result.err:
        raise RuntimeError(f"Failed to render PDF report ({result.err} errors)")
