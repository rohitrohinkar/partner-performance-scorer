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

# ---------- page 2: approach ----------
c.showPage(); y = H - m
def h(text, y, size=13):
    c.setFont("Helvetica-Bold", size); c.setFillGray(0); c.drawString(m, y, text); return y - 6 * mm
def bullets(items, y):
    for it in items:
        c.setFont("Helvetica", 10); c.drawString(m + 3 * mm, y, u"\u2022")
        xs = m + 8 * mm; words, line = it.split(), ""
        for w_ in words:
            if c.stringWidth(line + " " + w_, "Helvetica", 10) > W - m - xs: c.drawString(xs, y, line.strip()); y -= 5 * mm; line = w_
            else: line += " " + w_
        c.drawString(xs, y, line.strip()); y -= 5.5 * mm
    return y - 2 * mm

y = h("Approach", y, 16)
y = para("The brief asks for an AI that scores partner performance and recommends improvement actions. The design "
         "splits that into two jobs with different trust requirements. Scoring is deterministic: six inputs a Careem "
         "partner team already tracks, each normalised to 0-100 and combined with weights the user can change. That "
         "makes every score auditable and arguable, which is what finance and partner managers need. AI is applied only "
         "where language and judgment add value: turning the weakest metrics into three specific actions and a "
         "business-review brief the partner manager can take into the room.", W - 2 * m, y) - 3 * mm

y = h("Scoring rules", y)
rows = [("Metric", "Scale (0-100)", "Weight", "Why it matters"),
        ("GMV attainment", "GMV / target, capped at 150%", "30", "The number the business tracks"),
        ("Fulfilment rate", "completed / received", "15", "Cancellations cost the customer"),
        ("Repeat rate", "60% returning customers = 100", "20", "Busy vs. partners customers return to"),
        ("On-time rate", "share within promised window", "10", "Late is how a customer is lost"),
        ("Tools adopted", "5 partner tools = 100", "10", "Leading indicator of next quarter GMV"),
        ("Engagement", "review attended 50 + logins up to 50", "15", "Shows two quarters before GMV does")]
cols = (m, m + 34 * mm, m + 100 * mm, m + 116 * mm)
for i, r in enumerate(rows):
    c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 9.5)
    for x, t in zip(cols, r): c.drawString(x, y, t)
    y -= 5.5 * mm
    if i == 0: c.setLineWidth(0.3); c.line(m, y + 3.5 * mm, W - m, y + 3.5 * mm)
y -= 2 * mm
y = para("Quadrants: a score of 60 or more is strong. A quarter-on-quarter drop of more than 3 points counts as "
         "slipping; smaller moves are treated as noise. Invest = strong and holding. Protect = strong but slipping. "
         "Fix = weak but not sliding. Exit = weak and falling.", W - 2 * m, y) - 3 * mm

y = h("AI layer", y)
y = bullets(["For the selected partner the app sends the six normalised metrics for both quarters, the raw numbers and the "
             "quadrant to Claude (claude-opus-5-5 via the Anthropic API) and asks for three actions, each tied to a weak "
             "metric with an owner and a 30-day measurable, plus a four-sentence business-review brief.",
             "The score itself never touches the model. The prompt is grounded in the facts shown on screen, so the "
             "narrative can be checked against the table beside it.",
             "The public demo runs the rule-based fallback: a playbook keyed to the two weakest metrics. Adding an "
             "ANTHROPIC_API_KEY in Streamlit secrets switches the same panel to AI-written output with no code change."], y)

y = h("Data", y)
y = bullets(["Self-generated: 30 partners (15 merchants, 9 fleet partners, 6 brand partners) across UAE, KSA, Egypt and "
             "Pakistan, two quarters, GMV in AED thousands. No real companies, no confidential information.",
             "Four stories are planted so the demo has something to find: a large UAE merchant going cold, a small KSA "
             "brand partner tripling GMV, a merchant hitting target while disengaging, and a busy fleet whose fulfilment "
             "is sliding."], y)

y = h("Build", y)
y = bullets(["Python, pandas, Streamlit (Community Cloud), Anthropic SDK, reportlab for this document. Scoring lives in "
             "scoring.py with a unit test; the UI in app.py. About two hours end to end.",
             "Live app: " + app_url + "   Code and dataset: " + repo_url], y)

c.setFont("Helvetica", 8.5); c.setFillGray(0.4)
c.drawString(m, m - 4 * mm, "Rohit Rohinkar  |  +91 84466 02445  |  linkedin.com/in/rohitrohinkar  |  rohit.rohinkar@gmail.com")
c.save(); print("Partner_Performance_Scorer.pdf")
