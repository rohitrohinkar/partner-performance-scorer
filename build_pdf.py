"""One-page PDF for the application form. Usage: python build_pdf.py [app_url] [repo_url]"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image

app_url = sys.argv[1] if len(sys.argv) > 1 else "(Streamlit link)"
repo_url = sys.argv[2] if len(sys.argv) > 2 else "(GitHub link)"
summary = open("summary.md").read().split("\n", 2)[2].strip()

W, H = A4
c = canvas.Canvas("Partner_Performance_Scorer.pdf", pagesize=A4)
m = 16 * mm
y = H - m

c.setFont("Helvetica-Bold", 18); c.drawString(m, y, "Partner Performance Scorer"); y -= 7 * mm
c.setFont("Helvetica", 10.5); c.setFillGray(0.3)
c.drawString(m, y, "AI challenge submission, Rohit Rohinkar. Rules score the partner; AI writes the actions."); y -= 6 * mm
c.setFillGray(0)
c.setFont("Helvetica", 10)
for label, url in (("Live app:", app_url), ("Code and dataset:", repo_url)):
    c.setFont("Helvetica-Bold", 10); c.drawString(m, y, label)
    c.setFont("Helvetica", 10); c.setFillColorRGB(0.12, 0.37, 0.75); c.drawString(m + 32 * mm, y, url)
    if url.startswith("http"): c.linkURL(url, (m + 32 * mm, y - 1 * mm, W - m, y + 4 * mm))
    c.setFillGray(0); y -= 5 * mm
y -= 2 * mm

def para(text, width, y, size=10, leading=13.5):
    c.setFont("Helvetica", size)
    words, line = text.split(), ""
    for w in words:
        if c.stringWidth(line + " " + w, "Helvetica", size) > width: c.drawString(m, y, line.strip()); y -= leading; line = w
        else: line += " " + w
    c.drawString(m, y, line.strip()); return y - leading

c.setFont("Helvetica-Bold", 11); c.drawString(m, y, "Summary (100 words)"); y -= 5.5 * mm
y = para(summary, W - 2 * m, y) - 3 * mm

# crop each screenshot to the part that matters, then fit both into the space left on the page
ov = Image.open("shots/overview.png").crop((0, 0, 3000, 1700))
dd = Image.open("shots/drilldown.png").crop((640, 720, 2900, 1675))
shots = ((ov, "Portfolio view: weight sliders, Invest / Protect / Fix / Exit, score vs quarter-on-quarter trend, leaderboard."),
         (dd, "Drill-down: the planted 'big merchant going cold' story, the metric-by-metric reason for its score, and the recommended actions."))
avail = y - m - 12 * mm - 2 * 10 * mm  # footer + two captions
total_ratio = sum(i.size[1] / i.size[0] for i, _ in shots)
w = min(W - 2 * m, avail / total_ratio)
for img, cap in shots:
    iw, ih = img.size; h = w * ih / iw
    c.drawImage(ImageReader(img), m, y - h, w, h); y -= h + 4 * mm
    c.setFont("Helvetica-Oblique", 8.5); c.setFillGray(0.35); c.drawString(m, y, cap); c.setFillGray(0); y -= 6 * mm

c.setFont("Helvetica", 8.5); c.setFillGray(0.4)
c.drawString(m, m - 4 * mm, "Self-generated data, 30 partners, two quarters. No real companies or confidential information. Streamlit, pandas, Claude API.")
c.save(); print("Partner_Performance_Scorer.pdf")
