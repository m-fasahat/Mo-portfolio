#!/usr/bin/env python3
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from PIL import Image

IMG = "/sessions/stoic-dreamy-allen/mnt/figure-detailer"
OUT = "/sessions/stoic-dreamy-allen/mnt/outputs/Smart-Figure-Detailer.pdf"

PW, PH = A4                       # 595.27 x 841.89
ML = MR = 42
MT = 40
MB = 34
CW = PW - ML - MR                # content width
INK   = HexColor("#111111")
SUB   = HexColor("#777777")
LINE  = HexColor("#cccccc")
LIGHT = HexColor("#f2f2f2")

c = canvas.Canvas(OUT, pagesize=A4)

def aspect(path):
    im = Image.open(path); return im.size[0] / im.size[1]

def img_h(path, w):
    return w / aspect(path)

# ---------- text styles ----------
body = ParagraphStyle("body", fontName="Helvetica", fontSize=8.6, leading=12.6,
                      textColor=INK, alignment=TA_JUSTIFY)
stepname = ParagraphStyle("sn", fontName="Helvetica-Bold", fontSize=7.5, leading=10,
                          textColor=INK)
stepdesc = ParagraphStyle("sd", fontName="Helvetica", fontSize=7.3, leading=9.8,
                          textColor=SUB)

def draw_para(style, text, x, y_top, w):
    p = Paragraph(text, style)
    pw, ph = p.wrap(w, 1000)
    p.drawOn(c, x, y_top - ph)
    return ph

def label(x, y, num, name):
    c.setFillColor(SUB); c.setFont("Courier", 7)
    c.drawString(x, y, num)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 7.5)
    c.drawString(x + 18, y, name)
    # letter spacing emulation not needed; keep tidy

def caption(x, y, text, w):
    st = ParagraphStyle("cap", fontName="Helvetica", fontSize=6.8, leading=8.8, textColor=SUB)
    return draw_para(st, text, x, y, w)

def place_img(path, x, y_top, w):
    h = img_h(path, w)
    c.drawImage(path, x, y_top - h, width=w, height=h, mask='auto')
    return h

y = PH - MT

# ================= HEADER =================
c.setFillColor(INK)
c.setFont("Helvetica", 22)
c.drawString(ML, y - 18, "Smart Figure Detailer")
c.setFillColor(SUB); c.setFont("Helvetica", 8)
c.drawRightString(PW - MR, y - 8,  "Computational / 2026")
c.drawRightString(PW - MR, y - 20, "AI Workflow  —  ComfyUI · SAM · Detailer")
y -= 30
c.setStrokeColor(LINE); c.setLineWidth(0.8)
c.line(ML, y, PW - MR, y)
y -= 16

# ================= INTRO =================
intro = ("In a wide architectural rendering, the scale-figures that give a scene life often occupy "
         "only a few hundred pixels &mdash; too little for a diffusion model to resolve a believable "
         "face, hands, or fall of fabric. <b>Smart Figure Detailer</b> is a computational workflow "
         "that fixes exactly this: a segmentation model isolates every person, each figure is upscaled "
         "and passed through a detail pass that rebuilds features, clothing folds, and contact shadows, "
         "then composites them back into the original render. The building, lighting, and composition "
         "stay untouched &mdash; only the people are quietly brought up to standard.")
y -= draw_para(body, intro, ML, y, CW)
y -= 18

# ================= BEFORE / AFTER =================
label(ML, y, "□", "BEFORE / AFTER")
y -= 12
gap = 14
iw = (CW - gap) / 2
h1 = place_img(os.path.join(IMG, "fd-orig-comp.jpg"), ML, y, iw)
place_img(os.path.join(IMG, "fd-enhanced.jpg"), ML + iw + gap, y, iw)
# tags
c.setFillColor(SUB); c.setFont("Helvetica-Bold", 6.5)
c.drawString(ML, y - h1 - 8, "ORIGINAL")
c.drawString(ML + iw + gap, y - h1 - 8, "ENHANCED")
y -= h1 + 12
cap = ("The scene is identical &mdash; only the figures change. Left: raw AI figures read as flat "
       "placeholders. Right: faces, fabric, and grounded shadows rebuilt at full fidelity.")
y -= caption(ML, y, cap, CW)
y -= 16

# ================= PROCESS STEPS =================
c.setStrokeColor(LINE); c.setLineWidth(0.6)
c.line(ML, y, PW - MR, y)
y -= 12
steps = [
    ("01", "Detect &amp; Isolate", "A Segment-Anything (SAM) pass finds each figure and outputs a binary mask, separating people from the scene."),
    ("02", "Upscale", "The masked figures are cropped and upscaled, giving the model enough resolution to work with &mdash; sharper, but not yet refined."),
    ("03", "Enhance", "A detail pass rebuilds faces, fabric, and shadows at full fidelity, then composites the result back into the render."),
]
col_gap = 16
col_w = (CW - 2 * col_gap) / 3
y_steps_top = y
max_h = 0
for i, (num, name, desc) in enumerate(steps):
    x = ML + i * (col_w + col_gap)
    c.setFillColor(SUB); c.setFont("Courier", 7); c.drawString(x, y - 7, num)
    yy = y - 18
    hn = draw_para(stepname, name, x, yy, col_w); yy -= hn + 2
    hd = draw_para(stepdesc, desc, x, yy, col_w)
    total = 18 + hn + 2 + hd
    max_h = max(max_h, total)
y -= max_h + 18

# ================= PIPELINE STRIP =================
c.setStrokeColor(LINE); c.setLineWidth(0.6)
c.line(ML, y, PW - MR, y)
y -= 12
label(ML, y, "□", "THE PIPELINE")
y -= 12
pics = [
    ("fd-original.jpg", "Original render"),
    ("fd-mask.png", "Detect & mask"),
    ("fd-upscaled.jpg", "Upscaled"),
    ("fd-enhanced.jpg", "Enhanced"),
]
g = 10
pw = (CW - 3 * g) / 4
ph_img = 0
for i, (fn, lab) in enumerate(pics):
    x = ML + i * (pw + g)
    h = place_img(os.path.join(IMG, fn), x, y, pw)
    ph_img = h
    c.setFillColor(SUB); c.setFont("Helvetica", 6.2)
    c.drawString(x, y - h - 7, lab)
y -= ph_img + 18

# ================= DETAIL ROW =================
c.setStrokeColor(LINE); c.setLineWidth(0.6)
c.line(ML, y, PW - MR, y)
y -= 12
label(ML, y, "□", "DETAIL  —  ONE FIGURE")
y -= 12
# progress (wide) + two tall crops, matched height
row_h = y - MB - 10
row_h = min(row_h, 150)
prog = os.path.join(IMG, "fd-progress.jpg")
pw_prog = row_h * aspect(prog)
crop1 = os.path.join(IMG, "fd-detect.jpg")
crop2 = os.path.join(IMG, "fd-enhanced-crop.jpg")
cw1 = row_h * aspect(crop1)
cw2 = row_h * aspect(crop2)
gg = 14
total_w = pw_prog + gg + cw1 + 8 + cw2
x0 = ML
c.drawImage(prog, x0, y - row_h, width=pw_prog, height=row_h, mask='auto')
c.setFillColor(SUB); c.setFont("Helvetica", 6.2)
c.drawString(x0, y - row_h - 7, "Original -> upscaled -> enhanced")
xc = x0 + pw_prog + gg
c.drawImage(crop1, xc, y - row_h, width=cw1, height=row_h, mask='auto')
c.drawImage(crop2, xc + cw1 + 8, y - row_h, width=cw2, height=row_h, mask='auto')
c.drawString(xc, y - row_h - 7, "Before")
c.drawString(xc + cw1 + 8, y - row_h - 7, "After")
# side caption to the right
cap_x = xc + cw1 + 8 + cw2 + 14
cap_w = PW - MR - cap_x
if cap_w > 80:
    caption(cap_x, y - 6,
            "Up close, the gain is clearest: defined features, readable posture, and a grounded "
            "shadow &mdash; without altering the figure's placement or scale.", cap_w)
y -= row_h + 12

# ================= FOOTER =================
c.setStrokeColor(LINE); c.setLineWidth(0.6)
c.line(ML, MB + 6, PW - MR, MB + 6)
c.setFillColor(SUB); c.setFont("Helvetica", 6.5)
c.drawString(ML, MB - 4, "Mohammad Fasahat")
c.drawRightString(PW - MR, MB - 4, "Portfolio  —  Smart Figure Detailer")

c.showPage()
c.save()
print("Wrote", OUT)
