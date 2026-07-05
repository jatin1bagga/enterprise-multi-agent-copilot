import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

import pandas as pd  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

OUTPUT_DIR = SCRIPT_DIR / "sample_data"


def make_sample_csv() -> Path:
    df = pd.DataFrame(
        {
            "region": ["North", "South", "East", "West", "North", "South", "East", "West"],
            "quarter": ["Q1", "Q1", "Q1", "Q1", "Q2", "Q2", "Q2", "Q2"],
            "revenue": [120000, 98000, 105000, None, 130000, 102000, 111000, 97000],
            "expenses": [80000, 75000, 78000, 82000, 85000, 79000, 80000, 76000],
            "headcount": [12, 9, 10, 8, 13, 9, 11, 8],
        }
    )
    path = OUTPUT_DIR / "sample.csv"
    df.to_csv(path, index=False)
    return path


def make_sample_pdf() -> Path:
    path = OUTPUT_DIR / "sample.pdf"
    c = canvas.Canvas(str(path))
    c.drawString(72, 750, "Enterprise Operations Handbook")
    c.drawString(72, 720, "Page 1: Refund Policy")
    c.drawString(72, 700, "Customers may request a refund within 30 days of purchase,")
    c.drawString(72, 685, "provided the product is unused and in its original packaging.")
    c.showPage()
    c.drawString(72, 750, "Page 2: Support Escalation")
    c.drawString(72, 720, "Tier 1 support handles general inquiries. Issues unresolved after")
    c.drawString(72, 705, "48 hours are escalated to Tier 2 engineering support.")
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = make_sample_csv()
    pdf_path = make_sample_pdf()
    print(f"Wrote {csv_path}")
    print(f"Wrote {pdf_path}")
