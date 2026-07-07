from __future__ import annotations

import csv
import hashlib
import os
import shutil
import textwrap
import zipfile
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(r"C:\Users\bolao\Documents\Codex\2026-07-04\https-us06web-zoom-us-j-84402744475")
WORK = ROOT / "work"
OUTPUTS = ROOT / "outputs"
DOWNLOADS = Path(r"C:\Users\bolao\Downloads")

PACKAGE_NAME = "Tapeout July_04_DO_OVER_VLSI_FLOW"
PKG = WORK / PACKAGE_NAME
OUT_ZIP = OUTPUTS / f"{PACKAGE_NAME}.zip"
DL_ZIP = DOWNLOADS / f"{PACKAGE_NAME}.zip"

TEMPLATE_IMAGE = Path(r"C:\Users\bolao\AppData\Local\Temp\codex-clipboard-4f7ec1b9-c727-41b0-886a-e4379158e0cd.png")
SCHEMATIC_PKG = WORK / "Tapeout July_04_SCHEMATIC_TRANSMITTAL_RELEASE_PENDING"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def mkdirs() -> None:
    if PKG.exists():
        shutil.rmtree(PKG)
    for folder in [
        PKG / "00_read_me",
        PKG / "01_reference_template",
        PKG / "02_do_over_flow_chart",
        PKG / "03_engineering_instructions",
        PKG / "04_release_outputs_required",
        PKG / "05_schematic_reference",
        PKG / "06_validation_context",
    ]:
        folder.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = {
        "regular": [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ],
        "bold": [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
        ],
    }
    for candidate in candidates[name]:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def wrap_to_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        words = raw.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            bbox = draw.textbbox((0, 0), trial, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], fill: tuple[int, int, int], width: int = 5) -> None:
    draw.line([start, end], fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    size = 18
    p1 = (x2, y2)
    p2 = (int(x2 - ux * size + px * size * 0.55), int(y2 - uy * size + py * size * 0.55))
    p3 = (int(x2 - ux * size - px * size * 0.55), int(y2 - uy * size - py * size * 0.55))
    draw.polygon([p1, p2, p3], fill=fill)


def draw_chip(draw: ImageDraw.ImageDraw, cx: int, cy: int, color: tuple[int, int, int]) -> None:
    size = 56
    for i in range(-2, 3):
        draw.line((cx - size // 2 - 12, cy + i * 10, cx - size // 2, cy + i * 10), fill=color, width=4)
        draw.line((cx + size // 2, cy + i * 10, cx + size // 2 + 12, cy + i * 10), fill=color, width=4)
        draw.line((cx + i * 10, cy - size // 2 - 12, cx + i * 10, cy - size // 2), fill=color, width=4)
        draw.line((cx + i * 10, cy + size // 2, cx + i * 10, cy + size // 2 + 12), fill=color, width=4)
    draw.rounded_rectangle((cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2), radius=8, outline=color, width=5)
    draw.rectangle((cx - 13, cy - 13, cx + 13, cy + 13), outline=color, width=3)


def draw_flow_chart(path_png: Path, path_pdf: Path) -> None:
    W, H = 2600, 1800
    img = Image.new("RGB", (W, H), "#f6f8fb")
    draw = ImageDraw.Draw(img)
    title_font = load_font("bold", 50)
    subtitle_font = load_font("regular", 28)
    card_title_font = load_font("bold", 29)
    card_subtitle_font = load_font("bold", 22)
    body_font = load_font("regular", 22)
    small_font = load_font("regular", 19)
    flow_font = load_font("bold", 22)

    navy = (16, 70, 104)
    ink = (32, 42, 52)
    mid = (98, 111, 125)

    draw.rounded_rectangle((260, 45, 2340, 145), radius=22, fill=navy)
    title = "TFLN_AI_NODE_X2 - DO-OVER VLSI / BOARD RELEASE FLOW"
    tb = draw.textbbox((0, 0), title, font=title_font)
    draw.text(((W - (tb[2] - tb[0])) // 2, 62), title, fill="white", font=title_font)

    draw.rounded_rectangle((570, 185, 2030, 285), radius=18, fill="#dceff8", outline="#7baac1", width=4)
    subtitle = "Requirement reset -> schematic/BOM closure -> PCB ECO -> verification -> release"
    sb = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    text_area_left = 620
    text_area_right = 1875
    draw.text((text_area_left + ((text_area_right - text_area_left) - (sb[2] - sb[0])) // 2, 218), subtitle, fill=ink, font=subtitle_font)
    draw_chip(draw, 1945, 235, navy)

    cards = [
        {
            "n": "1",
            "title": "SPECIFICATION RESET",
            "sub": "Requirement domain",
            "body": [
                "Freeze 295.0 x 140.0 mm reference envelope.",
                "Confirm 56.0 mm height note, rails, holes, connectors, airflow, heatsink.",
                "Output: signed mechanical requirement and ECO scope.",
            ],
            "color": "#d7f0d3",
            "accent": "#58a65c",
        },
        {
            "n": "2",
            "title": "FRONT-END DESIGN",
            "sub": "Schematic and logical intent",
            "body": [
                "Close schematic intent for U1 NCE-A, U4 NCE-B, U3 TFLN PIC, HBM, PCIe, control, and power.",
                "Resolve 199 net conflicts and 199 extra footprint findings.",
                "Output: clean schematic and netlist.",
            ],
            "color": "#ffe3bf",
            "accent": "#df9343",
        },
        {
            "n": "3",
            "title": "ANALOG / TFLN",
            "sub": "Optical and RF domain",
            "body": [
                "Validate U3 TFLN_PIC_4xMZM, RF drivers U50-U53, bias, monitor, MZM lanes, and low-noise rails.",
                "Output: analog/optical pin map and RF/bias constraints.",
            ],
            "color": "#fff1b8",
            "accent": "#d9b32d",
        },
        {
            "n": "4",
            "title": "MIXED-SIGNAL",
            "sub": "Digital plus analog integration",
            "body": [
                "Map NCE TFLN_TX lanes to TFLN PIC pins.",
                "Confirm SPI, I2C, JTAG, AST2600, PLL, sensors, and service interfaces.",
                "Output: mixed-signal interface matrix.",
            ],
            "color": "#ffd5e8",
            "accent": "#cc6090",
        },
        {
            "n": "5",
            "title": "BOM ENGINEERING",
            "sub": "Procurement domain",
            "body": [
                "Resolve 82 missing MPN/field issues.",
                "Confirm value, package, quantity, AVL, DNP, and source status for each populated item.",
                "Output: signed final BOM after ECO closure.",
            ],
            "color": "#d7ecfa",
            "accent": "#5499bf",
        },
        {
            "n": "6",
            "title": "BACK-END PCB ECO",
            "sub": "Physical design",
            "body": [
                "Fix 32 DRC violations: edge copper, ULREG/URREG, CL32/CR32/DL32/DR32/JL32/JR32, MH5, UPWR_L/UPWR_R.",
                "Preserve 295.0 x 140.0 mm envelope.",
                "Output: updated KiCad PCB.",
            ],
            "color": "#e6dbf7",
            "accent": "#8569b6",
        },
        {
            "n": "7",
            "title": "PHYSICAL VERIFY",
            "sub": "DRC / parity / ERC closure",
            "body": [
                "Target KiCad DRC = 0 and unconnected = 0.",
                "Close or sign-waive all schematic parity items.",
                "Output: validation report and disposition log.",
            ],
            "color": "#dff3d8",
            "accent": "#6da562",
        },
        {
            "n": "8",
            "title": "DFM / DFA REVIEW",
            "sub": "Manufacturer review",
            "body": [
                "Review Gerbers, drill, mask, silkscreen, fab notes, assembly, panelization, stackup, and impedance.",
                "Output: DFM/DFA closure report.",
            ],
            "color": "#ffd6d3",
            "accent": "#c76b5f",
        },
        {
            "n": "9",
            "title": "RELEASE PACKAGE",
            "sub": "CAD / EDA outputs",
            "body": [
                "Regenerate Gerbers, drills, netlists, schematic PDF/SVG, BOM, placement, assembly/fab drawings, and manifest.",
                "Output: release candidate package.",
            ],
            "color": "#ffe0b8",
            "accent": "#d88b3a",
        },
        {
            "n": "10",
            "title": "FAB READINESS",
            "sub": "Production release gate",
            "body": [
                "Release after signed ECO, DRC/parity closure, final BOM signoff, and manufacturer DFM closure.",
                "Output: production release approval.",
            ],
            "color": "#cef3ed",
            "accent": "#4ca698",
        },
    ]

    margin_x = 80
    gap_x = 30
    card_w = (W - 2 * margin_x - 4 * gap_x) // 5
    card_h = 470
    row_y = [330, 850]
    positions: list[tuple[int, int, int, int]] = []

    for i, card in enumerate(cards):
        row = 0 if i < 5 else 1
        col = i % 5
        x = margin_x + col * (card_w + gap_x)
        y = row_y[row]
        positions.append((x, y, x + card_w, y + card_h))
        draw.rounded_rectangle((x + 10, y + 12, x + card_w + 10, y + card_h + 12), radius=18, fill="#dfe5ec")
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=18, fill=card["color"], outline=card["accent"], width=4)
        draw.rounded_rectangle((x, y, x + card_w, y + 112), radius=18, fill=card["color"], outline=card["accent"], width=0)
        draw.line((x, y + 112, x + card_w, y + 112), fill=card["accent"], width=3)
        number = f"{card['n']}."
        nb = draw.textbbox((0, 0), number, font=card_title_font)
        draw.text((x + 24, y + 28), number, fill=ink, font=card_title_font)
        title_lines = wrap_to_width(draw, card["title"], card_title_font, card_w - 125)
        ty = y + 22
        for line in title_lines[:2]:
            draw.text((x + 82, ty), line, fill=ink, font=card_title_font)
            ty += 34
        draw.text((x + 82, y + 78), card["sub"], fill=mid, font=card_subtitle_font)
        body_y = y + 135
        max_body_width = card_w - 54
        for bullet in card["body"]:
            wrapped = wrap_to_width(draw, bullet, body_font, max_body_width - 30)
            draw.text((x + 24, body_y), "-", fill=ink, font=body_font)
            for j, line in enumerate(wrapped):
                draw.text((x + 50, body_y + j * 28), line, fill=ink, font=body_font)
            body_y += max(34, len(wrapped) * 28 + 14)

    # Top connector.
    draw.line((1300, 285, 1300, 315), fill=ink, width=5)
    draw.line((300, 315, 2300, 315), fill=ink, width=5)
    for x, y1, _, _ in positions[:5]:
        cx = x + card_w // 2
        arrow(draw, (cx, 315), (cx, row_y[0] - 18), ink, 4)
    for x, y1, _, _ in positions[5:]:
        cx = x + card_w // 2
        arrow(draw, (cx, row_y[0] + card_h + 28), (cx, row_y[1] - 18), ink, 4)

    # Bottom flow.
    bottom_y = 1430
    flow_steps = [
        ("REQUIREMENT RESET", "#e2e6e9"),
        ("SCHEMATIC CLOSURE", "#d7f0d3"),
        ("PCB ECO", "#ffe3bf"),
        ("VERIFY / DFM", "#d7ecfa"),
        ("RELEASE GATE", "#cef3ed"),
    ]
    step_w = 410
    step_h = 92
    step_gap = 38
    start_x = (W - (len(flow_steps) * step_w + (len(flow_steps) - 1) * step_gap)) // 2
    for idx, (label, color) in enumerate(flow_steps):
        x = start_x + idx * (step_w + step_gap)
        draw.rounded_rectangle((x, bottom_y, x + step_w, bottom_y + step_h), radius=14, fill=color, outline="#99a4ad", width=3)
        lines = wrap_to_width(draw, label, flow_font, step_w - 40)
        total_h = len(lines) * 28
        yy = bottom_y + (step_h - total_h) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=flow_font)
            draw.text((x + (step_w - (bbox[2] - bbox[0])) // 2, yy), line, fill=ink, font=flow_font)
            yy += 28
        if idx < len(flow_steps) - 1:
            arrow(draw, (x + step_w + 8, bottom_y + step_h // 2), (x + step_w + step_gap - 8, bottom_y + step_h // 2), ink, 4)

    note = "Current state: release pending. Open items: 32 DRC violations, 564 schematic parity items, final BOM signoff after ECO closure."
    wrapped_note = wrap_to_width(draw, note, small_font, 2100)
    ny = 1580
    for line in wrapped_note:
        bbox = draw.textbbox((0, 0), line, font=small_font)
        draw.text(((W - (bbox[2] - bbox[0])) // 2, ny), line, fill=mid, font=small_font)
        ny += 26

    img.save(path_png, quality=95)

    # One-page PDF with the PNG embedded.
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    page_w, page_h = 17 * inch, 11 * inch
    c = canvas.Canvas(str(path_pdf), pagesize=(page_w, page_h))
    margin = 0.35 * inch
    c.drawImage(
        ImageReader(str(path_png)),
        margin,
        margin,
        width=page_w - 2 * margin,
        height=page_h - 2 * margin,
        preserveAspectRatio=True,
        anchor="c",
    )
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#66727f"))
    c.drawRightString(page_w - margin, 0.17 * inch, f"Generated {date.today().isoformat()} - {PACKAGE_NAME}")
    c.save()


def styles():
    s = getSampleStyleSheet()
    s.add(
        ParagraphStyle(
            name="DocTitle",
            parent=s["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )
    s.add(
        ParagraphStyle(
            name="Section",
            parent=s["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#154766"),
            spaceBefore=10,
            spaceAfter=5,
        )
    )
    s.add(
        ParagraphStyle(
            name="BodySmall",
            parent=s["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
        )
    )
    s["BodyText"].fontName = "Helvetica"
    s["BodyText"].fontSize = 9
    s["BodyText"].leading = 12
    return s


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    clean = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(clean, style)


def bullet_list(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(paragraph(item, style), bulletColor=colors.HexColor("#154766")) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=14,
        bulletFontSize=5,
    )


def pdf_table(rows: list[list[str]], widths: list[float] | None = None) -> Table:
    st = styles()
    data = [[paragraph(cell, st["BodySmall"]) for cell in row] for row in rows]
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#154766")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#a8b2bc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7f9fb")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f7f9fb"), colors.white]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def make_doc_pdf(path: Path, title: str, parts: list[dict]) -> None:
    st = styles()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )
    story = [paragraph(title, st["DocTitle"])]
    for part in parts:
        if part.get("page_break"):
            story.append(PageBreak())
        if "heading" in part:
            story.append(paragraph(part["heading"], st["Section"]))
        if "para" in part:
            for p in part["para"]:
                story.append(paragraph(p, st["BodyText"]))
                story.append(Spacer(1, 3))
        if "bullets" in part:
            story.append(bullet_list(part["bullets"], st["BodyText"]))
            story.append(Spacer(1, 5))
        if "table" in part:
            story.append(pdf_table(part["table"], part.get("widths")))
            story.append(Spacer(1, 7))
        if "image" in part:
            story.append(RLImage(str(part["image"]), width=7.4 * inch, height=5.1 * inch))
            story.append(Spacer(1, 6))
    doc.build(story)


domain_rows = [
    {
        "Step": "1",
        "Domain": "Specification Reset",
        "Purpose": "Freeze the real server chassis requirements before layout ECO.",
        "Current Gap": "Envelope is modeled at 295.0 x 140.0 mm, but chassis rail, connector, airflow, heatsink, and mounting constraints need signed confirmation.",
        "Engineer Output": "Signed mechanical requirement, board outline datum, hole map, keepouts, height envelope, and connector opening definition.",
    },
    {
        "Step": "2",
        "Domain": "Front-End Design",
        "Purpose": "Close schematic and logical design intent.",
        "Current Gap": "199 net conflicts and 199 extra footprints remain between schematic and PCB.",
        "Engineer Output": "Clean schematic revision, clean netlist, and disposition of every extra PCB footprint.",
    },
    {
        "Step": "3",
        "Domain": "Analog / TFLN Design",
        "Purpose": "Validate optical/RF/bias chain around the TFLN photonic IC.",
        "Current Gap": "TFLN PIC U3 and RF driver/bias chain need explicit pin-map and constraint review.",
        "Engineer Output": "TFLN pin map, MZM lane mapping, RF/bias constraints, power-noise requirements.",
    },
    {
        "Step": "4",
        "Domain": "Mixed-Signal Integration",
        "Purpose": "Verify digital control plus analog/optical interfaces.",
        "Current Gap": "NCE-to-TFLN lane mapping and service/control interfaces need an interface matrix.",
        "Engineer Output": "Mixed-signal interface matrix covering TFLN_TX lanes, SPI/I2C/JTAG, PLL, AST2600, and sensors.",
    },
    {
        "Step": "5",
        "Domain": "BOM Engineering",
        "Purpose": "Make the procurement BOM match the closed design.",
        "Current Gap": "82 field mismatches/missing MPN items and release-pending BOM state.",
        "Engineer Output": "Signed final BOM with MPN, value, package, quantity, AVL/source, DNP, and revision.",
    },
    {
        "Step": "6",
        "Domain": "Back-End PCB ECO",
        "Purpose": "Repair the physical design without changing the agreed envelope.",
        "Current Gap": "32 KiCad DRC violations in edge copper, top-row placeholders, mounting hole, and silkscreen.",
        "Engineer Output": "Updated PCB with clean edge clearances, fixed placeholders, moved MH5 or signed waiver, and cleaned silkscreen.",
    },
    {
        "Step": "7",
        "Domain": "Physical Verification",
        "Purpose": "Prove the schematic and PCB are release-clean.",
        "Current Gap": "DRC fails, schematic parity fails, unconnected count is already 0.",
        "Engineer Output": "KiCad DRC 0, unconnected 0, schematic parity closed or signed-waived, ERC/parity log.",
    },
    {
        "Step": "8",
        "Domain": "DFM / DFA Review",
        "Purpose": "Manufacturer checks the buildability and assembly path.",
        "Current Gap": "DFM/DFA can start for review, but closure depends on ECO-clean outputs.",
        "Engineer Output": "DFM/DFA report covering Gerbers, drill, stackup, solder mask, silkscreen, panelization, assembly, and test coupons.",
    },
    {
        "Step": "9",
        "Domain": "Release Package Generation",
        "Purpose": "Regenerate all outputs from the closed design.",
        "Current Gap": "Current outputs are review/reference outputs and must be regenerated after ECO closure.",
        "Engineer Output": "Gerbers, drills, IPC/ODB++ if required, schematic PDF/SVG, netlists, BOM, placement, fab/assembly drawings, checksum manifest.",
    },
    {
        "Step": "10",
        "Domain": "Fabrication Readiness",
        "Purpose": "Gate the package into production release.",
        "Current Gap": "Production release is pending DRC closure, schematic parity closure, final BOM, and manufacturer DFM closure.",
        "Engineer Output": "Signed production release approval with revision/date and final package checksum.",
    },
]

gap_rows = [
    {
        "Open Item": "KiCad DRC fails with 32 violations",
        "Flow Step": "6 / 7",
        "What Engineers Fix": "Move/trim no-net copper at edges, relocate ULREG/URREG, move CL32/CR32/DL32/DR32/JL32/JR32 inward, resolve MH5 edge clearance, and clean UPWR_L/UPWR_R silkscreen.",
        "Acceptance Criteria": "KiCad DRC returns 0 violations using the agreed board rules.",
    },
    {
        "Open Item": "Schematic parity fails with 564 items",
        "Flow Step": "2 / 7",
        "What Engineers Fix": "Reconcile PCB-to-schematic updates, classify extra footprints, resolve net conflicts, and fix footprint-symbol mismatches.",
        "Acceptance Criteria": "Parity is closed, or remaining items have signed engineering waivers.",
    },
    {
        "Open Item": "82 missing/mismatched MPN or field items",
        "Flow Step": "5",
        "What Engineers Fix": "Update schematic and footprint fields, then regenerate grouped and expanded BOM from the closed design.",
        "Acceptance Criteria": "Signed final BOM with MPN, value, package, quantity, DNP, AVL/source, revision, and date.",
    },
    {
        "Open Item": "Dual NCE and TFLN visibility question",
        "Flow Step": "2 / 3 / 4",
        "What Engineers Fix": "Use the included schematic overview and native schematic. Confirm U1 NCE-A, U4 NCE-B, U3 TFLN PIC, U50-U53 RF driver chain, and HBM groups.",
        "Acceptance Criteria": "Manufacturer can trace NCE/TFLN blocks in PDF/SVG/native KiCad schematic and netlist.",
    },
    {
        "Open Item": "Real server chassis constraints",
        "Flow Step": "1 / 6 / 8",
        "What Engineers Fix": "Confirm rail, connector, front-panel, airflow, heatsink, mounting-hole, keepout, and service-clearance requirements.",
        "Acceptance Criteria": "Signed mechanical review confirms 295.0 x 140.0 mm reference envelope and 56.0 mm height note are compatible with the chassis.",
    },
]

release_rows = [
    {
        "Required Output": "Signed mechanical specification",
        "Owner": "Mechanical / system engineering",
        "Release Criteria": "295.0 x 140.0 mm envelope, 56.0 mm height note, datum, rails, keepouts, holes, connector exits, heatsink and airflow confirmed.",
        "Current State": "Reference envelope modeled; signoff pending.",
    },
    {
        "Required Output": "Native schematic and schematic PDF/SVG",
        "Owner": "Electrical engineering",
        "Release Criteria": "Dual NCE, TFLN PIC, RF/bias, HBM, PCIe/control/power blocks visible and aligned to netlist.",
        "Current State": "Included in schematic reference; parity closure pending.",
    },
    {
        "Required Output": "Final netlists",
        "Owner": "Electrical engineering",
        "Release Criteria": "Generated from closed schematic and loaded into PCB with no unexplained differences.",
        "Current State": "Reference netlists included; final netlist after ECO closure.",
    },
    {
        "Required Output": "PCB native project",
        "Owner": "PCB layout engineering",
        "Release Criteria": "Updated KiCad project with DRC 0 and no unintended unconnected items.",
        "Current State": "Current project included in ECO package; DRC/parity still open.",
    },
    {
        "Required Output": "Gerbers, drill, drill map, stackup, impedance notes",
        "Owner": "PCB layout / manufacturer CAM",
        "Release Criteria": "Regenerated from DRC-clean PCB and approved by DFM.",
        "Current State": "Review outputs exist; regenerate after ECO closure.",
    },
    {
        "Required Output": "Placement and assembly outputs",
        "Owner": "PCB layout / assembly engineering",
        "Release Criteria": "XY placement, centroid, assembly drawings, polarity and DNP markings match final BOM.",
        "Current State": "Release-pending pending BOM and parity closure.",
    },
    {
        "Required Output": "Final procurement BOM",
        "Owner": "Component / procurement engineering",
        "Release Criteria": "MPN, value, package, quantity, source/AVL, DNP, alternates, revision/date signed.",
        "Current State": "Current BOM is release-pending; final BOM must follow ECO closure.",
    },
    {
        "Required Output": "Validation report",
        "Owner": "Electrical / PCB verification",
        "Release Criteria": "DRC 0, unconnected 0, schematic parity closed or signed-waived, ERC reviewed.",
        "Current State": "DRC 32, unconnected 0, schematic parity 564.",
    },
    {
        "Required Output": "DFM/DFA closure report",
        "Owner": "Manufacturer with engineering review",
        "Release Criteria": "CAM, panelization, solder mask, silkscreen, drill, stackup, assembly and test risks closed.",
        "Current State": "Pending ECO-clean outputs.",
    },
    {
        "Required Output": "Final release manifest",
        "Owner": "Release engineering",
        "Release Criteria": "All final files listed with SHA256, revision, date, and owner approval.",
        "Current State": "This do-over package includes its own manifest; production manifest comes after closure.",
    },
]

schematic_index_rows = [
    {
        "Reference": "U1",
        "Block": "NCE-A die",
        "Value": "NCE_Gen3_SpikingBrain",
        "MPN": "LR-NCE-G3-BGA2500-001",
        "Where To Look": "Clear overview PDF and native KiCad schematic.",
    },
    {
        "Reference": "U4",
        "Block": "NCE-B die",
        "Value": "NCE_Gen3_SpikingBrain",
        "MPN": "LR-NCE-G3-BGA2500-001",
        "Where To Look": "Clear overview PDF and native KiCad schematic.",
    },
    {
        "Reference": "U3",
        "Block": "TFLN photonic IC",
        "Value": "TFLN_PIC_4xMZM",
        "MPN": "TFLN-MZM-400G-C",
        "Where To Look": "Clear overview PDF, native schematic, SVG, and schematic BOM.",
    },
    {
        "Reference": "U50-U53",
        "Block": "RF driver chain",
        "Value": "HMC8410",
        "MPN": "HMC8410LP2FE",
        "Where To Look": "Native schematic and schematic BOM.",
    },
    {
        "Reference": "U30-U35",
        "Block": "HBM group for NCE-A",
        "Value": "HBM4-16GB",
        "MPN": "SK_HBM4_16GB_12H",
        "Where To Look": "Native schematic and schematic BOM.",
    },
    {
        "Reference": "U40-U45",
        "Block": "HBM group for NCE-B",
        "Value": "HBM4-16GB",
        "MPN": "SK_HBM4_16GB_12H",
        "Where To Look": "Native schematic and schematic BOM.",
    },
]


def md_table(rows: list[dict[str, str]]) -> str:
    headers = list(rows[0].keys())
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(row[h].replace("\n", " ") for h in headers) + " |")
    return "\n".join(out)


def build_docs(flow_png: Path) -> None:
    today = date.today().isoformat()
    readme = f"""
# {PACKAGE_NAME}

Date: {today}

## Purpose

This package maps the manufacturer-provided VLSI design-flow template into a board-specific do-over flow for TFLN_AI_NODE_X2.

It is intended to guide the engineering ECO path from requirement reset through schematic/BOM closure, PCB ECO, verification, DFM/DFA, and production release approval.

## Current engineering state

- Board reference envelope: 295.0 mm x 140.0 mm.
- Height note: 56.0 mm.
- KiCad DRC: 32 open violations.
- Unconnected items: 0.
- Schematic parity: 564 open PCB-vs-schematic items.
- BOM: final procurement BOM is pending ECO/parity closure and signed component-engineering review.

## What changed in this do-over package

- The manufacturer template was converted into a TFLN_AI_NODE_X2-specific flow.
- The engineer fix list is mapped to the flow domains.
- The schematic reference is included so the manufacturer can see U1/U4 dual NCE dies and U3 TFLN PIC.
- The release-output checklist defines what must be regenerated after ECO closure.

## Included files

- `02_do_over_flow_chart/TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.pdf`
- `02_do_over_flow_chart/TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.png`
- `03_engineering_instructions/TFLN_AI_NODE_X2_DO_OVER_DOMAIN_MATRIX.pdf`
- `03_engineering_instructions/CURRENT_GAPS_TO_FLOW_MAP.pdf`
- `04_release_outputs_required/RELEASE_OUTPUTS_REQUIRED.pdf`
- `05_schematic_reference/SCHEMATIC_VISIBILITY_INDEX.pdf`
- `00_read_me/MANUFACTURER_RESPONSE_DO_OVER.txt`

## Release position

Use this as the ECO and release-closure instruction set. The production package should be issued after DRC closure, schematic parity closure, final BOM signoff, and manufacturer DFM/DFA closure.
"""
    write_text(PKG / "00_read_me" / "README_FIRST_DO_OVER_FLOW.md", readme)

    response = """
Please use the attached Tapeout July_04 do-over flow package as the ECO closure guide.

We converted your VLSI design-flow template into a board-specific release flow for TFLN_AI_NODE_X2. The package shows the required path:

1. Specification reset and real server chassis mechanical signoff.
2. Front-end schematic closure.
3. Analog/TFLN optical and RF/bias review.
4. Mixed-signal NCE-to-TFLN and service-interface review.
5. BOM engineering and final procurement BOM signoff.
6. Back-end PCB ECO.
7. Physical verification closure.
8. DFM/DFA review.
9. Regeneration of all release outputs.
10. Production release approval.

The schematic reference is included. For the dual NCE and TFLN visibility question, open:
`05_schematic_reference/TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf`

That overview identifies:
- U1 = NCE-A die
- U4 = NCE-B die
- U3 = TFLN_PIC_4xMZM photonic IC
- U50-U53 = RF driver chain
- U30-U35 and U40-U45 = HBM groups for the two NCE dies

Current open engineering items are:
- KiCad DRC: 32 open violations
- Unconnected items: 0
- Schematic parity: 564 open items
- BOM: final procurement BOM to be signed after ECO/parity closure

Please use `03_engineering_instructions/CURRENT_GAPS_TO_FLOW_MAP.csv` and `04_release_outputs_required/RELEASE_OUTPUTS_REQUIRED.csv` as the action checklist.
"""
    write_text(PKG / "00_read_me" / "MANUFACTURER_RESPONSE_DO_OVER.txt", response)

    domain_md = "# TFLN_AI_NODE_X2 Do-Over Domain Matrix\n\n" + md_table(domain_rows)
    write_text(PKG / "03_engineering_instructions" / "TFLN_AI_NODE_X2_DO_OVER_DOMAIN_MATRIX.md", domain_md)
    write_csv(PKG / "03_engineering_instructions" / "TFLN_AI_NODE_X2_DO_OVER_DOMAIN_MATRIX.csv", domain_rows)

    gaps_md = "# Current Gaps To Do-Over Flow Map\n\n" + md_table(gap_rows)
    write_text(PKG / "03_engineering_instructions" / "CURRENT_GAPS_TO_FLOW_MAP.md", gaps_md)
    write_csv(PKG / "03_engineering_instructions" / "CURRENT_GAPS_TO_FLOW_MAP.csv", gap_rows)

    release_md = "# Release Outputs Required\n\n" + md_table(release_rows)
    write_text(PKG / "04_release_outputs_required" / "RELEASE_OUTPUTS_REQUIRED.md", release_md)
    write_csv(PKG / "04_release_outputs_required" / "RELEASE_OUTPUTS_REQUIRED.csv", release_rows)

    schematic_md = "# Schematic Visibility Index\n\n" + md_table(schematic_index_rows)
    write_text(PKG / "05_schematic_reference" / "SCHEMATIC_VISIBILITY_INDEX.md", schematic_md)
    write_csv(PKG / "05_schematic_reference" / "SCHEMATIC_VISIBILITY_INDEX.csv", schematic_index_rows)

    make_doc_pdf(
        PKG / "00_read_me" / "README_FIRST_DO_OVER_FLOW.pdf",
        "README FIRST - Tapeout July_04 Do-Over Flow",
        [
            {"heading": "Purpose", "para": ["This package maps the manufacturer-provided VLSI design-flow template into a board-specific do-over flow for TFLN_AI_NODE_X2."]},
            {
                "heading": "Current engineering state",
                "bullets": [
                    "Board reference envelope: 295.0 mm x 140.0 mm.",
                    "Height note: 56.0 mm.",
                    "KiCad DRC: 32 open violations.",
                    "Unconnected items: 0.",
                    "Schematic parity: 564 open PCB-vs-schematic items.",
                    "BOM: final procurement BOM is pending ECO/parity closure and signed component-engineering review.",
                ],
            },
            {"heading": "Do-over flow chart", "image": flow_png},
            {
                "heading": "Release position",
                "para": [
                    "Use this package as the ECO and release-closure instruction set. The production package should be issued after DRC closure, schematic parity closure, final BOM signoff, and manufacturer DFM/DFA closure."
                ],
            },
        ],
    )

    make_doc_pdf(
        PKG / "03_engineering_instructions" / "TFLN_AI_NODE_X2_DO_OVER_DOMAIN_MATRIX.pdf",
        "TFLN_AI_NODE_X2 Do-Over Domain Matrix",
        [
            {
                "heading": "Domain matrix",
                "table": [["Step", "Domain", "Purpose", "Current Gap", "Engineer Output"]]
                + [[r["Step"], r["Domain"], r["Purpose"], r["Current Gap"], r["Engineer Output"]] for r in domain_rows],
                "widths": [0.35 * inch, 1.05 * inch, 1.25 * inch, 2.05 * inch, 2.1 * inch],
            }
        ],
    )

    make_doc_pdf(
        PKG / "03_engineering_instructions" / "CURRENT_GAPS_TO_FLOW_MAP.pdf",
        "Current Gaps To Do-Over Flow Map",
        [
            {
                "heading": "Action map",
                "table": [["Open Item", "Flow Step", "What Engineers Fix", "Acceptance Criteria"]]
                + [[r["Open Item"], r["Flow Step"], r["What Engineers Fix"], r["Acceptance Criteria"]] for r in gap_rows],
                "widths": [1.55 * inch, 0.7 * inch, 2.35 * inch, 2.2 * inch],
            }
        ],
    )

    make_doc_pdf(
        PKG / "04_release_outputs_required" / "RELEASE_OUTPUTS_REQUIRED.pdf",
        "Release Outputs Required",
        [
            {
                "heading": "Required final outputs",
                "table": [["Required Output", "Owner", "Release Criteria", "Current State"]]
                + [[r["Required Output"], r["Owner"], r["Release Criteria"], r["Current State"]] for r in release_rows],
                "widths": [1.4 * inch, 1.0 * inch, 2.6 * inch, 1.8 * inch],
            }
        ],
    )

    make_doc_pdf(
        PKG / "05_schematic_reference" / "SCHEMATIC_VISIBILITY_INDEX.pdf",
        "Schematic Visibility Index",
        [
            {
                "heading": "Key devices visible in schematic reference",
                "table": [["Reference", "Block", "Value", "MPN", "Where To Look"]]
                + [[r["Reference"], r["Block"], r["Value"], r["MPN"], r["Where To Look"]] for r in schematic_index_rows],
                "widths": [0.8 * inch, 1.35 * inch, 1.55 * inch, 1.35 * inch, 1.75 * inch],
            }
        ],
    )

    make_doc_pdf(
        PKG / "00_read_me" / "MANUFACTURER_RESPONSE_DO_OVER.pdf",
        "Manufacturer Response - Do-Over Flow",
        [
            {
                "heading": "Response",
                "para": [
                    "Please use the attached Tapeout July_04 do-over flow package as the ECO closure guide. The VLSI template has been converted into a board-specific flow covering specification reset, front-end schematic closure, analog/TFLN review, mixed-signal integration, BOM engineering, back-end PCB ECO, physical verification, DFM/DFA, release-output regeneration, and production release approval."
                ],
            },
            {
                "heading": "Schematic visibility",
                "bullets": [
                    "Open 05_schematic_reference/TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf.",
                    "U1 = NCE-A die.",
                    "U4 = NCE-B die.",
                    "U3 = TFLN_PIC_4xMZM photonic IC.",
                    "U50-U53 = RF driver chain.",
                    "U30-U35 and U40-U45 = HBM groups for the two NCE dies.",
                ],
            },
            {
                "heading": "Current open engineering items",
                "bullets": [
                    "KiCad DRC: 32 open violations.",
                    "Unconnected items: 0.",
                    "Schematic parity: 564 open items.",
                    "Final procurement BOM to be signed after ECO/parity closure.",
                ],
            },
        ],
    )


def copy_reference_files() -> None:
    if TEMPLATE_IMAGE.exists():
        shutil.copy2(TEMPLATE_IMAGE, PKG / "01_reference_template" / "manufacturer_vlsi_flow_template.png")

    copy_map = [
        (
            SCHEMATIC_PKG / "01_pdf_and_svg" / "TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf",
            PKG / "05_schematic_reference" / "TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf",
        ),
        (
            SCHEMATIC_PKG / "01_pdf_and_svg" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic.pdf",
            PKG / "05_schematic_reference" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic.pdf",
        ),
        (
            SCHEMATIC_PKG / "01_pdf_and_svg" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.svg",
            PKG / "05_schematic_reference" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.svg",
        ),
        (
            SCHEMATIC_PKG / "00_native_kicad_schematic" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_sch",
            PKG / "05_schematic_reference" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_sch",
        ),
        (
            SCHEMATIC_PKG / "02_netlists" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_netlist_kicadxml.xml",
            PKG / "05_schematic_reference" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_netlist_kicadxml.xml",
        ),
        (
            SCHEMATIC_PKG / "03_bom_reference" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic_bom.csv",
            PKG / "05_schematic_reference" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic_bom.csv",
        ),
    ]
    for src, dst in copy_map:
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def write_validation_context() -> None:
    text = """
# Validation Context

The current release-pending ECO state is:

- Reference envelope: 295.0 mm x 140.0 mm.
- Height note: 56.0 mm.
- KiCad CLI used previously: 10.0.3.
- KiCad DRC: 32 open violations.
- Unconnected items: 0.
- Schematic parity: 564 open PCB-vs-schematic items.

Open DRC groups:

- 7 no-net copper graphics near board edges on EO_Bias_Monitor / Slow_Control.
- 10 top-edge regulator placeholder pad clearances on ULREG / URREG.
- 10 top-row bias/monitor component clearances on CL32 / CR32 / DL32 / DR32 / JL32 / JR32.
- 1 mounting-hole clearance item at MH5.
- 4 silkscreen clipping items at UPWR_L / UPWR_R.

Schematic parity groups:

- 199 net conflicts.
- 199 extra footprints.
- 84 footprint-symbol mismatches.
- 82 footprint/symbol field mismatches, including missing MPN fields.
"""
    write_text(PKG / "06_validation_context" / "VALIDATION_CONTEXT.md", text)
    make_doc_pdf(
        PKG / "06_validation_context" / "VALIDATION_CONTEXT.pdf",
        "Validation Context",
        [
            {
                "heading": "Current state",
                "bullets": [
                    "Reference envelope: 295.0 mm x 140.0 mm.",
                    "Height note: 56.0 mm.",
                    "KiCad DRC: 32 open violations.",
                    "Unconnected items: 0.",
                    "Schematic parity: 564 open PCB-vs-schematic items.",
                ],
            },
            {
                "heading": "Open DRC groups",
                "bullets": [
                    "7 no-net copper graphics near board edges on EO_Bias_Monitor / Slow_Control.",
                    "10 top-edge regulator placeholder pad clearances on ULREG / URREG.",
                    "10 top-row bias/monitor component clearances on CL32 / CR32 / DL32 / DR32 / JL32 / JR32.",
                    "1 mounting-hole clearance item at MH5.",
                    "4 silkscreen clipping items at UPWR_L / UPWR_R.",
                ],
            },
            {
                "heading": "Schematic parity groups",
                "bullets": [
                    "199 net conflicts.",
                    "199 extra footprints.",
                    "84 footprint-symbol mismatches.",
                    "82 footprint/symbol field mismatches, including missing MPN fields.",
                ],
            },
        ],
    )


def build_manifest() -> None:
    rows = []
    for path in sorted(PKG.rglob("*")):
        if path.is_file() and path.name not in {"FULL_PACKAGE_MANIFEST.csv", "FULL_PACKAGE_MANIFEST.md"}:
            rows.append(
                {
                    "Path": str(path.relative_to(PKG)).replace("/", "\\"),
                    "Bytes": str(path.stat().st_size),
                    "SHA256": sha256(path),
                }
            )
    write_csv(PKG / "FULL_PACKAGE_MANIFEST.csv", rows)
    md = "# Full Package Manifest\n\n" + md_table(rows)
    write_text(PKG / "FULL_PACKAGE_MANIFEST.md", md)


def make_zip() -> None:
    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    if DL_ZIP.exists():
        DL_ZIP.unlink()
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(PKG.rglob("*")):
            if path.is_file():
                z.write(path, arcname=str(Path(PACKAGE_NAME) / path.relative_to(PKG)))
    shutil.copy2(OUT_ZIP, DL_ZIP)


def copy_key_outputs(flow_png: Path, flow_pdf: Path) -> None:
    copies = [
        (flow_png, OUTPUTS / flow_png.name),
        (flow_pdf, OUTPUTS / flow_pdf.name),
        (PKG / "00_read_me" / "MANUFACTURER_RESPONSE_DO_OVER.txt", OUTPUTS / "MANUFACTURER_RESPONSE_DO_OVER.txt"),
        (PKG / "00_read_me" / "MANUFACTURER_RESPONSE_DO_OVER.pdf", OUTPUTS / "MANUFACTURER_RESPONSE_DO_OVER.pdf"),
        (PKG / "03_engineering_instructions" / "CURRENT_GAPS_TO_FLOW_MAP.pdf", OUTPUTS / "CURRENT_GAPS_TO_FLOW_MAP.pdf"),
        (PKG / "04_release_outputs_required" / "RELEASE_OUTPUTS_REQUIRED.pdf", OUTPUTS / "RELEASE_OUTPUTS_REQUIRED.pdf"),
    ]
    for src, dst in copies:
        if src.exists():
            shutil.copy2(src, dst)
            shutil.copy2(src, DOWNLOADS / dst.name)


def verify_text_clean() -> None:
    forbidden = ["M" + "SI", "Do NOT FABRICATE", "DO NOT FABRICATE", "FABRICATION HOLD"]
    hits: list[str] = []
    for path in PKG.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for phrase in forbidden:
            if phrase in text:
                hits.append(f"{path.relative_to(PKG)}: {phrase}")
    if hits:
        raise RuntimeError("Forbidden text found:\n" + "\n".join(hits))


def main() -> None:
    mkdirs()
    flow_png = PKG / "02_do_over_flow_chart" / "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.png"
    flow_pdf = PKG / "02_do_over_flow_chart" / "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.pdf"
    draw_flow_chart(flow_png, flow_pdf)
    copy_reference_files()
    build_docs(flow_png)
    write_validation_context()
    verify_text_clean()
    build_manifest()
    make_zip()
    copy_key_outputs(flow_png, flow_pdf)
    print(f"Package: {PKG}")
    print(f"Output ZIP: {OUT_ZIP}")
    print(f"Downloads ZIP: {DL_ZIP}")
    print(f"ZIP SHA256: {sha256(OUT_ZIP)}")
    print(f"Flow PDF: {OUTPUTS / flow_pdf.name}")


if __name__ == "__main__":
    main()
