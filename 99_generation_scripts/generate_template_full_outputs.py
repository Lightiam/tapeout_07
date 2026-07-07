from __future__ import annotations

import csv
import hashlib
import shutil
import zipfile
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
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

PACKAGE_NAME = "Tapeout July_04_TEMPLATE_FULL_OUTPUTS_RELEASE_PENDING"
PKG = WORK / PACKAGE_NAME
OUT_ZIP = OUTPUTS / f"{PACKAGE_NAME}.zip"
DL_ZIP = DOWNLOADS / f"{PACKAGE_NAME}.zip"

ECO = WORK / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED"
SCH = WORK / "Tapeout July_04_SCHEMATIC_TRANSMITTAL_RELEASE_PENDING"
FLOW = WORK / "Tapeout July_04_DO_OVER_VLSI_FLOW"
OLD_NATIVE = OUTPUTS / "05_kicad10_native_exports_DRC_FAIL_NOT_FOR_FAB"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def md_table(rows: list[dict[str, str]]) -> str:
    headers = list(rows[0].keys())
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row[h]).replace("\n", " ") for h in headers) + " |")
    return "\n".join(out)


def styles():
    s = getSampleStyleSheet()
    s.add(
        ParagraphStyle(
            name="DocTitle",
            parent=s["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#154766"),
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
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    s.add(
        ParagraphStyle(
            name="BodySmall",
            parent=s["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=8.8,
            alignment=TA_LEFT,
        )
    )
    s["BodyText"].fontName = "Helvetica"
    s["BodyText"].fontSize = 9
    s["BodyText"].leading = 12
    return s


def p(text: str, style: ParagraphStyle) -> Paragraph:
    clean = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(clean, style)


def bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, style), bulletColor=colors.HexColor("#154766")) for item in items],
        bulletType="bullet",
        leftIndent=14,
        bulletFontSize=5,
    )


def table(rows: list[list[str]], widths: list[float] | None = None) -> Table:
    st = styles()
    data = [[p(cell, st["BodySmall"]) for cell in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#154766")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#a8b2bc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fb")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def make_pdf(path: Path, title: str, parts: list[dict], landscape_mode: bool = False) -> None:
    page_size = landscape(A4) if landscape_mode else A4
    doc = SimpleDocTemplate(
        str(path),
        pagesize=page_size,
        rightMargin=0.42 * inch,
        leftMargin=0.42 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.42 * inch,
    )
    st = styles()
    story = [p(title, st["DocTitle"])]
    for part in parts:
        if part.get("page_break"):
            story.append(PageBreak())
        if "heading" in part:
            story.append(p(part["heading"], st["Section"]))
        for para in part.get("para", []):
            story.append(p(para, st["BodyText"]))
            story.append(Spacer(1, 3))
        if "bullets" in part:
            story.append(bullets(part["bullets"], st["BodyText"]))
            story.append(Spacer(1, 6))
        if "table" in part:
            story.append(table(part["table"], part.get("widths")))
            story.append(Spacer(1, 7))
    doc.build(story)


def copy_file(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for path in src.rglob("*"):
        if path.is_file():
            copy_file(path, dst / path.relative_to(src))


vlsi_rows = [
    {
        "Template Stage": "1. Front-End Design",
        "Board-Specific Output": "Schematic closure package",
        "Files": "04_front_end_schematic, 07_netlists, 16_verification",
        "Status": "Release pending: 564 schematic parity items remain open.",
        "Engineer Action": "Reconcile schematic/netlist/PCB and close or sign-waive every parity item.",
    },
    {
        "Template Stage": "2. Back-End Design",
        "Board-Specific Output": "PCB ECO package",
        "Files": "08_board_outline_mechanical, 10_component_placement, 11_routing_planes",
        "Status": "Release pending: 32 DRC violations remain open.",
        "Engineer Action": "Fix edge clearances, placeholders, mounting-hole clearance, and silkscreen issues.",
    },
    {
        "Template Stage": "3. Analog Design",
        "Board-Specific Output": "TFLN optical/RF/bias review",
        "Files": "04_front_end_schematic, 06_footprints_symbols, 12_silkscreen_drc_fab_notes",
        "Status": "Review output issued.",
        "Engineer Action": "Validate U3 TFLN PIC, U50-U53 RF drivers, bias rails, monitor lines, and MZM lanes.",
    },
    {
        "Template Stage": "4. Mixed-Signal Design",
        "Board-Specific Output": "NCE-to-TFLN interface review",
        "Files": "04_front_end_schematic, 07_netlists",
        "Status": "Review output issued.",
        "Engineer Action": "Confirm TFLN_TX lane mapping plus SPI/I2C/JTAG/PLL/AST2600 service interfaces.",
    },
    {
        "Template Stage": "5. Verification Domain",
        "Board-Specific Output": "Validation reports and issue logs",
        "Files": "16_verification",
        "Status": "Release pending: DRC/parity open.",
        "Engineer Action": "Target DRC 0, unconnected 0, parity closed or signed-waived.",
    },
    {
        "Template Stage": "6. Physical Verification",
        "Board-Specific Output": "DRC, board outline, mechanical, fab notes",
        "Files": "08_board_outline_mechanical, 12_silkscreen_drc_fab_notes, 16_verification",
        "Status": "Release pending.",
        "Engineer Action": "Rerun KiCad DRC after ECO and document any mechanical-rule waiver.",
    },
    {
        "Template Stage": "7. FPGA Design",
        "Board-Specific Output": "Not applicable / interface reserve",
        "Files": "02_vlsi_domain_outputs/FPGA_DOMAIN_NOTE",
        "Status": "No FPGA-specific RTL supplied in the current package.",
        "Engineer Action": "If FPGA/programmable logic is added, issue RTL, constraints, bitstream, and verification logs.",
    },
    {
        "Template Stage": "8. Embedded Systems",
        "Board-Specific Output": "AST2600/service-interface checklist",
        "Files": "02_vlsi_domain_outputs/EMBEDDED_SYSTEMS_SERVICE_CHECKLIST",
        "Status": "Checklist output issued.",
        "Engineer Action": "Confirm firmware ownership, boot straps, management bus, sensors, reset and update path.",
    },
    {
        "Template Stage": "9. CAD / EDA Tool Development",
        "Board-Specific Output": "KiCad project, generated reports, manifest",
        "Files": "00_OPEN_IN_KICAD, FULL_PACKAGE_MANIFEST",
        "Status": "Generated in KiCad-compatible handoff format.",
        "Engineer Action": "Use KiCad 10.0.3 or later and preserve generated checksum manifest.",
    },
    {
        "Template Stage": "10. Semiconductor Fabrication",
        "Board-Specific Output": "PCB fab/assembly review package",
        "Files": "13_gerbers_drill, 14_dfa_assembly, 15_dfm_manufacturability, 17_release_gate",
        "Status": "DFM/DFA review package issued; production release follows closure.",
        "Engineer Action": "Complete DFM/DFA and regenerate final production outputs after ECO closure.",
    },
]


pcb_rows = [
    {
        "PCB Step": "1. Schematic Creation / Validation",
        "Generated Output": "Native KiCad schematic, schematic PDF/SVG, dual-NCE/TFLN overview, visibility index.",
        "Package Folder": "04_front_end_schematic",
        "Current Status": "Available. Parity closure still required.",
    },
    {
        "PCB Step": "2. BOM",
        "Generated Output": "Current BOM workbook, grouped/expanded CSV, schematic BOM, BOM action items, final BOM release template.",
        "Package Folder": "05_bom",
        "Current Status": "Release pending until ECO/parity closure and component signoff.",
    },
    {
        "PCB Step": "3. Footprint Creation / Validation",
        "Generated Output": "Footprint-symbol reconciliation matrix and schematic parity issue detail.",
        "Package Folder": "06_footprints_symbols",
        "Current Status": "84 footprint-symbol mismatches and 82 field mismatches remain open.",
    },
    {
        "PCB Step": "4. Netlist",
        "Generated Output": "KiCad XML netlist and S-expression netlist, plus netlist release summary.",
        "Package Folder": "07_netlists",
        "Current Status": "Available. Reissue final after parity closure.",
    },
    {
        "PCB Step": "5. Board Outline / Mechanical Detail",
        "Generated Output": "295.0 x 140.0 mm mechanical envelope, 56.0 mm height note, KiCad PCB, STEP if available.",
        "Package Folder": "08_board_outline_mechanical",
        "Current Status": "Envelope modeled. Real chassis signoff pending.",
    },
    {
        "PCB Step": "6. Stackup / Constraints Setting",
        "Generated Output": "Stackup/constraints requirements and manufacturer confirmation checklist.",
        "Package Folder": "09_stackup_constraints",
        "Current Status": "Review checklist issued. Manufacturer stackup confirmation required.",
    },
    {
        "PCB Step": "7. Component Placement",
        "Generated Output": "Placement ECO instructions and current position CSV if available.",
        "Package Folder": "10_component_placement",
        "Current Status": "Release pending due to edge-clearance and parity fixes.",
    },
    {
        "PCB Step": "8. Routing and Planes",
        "Generated Output": "Routing/planes review instructions and candidate layer preview.",
        "Package Folder": "11_routing_planes",
        "Current Status": "Release pending due to no-net copper edge-clearance DRC items.",
    },
    {
        "PCB Step": "9. Silkscreen / DRC / FAB Notes",
        "Generated Output": "Silkscreen/fab-note review plus DRC fix list.",
        "Package Folder": "12_silkscreen_drc_fab_notes",
        "Current Status": "4 silkscreen clipping items remain open.",
    },
    {
        "PCB Step": "10. Gerber Generation",
        "Generated Output": "Review Gerbers, drill, drill map/report where available, Gerber index.",
        "Package Folder": "13_gerbers_drill",
        "Current Status": "Review outputs included. Regenerate final after DRC/parity closure.",
    },
    {
        "PCB Step": "11. DFA",
        "Generated Output": "Assembly/DFA review checklist and action matrix.",
        "Package Folder": "14_dfa_assembly",
        "Current Status": "Checklist issued. Assembly release depends on final BOM.",
    },
    {
        "PCB Step": "12. DFM",
        "Generated Output": "DFM/manufacturability checklist and action matrix.",
        "Package Folder": "15_dfm_manufacturability",
        "Current Status": "Checklist issued. DFM closure depends on ECO-clean outputs.",
    },
]


issue_rows = [
    {
        "Issue Group": "DRC edge-clearance/open physical items",
        "Count": "32 total DRC violations",
        "Affected Template Output": "Back-End Design / Physical Verification / Gerber Generation",
        "Fix Required": "Move/trim no-net copper, relocate ULREG/URREG, move top-row CL/CR/DL/DR/JL/JR items, resolve MH5, clean UPWR_L/UPWR_R silkscreen.",
        "Acceptance": "KiCad DRC returns 0 violations.",
    },
    {
        "Issue Group": "Schematic parity",
        "Count": "564 total parity items",
        "Affected Template Output": "Front-End Design / Verification Domain",
        "Fix Required": "Reconcile 199 net conflicts, 199 extra footprints, 84 footprint-symbol mismatches, 82 field mismatches.",
        "Acceptance": "Parity closed or every residual item signed-waived.",
    },
    {
        "Issue Group": "BOM finalization",
        "Count": "82 field/MPN mismatches within parity set",
        "Affected Template Output": "BOM / DFA / Production Release",
        "Fix Required": "Update MPN, value, package, quantity, DNP and AVL/source status after ECO closure.",
        "Acceptance": "Signed final procurement BOM with revision/date.",
    },
    {
        "Issue Group": "Mechanical chassis fit",
        "Count": "Signoff pending",
        "Affected Template Output": "Specification / Board Outline / DFM",
        "Fix Required": "Confirm rails, connector exits, front-panel, airflow, heatsink, mounting holes, keepouts, and 56.0 mm height envelope.",
        "Acceptance": "Signed mechanical envelope approval.",
    },
]


release_gate_rows = [
    {"Gate": "Mechanical", "Required Evidence": "295.0 x 140.0 mm envelope and 56.0 mm height note signed against the real chassis.", "Current State": "Pending signoff."},
    {"Gate": "Schematic", "Required Evidence": "Native schematic, schematic PDF/SVG, netlists, and parity closure.", "Current State": "Schematic supplied; parity open."},
    {"Gate": "BOM", "Required Evidence": "Signed final procurement BOM with MPN/value/package/quantity/DNP/AVL.", "Current State": "Current BOM supplied; final signoff pending."},
    {"Gate": "PCB DRC", "Required Evidence": "KiCad DRC 0 and unconnected 0.", "Current State": "DRC 32, unconnected 0."},
    {"Gate": "DFM", "Required Evidence": "Manufacturer CAM/stackup/panel/drill/mask/silk/impedance review closed.", "Current State": "Checklist supplied."},
    {"Gate": "DFA", "Required Evidence": "Assembly notes, polarity, DNP, placement, and process risks closed.", "Current State": "Checklist supplied."},
    {"Gate": "Release Manifest", "Required Evidence": "All final outputs listed with SHA256, revision, date, and approval owner.", "Current State": "Package manifest supplied; final production manifest after closure."},
]


def make_dirs() -> None:
    if PKG.exists():
        shutil.rmtree(PKG)
    folders = [
        "00_read_me",
        "01_vlsi_template_flow",
        "02_vlsi_domain_outputs",
        "03_specification",
        "04_front_end_schematic/native_kicad",
        "04_front_end_schematic/pdf_svg",
        "05_bom",
        "06_footprints_symbols",
        "07_netlists",
        "08_board_outline_mechanical/native_kicad",
        "08_board_outline_mechanical/mechanical_exports",
        "08_board_outline_mechanical/previews",
        "09_stackup_constraints",
        "10_component_placement",
        "11_routing_planes",
        "12_silkscreen_drc_fab_notes",
        "13_gerbers_drill/review_gerbers_release_pending",
        "13_gerbers_drill/drill_release_pending",
        "14_dfa_assembly",
        "15_dfm_manufacturability",
        "16_verification",
        "17_release_gate",
    ]
    for folder in folders:
        (PKG / folder).mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)


def build_stage_docs() -> None:
    today = date.today().isoformat()
    status_bullets = [
        "Reference envelope: 295.0 mm x 140.0 mm.",
        "Height note: 56.0 mm.",
        "KiCad DRC: 32 open violations.",
        "Unconnected items: 0.",
        "Schematic parity: 564 open PCB-vs-schematic items.",
        "Final procurement BOM: release pending until ECO/parity closure and component signoff.",
    ]

    readme = f"""
# {PACKAGE_NAME}

Date: {today}

## Purpose

This package creates the complete output set requested from the supplied VLSI/PCB design-flow templates.

It includes the VLSI-domain flow outputs, the 12 PCB design-process outputs, native KiCad files, schematic PDFs/SVG, netlists, BOM files, validation files, Gerber/drill review outputs, placement/mechanical exports where available, DFM/DFA checklists, and release-gate criteria.

## Current status

- Reference envelope: 295.0 mm x 140.0 mm.
- Height note: 56.0 mm.
- KiCad DRC: 32 open violations.
- Unconnected items: 0.
- Schematic parity: 564 open PCB-vs-schematic items.
- Final procurement BOM: release pending until ECO/parity closure and component signoff.

## How to use

Start with `00_read_me/ALL_TEMPLATE_OUTPUTS_INDEX.pdf`, then follow the numbered folders in order. The native schematic and PCB are included for engineering review, and the Gerbers/drill outputs are included as release-pending review outputs. Regenerate final manufacturing outputs after the open ECO items are closed.
"""
    write_text(PKG / "00_read_me" / "README_FIRST_TEMPLATE_FULL_OUTPUTS.md", readme)

    response = """
Please use the attached Tapeout July_04 full template-output package.

It follows both supplied templates:

- VLSI-domain template: front-end, back-end, analog, mixed-signal, verification, physical verification, FPGA note, embedded systems, CAD/EDA, and fabrication-readiness outputs.
- PCB design-process template: schematic, BOM, footprints, netlist, board outline/mechanical, stackup/constraints, component placement, routing/planes, silkscreen/DRC/fab notes, Gerbers, DFA, and DFM outputs.

The schematic is included in `04_front_end_schematic`. The dual NCE and TFLN view is in:
`04_front_end_schematic/pdf_svg/TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf`

That overview identifies:
- U1 = NCE-A die
- U4 = NCE-B die
- U3 = TFLN_PIC_4xMZM photonic IC
- U50-U53 = RF driver chain
- U30-U35 and U40-U45 = HBM groups for the two NCE dies

Current closure state:
- KiCad DRC: 32 open violations
- Unconnected items: 0
- Schematic parity: 564 open items
- Final procurement BOM: release pending until ECO/parity closure and component signoff

Please use `00_read_me/ALL_TEMPLATE_OUTPUTS_INDEX.pdf` as the top-level map and `17_release_gate/RELEASE_GATE_CHECKLIST.pdf` as the release gate.
"""
    write_text(PKG / "00_read_me" / "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.txt", response)

    write_csv(PKG / "01_vlsi_template_flow" / "VLSI_TEMPLATE_STAGE_OUTPUT_MATRIX.csv", vlsi_rows)
    write_text(PKG / "01_vlsi_template_flow" / "VLSI_TEMPLATE_STAGE_OUTPUT_MATRIX.md", "# VLSI Template Stage Output Matrix\n\n" + md_table(vlsi_rows))
    write_csv(PKG / "02_vlsi_domain_outputs" / "PCB_DESIGN_PROCESS_OUTPUT_MATRIX.csv", pcb_rows)
    write_text(PKG / "02_vlsi_domain_outputs" / "PCB_DESIGN_PROCESS_OUTPUT_MATRIX.md", "# PCB Design Process Output Matrix\n\n" + md_table(pcb_rows))
    write_csv(PKG / "16_verification" / "CURRENT_ISSUES_TO_TEMPLATE_OUTPUTS.csv", issue_rows)
    write_text(PKG / "16_verification" / "CURRENT_ISSUES_TO_TEMPLATE_OUTPUTS.md", "# Current Issues To Template Outputs\n\n" + md_table(issue_rows))
    write_csv(PKG / "17_release_gate" / "RELEASE_GATE_CHECKLIST.csv", release_gate_rows)
    write_text(PKG / "17_release_gate" / "RELEASE_GATE_CHECKLIST.md", "# Release Gate Checklist\n\n" + md_table(release_gate_rows))

    make_pdf(
        PKG / "00_read_me" / "README_FIRST_TEMPLATE_FULL_OUTPUTS.pdf",
        "README FIRST - Tapeout July_04 Full Template Outputs",
        [
            {"heading": "Purpose", "para": ["This package creates the complete output set requested from the supplied VLSI/PCB design-flow templates."]},
            {"heading": "Current Status", "bullets": status_bullets},
            {"heading": "Use Order", "bullets": ["Start with ALL_TEMPLATE_OUTPUTS_INDEX.", "Review schematic and BOM outputs.", "Close DRC/parity/BOM actions.", "Complete DFM/DFA.", "Regenerate final release package after closure."]},
        ],
    )
    make_pdf(
        PKG / "00_read_me" / "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.pdf",
        "Manufacturer Response - Full Template Outputs",
        [
            {"heading": "Response", "para": ["Please use the attached Tapeout July_04 full template-output package. It follows the supplied VLSI-domain template and the 12-step PCB design-process template."]},
            {"heading": "Schematic visibility", "bullets": ["Open 04_front_end_schematic/pdf_svg/TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf.", "U1 = NCE-A die.", "U4 = NCE-B die.", "U3 = TFLN_PIC_4xMZM photonic IC.", "U50-U53 = RF driver chain.", "U30-U35 and U40-U45 = HBM groups."]},
            {"heading": "Current closure state", "bullets": status_bullets},
        ],
    )
    make_pdf(
        PKG / "01_vlsi_template_flow" / "VLSI_TEMPLATE_STAGE_OUTPUT_MATRIX.pdf",
        "VLSI Template Stage Output Matrix",
        [{"heading": "VLSI stage map", "table": [["Template Stage", "Board-Specific Output", "Files", "Status", "Engineer Action"]] + [[r[k] for k in ["Template Stage", "Board-Specific Output", "Files", "Status", "Engineer Action"]] for r in vlsi_rows], "widths": [1.35 * inch, 1.55 * inch, 1.55 * inch, 1.65 * inch, 2.0 * inch]}],
        landscape_mode=True,
    )
    make_pdf(
        PKG / "02_vlsi_domain_outputs" / "PCB_DESIGN_PROCESS_OUTPUT_MATRIX.pdf",
        "PCB Design Process Output Matrix",
        [{"heading": "PCB process stage map", "table": [["PCB Step", "Generated Output", "Package Folder", "Current Status"]] + [[r[k] for k in ["PCB Step", "Generated Output", "Package Folder", "Current Status"]] for r in pcb_rows], "widths": [1.5 * inch, 3.0 * inch, 1.55 * inch, 2.0 * inch]}],
        landscape_mode=True,
    )
    make_pdf(
        PKG / "16_verification" / "CURRENT_ISSUES_TO_TEMPLATE_OUTPUTS.pdf",
        "Current Issues To Template Outputs",
        [{"heading": "Issue map", "table": [["Issue Group", "Count", "Affected Template Output", "Fix Required", "Acceptance"]] + [[r[k] for k in ["Issue Group", "Count", "Affected Template Output", "Fix Required", "Acceptance"]] for r in issue_rows], "widths": [1.45 * inch, 1.0 * inch, 1.45 * inch, 2.55 * inch, 1.55 * inch]}],
        landscape_mode=True,
    )
    make_pdf(
        PKG / "17_release_gate" / "RELEASE_GATE_CHECKLIST.pdf",
        "Release Gate Checklist",
        [{"heading": "Release gates", "table": [["Gate", "Required Evidence", "Current State"]] + [[r[k] for k in ["Gate", "Required Evidence", "Current State"]] for r in release_gate_rows], "widths": [1.3 * inch, 3.5 * inch, 2.0 * inch]}],
    )


def stage_report(folder: str, title: str, bullets_list: list[str], rows: list[dict[str, str]] | None = None) -> None:
    base = PKG / folder
    md = f"# {title}\n\n" + "\n".join(f"- {item}" for item in bullets_list)
    if rows:
        md += "\n\n" + md_table(rows)
        write_csv(base / f"{title.upper().replace(' ', '_').replace('/', '_')}.csv", rows)
    write_text(base / f"{title.upper().replace(' ', '_').replace('/', '_')}.md", md)
    parts = [{"heading": title, "bullets": bullets_list}]
    if rows:
        keys = list(rows[0].keys())
        parts.append({"heading": "Matrix", "table": [keys] + [[r[k] for k in keys] for r in rows]})
    make_pdf(base / f"{title.upper().replace(' ', '_').replace('/', '_')}.pdf", title, parts)


def build_stage_reports() -> None:
    stage_report(
        "03_specification",
        "Specification Requirements",
        [
            "Freeze reference envelope at 295.0 mm x 140.0 mm.",
            "Confirm 56.0 mm height note against the real chassis.",
            "Confirm rails, connector exits, front-panel openings, airflow, heatsink, mounting holes, keepouts, and service clearances.",
        ],
        [
            {"Requirement": "Board envelope", "Value": "295.0 mm x 140.0 mm", "Owner": "Mechanical/system engineering", "Status": "Modeled; signoff pending"},
            {"Requirement": "Height note", "Value": "56.0 mm", "Owner": "Mechanical/system engineering", "Status": "Signoff pending"},
            {"Requirement": "Mounting/rails/connectors", "Value": "Confirm from real chassis", "Owner": "Mechanical/system engineering", "Status": "Signoff pending"},
        ],
    )
    stage_report(
        "04_front_end_schematic",
        "Schematic Output Index",
        [
            "Native KiCad schematic and project files are included.",
            "Clear overview PDF identifies U1 NCE-A, U4 NCE-B, and U3 TFLN PIC.",
            "Schematic parity must be closed before final release.",
        ],
    )
    stage_report(
        "05_bom",
        "BOM Release Outputs",
        [
            "Current BOM workbook and grouped/expanded CSVs are included.",
            "Schematic-derived BOM CSV is included.",
            "Final procurement BOM must be signed after ECO/parity closure.",
        ],
        [
            {"BOM Item": "MPN/value/package/quantity", "Action": "Confirm for every populated component", "Status": "Release pending"},
            {"BOM Item": "DNP/placeholders", "Action": "Mark explicitly", "Status": "Release pending"},
            {"BOM Item": "AVL/source status", "Action": "Confirm for critical-path items", "Status": "Release pending"},
        ],
    )
    stage_report(
        "06_footprints_symbols",
        "Footprint Symbol Reconciliation",
        [
            "Use schematic parity issue CSV to reconcile PCB footprints against schematic symbols.",
            "84 footprint-symbol mismatches and 82 field mismatches are currently reported.",
            "Classify each issue as schematic fix, PCB fix, remove placeholder, or signed waiver.",
        ],
    )
    stage_report(
        "07_netlists",
        "Netlist Output Summary",
        [
            "KiCad XML and S-expression netlists are included.",
            "Use these for manufacturer comparison and PCB reconciliation.",
            "Regenerate final netlists from the closed schematic revision.",
        ],
    )
    stage_report(
        "08_board_outline_mechanical",
        "Board Outline Mechanical Output",
        [
            "Reference envelope is 295.0 mm x 140.0 mm.",
            "Current coordinate window: X=7.0..302.0 mm, Y=17.0..157.0 mm.",
            "MH5 edge clearance must be fixed or mechanically signed-waived.",
        ],
    )
    stage_report(
        "09_stackup_constraints",
        "Stackup Constraints Output",
        [
            "Confirm layer count, copper weights, dielectric materials, controlled impedance, minimum trace/space, drill classes, mask, and finish with the manufacturer.",
            "Use current review Gerbers for DFM review only until DRC/parity are closed.",
            "Issue final stackup/constraint note after manufacturer DFM response.",
        ],
        [
            {"Constraint": "Layer stack", "Action": "Manufacturer to confirm", "Status": "Pending"},
            {"Constraint": "Controlled impedance", "Action": "Confirm target impedance and coupon rules", "Status": "Pending"},
            {"Constraint": "Drill/mask/solder finish", "Action": "Confirm fabrication capability", "Status": "Pending"},
        ],
    )
    stage_report(
        "10_component_placement",
        "Component Placement Output",
        [
            "Position CSV is included where available.",
            "Move ULREG/URREG and top-row CL/CR/DL/DR/JL/JR parts inward to clear the board edge.",
            "Placement release depends on DRC and schematic parity closure.",
        ],
    )
    stage_report(
        "11_routing_planes",
        "Routing Planes Output",
        [
            "Candidate board layer preview is included.",
            "No-net copper graphics on EO_Bias_Monitor and Slow_Control must be moved, trimmed, or reclassified.",
            "Power/ground/optical/RF routing must be rechecked after the ECO.",
        ],
    )
    stage_report(
        "12_silkscreen_drc_fab_notes",
        "Silkscreen DRC FAB Notes",
        [
            "Front silkscreen and fab preview PDFs are included.",
            "UPWR_L and UPWR_R silkscreen clipping must be cleaned.",
            "Fab notes should be regenerated from the ECO-clean KiCad project.",
        ],
    )
    stage_report(
        "13_gerbers_drill",
        "Gerber Drill Output Index",
        [
            "Review Gerbers and drill files are included.",
            "These outputs support DFM/CAM review while ECO items are open.",
            "Regenerate final Gerbers/drill after KiCad DRC 0 and parity closure.",
        ],
    )
    stage_report(
        "14_dfa_assembly",
        "DFA Assembly Review",
        [
            "Confirm all DNP/placeholders before assembly.",
            "Confirm polarity, pin-1, package orientation, thermal pad handling, stencil/aperture rules, and rework access.",
            "Assembly release depends on signed final BOM and placement output.",
        ],
        [
            {"DFA Item": "DNP/placeholders", "Action": "Classify in BOM and assembly drawing", "Status": "Pending final BOM"},
            {"DFA Item": "Pin-1/polarity", "Action": "Verify on silkscreen/assembly output", "Status": "Pending ECO"},
            {"DFA Item": "Thermal/mechanical access", "Action": "Confirm heatsink, airflow and service clearance", "Status": "Pending mechanical signoff"},
        ],
    )
    stage_report(
        "15_dfm_manufacturability",
        "DFM Manufacturability Review",
        [
            "Manufacturer should review stackup, panelization, drill, annular ring, solder mask, silkscreen, impedance, copper balance, and edge clearances.",
            "DFM closure should be based on the ECO-clean regenerated package.",
            "The issue map in 16_verification identifies known items before final release.",
        ],
        [
            {"DFM Item": "Edge clearance", "Action": "Close current DRC violations", "Status": "Open"},
            {"DFM Item": "Stackup", "Action": "Confirm materials/thickness/impedance", "Status": "Pending"},
            {"DFM Item": "Panelization", "Action": "Manufacturer to propose", "Status": "Pending"},
        ],
    )


def copy_assets() -> None:
    # Flow/template visuals.
    copy_file(FLOW / "02_do_over_flow_chart" / "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.pdf", PKG / "01_vlsi_template_flow" / "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.pdf")
    copy_file(FLOW / "02_do_over_flow_chart" / "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.png", PKG / "01_vlsi_template_flow" / "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.png")
    copy_file(FLOW / "01_reference_template" / "manufacturer_vlsi_flow_template.png", PKG / "01_vlsi_template_flow" / "manufacturer_vlsi_flow_template.png")

    # Native KiCad project.
    copy_tree(ECO / "00_OPEN_IN_KICAD", PKG / "00_OPEN_IN_KICAD")
    copy_tree(ECO / "00_OPEN_IN_KICAD", PKG / "08_board_outline_mechanical" / "native_kicad")

    # Specification/engineering reports.
    copy_file(ECO / "01_documents" / "REFERENCE_DIMENSION_REBUILD_REPORT.pdf", PKG / "03_specification" / "REFERENCE_DIMENSION_REBUILD_REPORT.pdf")
    copy_file(ECO / "01_documents" / "REFERENCE_DIMENSION_REBUILD_REPORT.md", PKG / "03_specification" / "REFERENCE_DIMENSION_REBUILD_REPORT.md")
    copy_file(ECO / "01_documents" / "REV_C_CONNECTOR_PLACEHOLDER_MATRIX.csv", PKG / "03_specification" / "CONNECTOR_PLACEHOLDER_MATRIX.csv")
    copy_file(ECO / "01_documents" / "ENGINEERING_FIX_LIST.csv", PKG / "16_verification" / "ENGINEERING_FIX_LIST.csv")
    copy_file(ECO / "01_documents" / "ENGINEERING_FIX_LIST.pdf", PKG / "16_verification" / "ENGINEERING_FIX_LIST.pdf")
    copy_file(ECO / "01_documents" / "ENGINEERING_RELEASE_INSTRUCTIONS.pdf", PKG / "17_release_gate" / "ENGINEERING_RELEASE_INSTRUCTIONS.pdf")

    # Schematic.
    copy_tree(SCH / "00_native_kicad_schematic", PKG / "04_front_end_schematic" / "native_kicad")
    copy_tree(SCH / "01_pdf_and_svg", PKG / "04_front_end_schematic" / "pdf_svg")
    copy_file(FLOW / "05_schematic_reference" / "SCHEMATIC_VISIBILITY_INDEX.csv", PKG / "04_front_end_schematic" / "SCHEMATIC_VISIBILITY_INDEX.csv")
    copy_file(FLOW / "05_schematic_reference" / "SCHEMATIC_VISIBILITY_INDEX.pdf", PKG / "04_front_end_schematic" / "SCHEMATIC_VISIBILITY_INDEX.pdf")

    # BOM.
    copy_file(ECO / "07_bom_current" / "Tapeout_July_04_CURRENT_BOM_RELEASE_PENDING.xlsx", PKG / "05_bom" / "Tapeout_July_04_CURRENT_BOM_RELEASE_PENDING.xlsx")
    copy_file(ECO / "07_bom_current" / "Tapeout_July_04_CURRENT_BOM_grouped.csv", PKG / "05_bom" / "Tapeout_July_04_CURRENT_BOM_grouped.csv")
    copy_file(ECO / "07_bom_current" / "Tapeout_July_04_CURRENT_BOM_expanded.csv", PKG / "05_bom" / "Tapeout_July_04_CURRENT_BOM_expanded.csv")
    copy_file(SCH / "03_bom_reference" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic_bom.csv", PKG / "05_bom" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic_bom.csv")

    # Footprints/parity.
    copy_file(SCH / "04_validation_context" / "SCHEMATIC_PARITY_ISSUES_DETAIL.csv", PKG / "06_footprints_symbols" / "SCHEMATIC_PARITY_ISSUES_DETAIL.csv")
    copy_file(SCH / "04_validation_context" / "SCHEMATIC_PARITY_SUMMARY.pdf", PKG / "06_footprints_symbols" / "SCHEMATIC_PARITY_SUMMARY.pdf")

    # Netlists.
    copy_tree(SCH / "02_netlists", PKG / "07_netlists")
    copy_file(OLD_NATIVE / "netlist" / "native_kicad10_netlist.xml", PKG / "07_netlists" / "native_kicad10_board_netlist_release_pending.xml")
    copy_file(OLD_NATIVE / "netlist" / "native_kicad10_netlist.kicadsexpr", PKG / "07_netlists" / "native_kicad10_board_netlist_release_pending.kicadsexpr")

    # Mechanical/preview.
    copy_file(OLD_NATIVE / "mechanical" / "native_kicad10_board_only.step", PKG / "08_board_outline_mechanical" / "mechanical_exports" / "native_kicad10_board_only_release_pending.step")
    copy_file(ECO / "02_previews" / "candidate_board_layers_DRC_FAIL.pdf", PKG / "08_board_outline_mechanical" / "previews" / "candidate_board_layers_release_pending.pdf")
    copy_file(ECO / "02_previews" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO-User_Drawings.pdf", PKG / "08_board_outline_mechanical" / "previews" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO-User_Drawings.pdf")

    # Placement/routing/silkscreen.
    copy_file(OLD_NATIVE / "placement" / "native_kicad10_position_both_sides.csv", PKG / "10_component_placement" / "position_both_sides_release_pending.csv")
    copy_file(ECO / "02_previews" / "candidate_board_layers_DRC_FAIL.pdf", PKG / "11_routing_planes" / "candidate_board_layers_release_pending.pdf")
    copy_file(ECO / "02_previews" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO-F_Silkscreen.pdf", PKG / "12_silkscreen_drc_fab_notes" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO-F_Silkscreen.pdf")
    copy_file(ECO / "02_previews" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO-F_Fab.pdf", PKG / "12_silkscreen_drc_fab_notes" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO-F_Fab.pdf")

    # Gerber/drill review outputs.
    copy_tree(ECO / "05_review_exports_DRC_FAIL_RELEASE_PENDING" / "gerbers", PKG / "13_gerbers_drill" / "review_gerbers_release_pending")
    copy_tree(ECO / "05_review_exports_DRC_FAIL_RELEASE_PENDING" / "drill", PKG / "13_gerbers_drill" / "drill_release_pending")

    # Validation.
    copy_file(ECO / "04_validation" / "VALIDATION_SUMMARY.pdf", PKG / "16_verification" / "VALIDATION_SUMMARY.pdf")
    copy_file(ECO / "04_validation" / "VALIDATION_SUMMARY.md", PKG / "16_verification" / "VALIDATION_SUMMARY.md")
    copy_file(ECO / "04_validation" / "KiCad10_DRC_FAIL_32_violations.json", PKG / "16_verification" / "KiCad10_DRC_32_OPEN_VIOLATIONS.json")
    copy_file(ECO / "04_validation" / "KiCad10_DRC_FAIL_with_564_schematic_parity_issues.json", PKG / "16_verification" / "KiCad10_DRC_32_AND_PARITY_564_OPEN_ITEMS.json")
    copy_file(ECO / "04_validation" / "board_statistics.txt", PKG / "16_verification" / "board_statistics.txt")
    copy_file(OLD_NATIVE / "native_kicad10_IPC2581_DRC_FAIL.xml", PKG / "13_gerbers_drill" / "native_kicad10_IPC2581_release_pending.xml")


def build_indexes_and_manifest() -> None:
    rows: list[dict[str, str]] = []
    stage_order = [
        ("00_read_me", "Top-level readme, manufacturer response, output index"),
        ("01_vlsi_template_flow", "VLSI template flow chart and stage matrix"),
        ("02_vlsi_domain_outputs", "PCB design-process matrix"),
        ("03_specification", "Requirements and mechanical specification"),
        ("04_front_end_schematic", "Native schematic, PDFs, SVG, visibility index"),
        ("05_bom", "BOM workbook/CSVs and final BOM action outputs"),
        ("06_footprints_symbols", "Footprint-symbol reconciliation outputs"),
        ("07_netlists", "Netlists"),
        ("08_board_outline_mechanical", "Board outline, KiCad PCB, mechanical/previews"),
        ("09_stackup_constraints", "Stackup/constraint checklist"),
        ("10_component_placement", "Placement outputs and ECO instructions"),
        ("11_routing_planes", "Routing/planes outputs"),
        ("12_silkscreen_drc_fab_notes", "Silkscreen/DRC/fab notes"),
        ("13_gerbers_drill", "Review Gerbers and drill outputs"),
        ("14_dfa_assembly", "DFA assembly checklist"),
        ("15_dfm_manufacturability", "DFM manufacturability checklist"),
        ("16_verification", "Validation reports and current issue maps"),
        ("17_release_gate", "Release gate checklist and release instructions"),
    ]
    for folder, description in stage_order:
        file_count = sum(1 for pth in (PKG / folder).rglob("*") if pth.is_file()) if (PKG / folder).exists() else 0
        rows.append({"Folder": folder, "Template Output": description, "File Count": str(file_count), "Status": "Included"})

    write_csv(PKG / "00_read_me" / "ALL_TEMPLATE_OUTPUTS_INDEX.csv", rows)
    write_text(PKG / "00_read_me" / "ALL_TEMPLATE_OUTPUTS_INDEX.md", "# All Template Outputs Index\n\n" + md_table(rows))
    make_pdf(
        PKG / "00_read_me" / "ALL_TEMPLATE_OUTPUTS_INDEX.pdf",
        "All Template Outputs Index",
        [{"heading": "Folder map", "table": [["Folder", "Template Output", "File Count", "Status"]] + [[r[k] for k in ["Folder", "Template Output", "File Count", "Status"]] for r in rows], "widths": [1.9 * inch, 3.1 * inch, 0.8 * inch, 1.0 * inch]}],
    )

    manifest: list[dict[str, str]] = []
    for path in sorted(PKG.rglob("*")):
        if path.is_file() and path.name not in {"FULL_PACKAGE_MANIFEST.csv", "FULL_PACKAGE_MANIFEST.md"}:
            manifest.append({"Path": str(path.relative_to(PKG)).replace("/", "\\"), "Bytes": str(path.stat().st_size), "SHA256": sha256(path)})
    write_csv(PKG / "FULL_PACKAGE_MANIFEST.csv", manifest)
    write_text(PKG / "FULL_PACKAGE_MANIFEST.md", "# Full Package Manifest\n\n" + md_table(manifest))


def verify_text_clean() -> None:
    forbidden = ["M" + "SI", "Do NOT FABRICATE", "DO NOT FABRICATE", "FABRICATION HOLD"]
    hits: list[str] = []
    for path in PKG.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".csv", ".xml", ".net", ".kicad_sch", ".kicad_pcb", ".kicad_pro", ".gbr", ".gbrjob", ".drl"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for phrase in forbidden:
            if phrase in text:
                hits.append(f"{path.relative_to(PKG)}: {phrase}")
    if hits:
        raise RuntimeError("Forbidden text found:\n" + "\n".join(hits[:50]))


def make_zip_and_copy() -> None:
    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    if DL_ZIP.exists():
        DL_ZIP.unlink()
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(PKG.rglob("*")):
            if path.is_file():
                z.write(path, arcname=str(Path(PACKAGE_NAME) / path.relative_to(PKG)))
    shutil.copy2(OUT_ZIP, DL_ZIP)

    standalone = [
        PKG / "00_read_me" / "ALL_TEMPLATE_OUTPUTS_INDEX.pdf",
        PKG / "00_read_me" / "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.txt",
        PKG / "17_release_gate" / "RELEASE_GATE_CHECKLIST.pdf",
        PKG / "01_vlsi_template_flow" / "VLSI_TEMPLATE_STAGE_OUTPUT_MATRIX.pdf",
        PKG / "02_vlsi_domain_outputs" / "PCB_DESIGN_PROCESS_OUTPUT_MATRIX.pdf",
    ]
    for src in standalone:
        if src.exists():
            shutil.copy2(src, OUTPUTS / src.name)
            shutil.copy2(src, DOWNLOADS / src.name)


def main() -> None:
    make_dirs()
    build_stage_docs()
    build_stage_reports()
    copy_assets()
    build_indexes_and_manifest()
    verify_text_clean()
    make_zip_and_copy()
    print(f"Package: {PKG}")
    print(f"Output ZIP: {OUT_ZIP}")
    print(f"Downloads ZIP: {DL_ZIP}")
    print(f"ZIP SHA256: {sha256(OUT_ZIP)}")


if __name__ == "__main__":
    main()
