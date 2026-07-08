from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(r"C:\Users\bolao\Documents\Codex\2026-07-04\https-us06web-zoom-us-j-84402744475")
REPO = ROOT / "work" / "github_tapeout_07"


styles = getSampleStyleSheet()
TITLE = ParagraphStyle(
    "Title",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=22,
    textColor=colors.HexColor("#12344d"),
    spaceAfter=8,
)
SUBTITLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#334155"),
    spaceAfter=8,
)
CELL = ParagraphStyle(
    "Cell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.2,
    leading=8.5,
)
HEADER = ParagraphStyle(
    "Header",
    parent=CELL,
    fontName="Helvetica-Bold",
    textColor=colors.white,
)
CALLOUT = ParagraphStyle(
    "Callout",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=10,
)


def para(text: str, style=CELL):
    return Paragraph(text.replace("\n", "<br/>"), style)


def table_pdf(path: Path, title: str, subtitle: str, headers: list[str], rows: list[list[str]], col_widths: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )
    data = [[para(h, HEADER) for h in headers]]
    data.extend([[para(c) for c in row] for row in rows])
    tbl = Table(data, colWidths=[w * mm for w in col_widths], repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12344d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eff6ff")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    doc.build([para(title, TITLE), para(subtitle, SUBTITLE), tbl])


def schematic_overview(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    blocks = [
        para("TFLN_AI_NODE_X2 - Critical Schematic Overview", TITLE),
        para(
            "Dual NCE dies, HBM groups, the TFLN photonic IC, and the RF driver chain are called out here for manufacturer and engineering review. Status: engineering review; complete schematic/netlist source required to close 214 schematic-parity warnings.",
            SUBTITLE,
        ),
        Spacer(1, 5 * mm),
    ]
    cards = [
        ("NCE-A DIE", "Ref: U1\nValue: NCE_Gen3_SpikingBrain\nFootprint: BGA-2500 40x40mm\nMPN: LR-NCE-G3-BGA2500-001\nTFLN lanes: P/N 0..3"),
        ("NCE-B DIE", "Ref: U4\nValue: NCE_Gen3_SpikingBrain\nFootprint: BGA-2500 40x40mm\nMPN: LR-NCE-G3-BGA2500-001\nTFLN lanes: P/N 0..3"),
        ("TFLN PHOTONIC IC", "Ref: U3\nValue: TFLN_PIC_4xMZM\nFootprint: Custom optical module 25x8mm\nMPN: TFLN-MZM-400G-C\nFunction: 4 x TW-MZM / optical TX"),
        ("RF DRIVER CHAIN", "Refs: U50, U51, U52, U53\nValue: HMC8410\nFunction: 100GHz differential RF drive\nFeeds TFLN/MZM modulation chain"),
        ("HBM4 FOR NCE-A", "U30, U31, U32, U33, U34, U35\n6 x HBM4-16GB stacks\nGroup total: 96GB"),
        ("HBM4 FOR NCE-B", "U40, U41, U42, U43, U44, U45\n6 x HBM4-16GB stacks\nGroup total: 96GB"),
        ("OPTICAL OUTPUTS", "U3 outputs: OPT_TX0, OPT_TX1, OPT_TX2, OPT_TX3\nU1 and U4 expose TFLN_TX lane groups P/N 0..3"),
        ("ENGINEERING NOTE", "This overview is a readable callout sheet. It does not replace the missing complete schematic/netlist source needed for parity closure."),
    ]
    data = []
    for i in range(0, len(cards), 2):
        row = []
        for title, body in cards[i : i + 2]:
            row.append(para(f"<b>{title}</b><br/>{body}", CALLOUT))
        data.append(row)
    tbl = Table(data, colWidths=[88 * mm, 88 * mm])
    tbl.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    blocks.extend([tbl, Spacer(1, 5 * mm)])
    cross_ref = [
        ["Ref", "Block", "Value / MPN", "Role"],
        ["U1", "NCE-A die", "NCE_Gen3_SpikingBrain / LR-NCE-G3-BGA2500-001", "Neural compute engine A; TFLN TX lane group and HBM group U30-U35."],
        ["U4", "NCE-B die", "NCE_Gen3_SpikingBrain / LR-NCE-G3-BGA2500-001", "Neural compute engine B; TFLN TX lane group and HBM group U40-U45."],
        ["U3", "TFLN photonic IC", "TFLN_PIC_4xMZM / TFLN-MZM-400G-C", "LiNbO3 photonic IC with 4 x TW-MZM and OPT_TX0..OPT_TX3."],
        ["U50-U53", "RF driver chain", "HMC8410 / HMC8410LP2FE", "Differential RF drivers feeding the TFLN/MZM modulation chain."],
        ["U30-U35", "HBM4 for NCE-A", "HBM4-16GB / SK_HBM4_16GB_12H", "Six HBM4 stacks near U1."],
        ["U40-U45", "HBM4 for NCE-B", "HBM4-16GB / SK_HBM4_16GB_12H", "Six HBM4 stacks near U4."],
    ]
    blocks.append(make_small_table(cross_ref, [22, 38, 62, 58]))
    doc.build(blocks)


def text_pdf(path: Path, title: str, source_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )
    story = [para(title, TITLE), para("Current July_04 manufacturer response text.", SUBTITLE)]
    for block in source_text.strip().split("\n\n"):
        story.append(para(block.replace("\n", "<br/>"), CALLOUT))
        story.append(Spacer(1, 3 * mm))
    doc.build(story)


def make_small_table(data: list[list[str]], widths: list[float]):
    table = Table([[para(c, HEADER if r == 0 else CELL) for c in row] for r, row in enumerate(data)], colWidths=[w * mm for w in widths], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12344d")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eff6ff")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def main() -> None:
    table_pdf(
        REPO / "01_full_template_outputs" / "PCB_DESIGN_PROCESS_OUTPUT_MATRIX.pdf",
        "PCB Design Process Output Matrix",
        "Current July_04 status based on KiCad 10.0.3 validation after non-netlist manufacturability cleanup.",
        ["PCB Step", "Generated Output", "Package Folder", "Current Status"],
        [
            ["1. Schematic Creation / Validation", "Native KiCad schematic stub and readable dual-NCE/TFLN overview.", "04_front_end_schematic", "Complete schematic/netlist source required to close 214 parity warnings."],
            ["2. BOM", "Current BOM workbook with grouped and expanded placements.", "05_bom", "Current July_04 review list; owner signoff required for AVL, quantity, DNP/populate, substitutions, and parity."],
            ["3. Footprint Creation / Validation", "Project-local footprint libraries and reconciliation evidence.", "06_footprints_symbols", "82 library/footprint mismatch warnings remain for engineering review."],
            ["4. Netlist", "Board net table and available reference exports.", "07_netlists", "Authoritative schematic/netlist source still required; current schematic is a stub."],
            ["5. Board Outline / Mechanical Detail", "KiCad Edge.Cuts and mechanical notes.", "08_board_outline_mechanical", "Current Edge.Cuts approx. 305.0 mm x 260.5 mm; chassis constraints need confirmation."],
            ["6. Stackup / Constraints Setting", "Board setup stackup and manufacturer checklist.", "09_stackup_constraints", "4-layer High-Tg FR4 review stackup and ENIG finish metadata added."],
            ["7. Component Placement", "Placement ECO notes and current PCB source.", "10_component_placement", "Six board-only fiducials added; placement still needs chassis, thermal, and SI review."],
            ["8. Routing and Planes", "Current routing/plane state and review notes.", "11_routing_planes", "0 unconnected items in current DRC; real schematic/netlist needed for electrical closure."],
            ["9. Silkscreen / DRC / FAB Notes", "Silkscreen/fab-note review and DRC records.", "12_silkscreen_drc_fab_notes", "Silkscreen-over-copper warnings cleared; 82 library warnings remain."],
            ["10. Gerber Generation", "Review Gerbers, drill, drill map/report, and Gerber index.", "13_gerbers_drill", "Post-cleanup Gerber/drill review export generated and copied to Step 01 pair."],
            ["11. DFA", "Assembly/DFA checklist and action matrix.", "14_dfa_assembly", "Review placement, polarity, DNP/populate, and BOM owner signoff."],
            ["12. DFM", "DFM/manufacturability checklist and action matrix.", "15_dfm_manufacturability", "Submit post-cleanup Gerber/drill package for DFM plus stackup and chassis confirmation."],
        ],
        [55, 75, 42, 95],
    )

    table_pdf(
        REPO / "01_full_template_outputs" / "VLSI_TEMPLATE_STAGE_OUTPUT_MATRIX.pdf",
        "VLSI Template Stage Output Matrix",
        "Board-specific VLSI flow view for the July_04 engineering review package.",
        ["Template Stage", "Board-Specific Output", "Files", "Status", "Engineer Action"],
        [
            ["1. Front-End Design", "Schematic closure package", "04_front_end_schematic, 07_netlists, 16_verification", "214 schematic-parity warnings remain.", "Provide complete schematic/netlist source and close or sign-waive parity."],
            ["2. Back-End Design", "PCB ECO package", "08_board_outline_mechanical, 10_component_placement, 11_routing_planes", "0 DRC errors; 82 library/footprint mismatch warnings.", "Resolve library mappings and confirm chassis/mechanical constraints."],
            ["3. Analog Design", "TFLN optical/RF/bias review", "04_front_end_schematic, 06_footprints_symbols, 12_silkscreen_drc_fab_notes", "Review output issued.", "Validate TFLN PIC, RF drivers, bias rails, monitor lines, and MZM lanes."],
            ["4. Mixed-Signal Design", "NCE-to-TFLN interface review", "04_front_end_schematic, 07_netlists", "Interface mapping requires authoritative netlist.", "Confirm TFLN_TX lane mapping plus SPI/I2C/JTAG/PLL/AST2600 interfaces."],
            ["5. Verification Domain", "Validation reports and issue logs", "16_verification", "0 unconnected items; parity still open.", "Target parity zero using complete schematic/netlist source."],
            ["6. Physical Verification", "DRC, board outline, mechanical, fab notes", "08_board_outline_mechanical, 12_silkscreen_drc_fab_notes, 16_verification", "Current DRC has 82 warnings.", "Rerun KiCad DRC after footprint/library and mechanical closure."],
            ["7. FPGA Design", "Interface reserve", "02_vlsi_domain_outputs/FPGA_DOMAIN_NOTE", "No FPGA-specific RTL supplied.", "If programmable logic is added, issue RTL, constraints, bitstream, and verification logs."],
            ["8. Embedded Systems", "AST2600/service-interface checklist", "02_vlsi_domain_outputs/EMBEDDED_SYSTEMS_SERVICE_CHECKLIST", "Checklist output issued.", "Confirm firmware ownership, boot straps, management bus, sensors, reset, and update path."],
            ["9. CAD / EDA Tool Development", "KiCad project, generated reports, manifest", "00_OPEN_IN_KICAD, FULL_PACKAGE_MANIFEST", "KiCad-compatible handoff format.", "Use KiCad 10.0.3 or later and preserve checksum manifest."],
            ["10. Semiconductor Fabrication", "PCB fab/assembly review package", "13_gerbers_drill, 14_dfa_assembly, 15_dfm_manufacturability, 17_release_gate", "DFM/DFA review package issued.", "Complete DFM/DFA, BOM owner signoff, and parity closure before production package approval."],
        ],
        [42, 50, 55, 52, 68],
    )

    table_pdf(
        REPO / "02_do_over_vlsi_flow" / "RELEASE_OUTPUTS_REQUIRED.pdf",
        "Release Outputs Required",
        "Current required-output checklist for the July_04 engineering review flow.",
        ["Required Output", "Owner", "Release Criteria", "Current State"],
        [
            ["Signed mechanical specification", "Mechanical / system engineering", "Envelope, datum, rails, keepouts, holes, connector exits, heatsink, and airflow confirmed.", "Current Edge.Cuts approx. 305.0 mm x 260.5 mm; chassis constraints need confirmation."],
            ["Native schematic and schematic PDF/SVG", "Electrical engineering", "Dual NCE, TFLN PIC, RF/bias, HBM, PCIe/control/power blocks visible and aligned to netlist.", "Readable overview exists; complete schematic/netlist source is still required."],
            ["Closed netlists", "Electrical engineering", "Generated from closed schematic and loaded into PCB with no unexplained differences.", "214 schematic-parity warnings remain until authoritative source is imported."],
            ["PCB native project", "PCB layout engineering", "Updated KiCad project with 0 DRC errors and 0 unintended unconnected items.", "Current DRC: 0 errors, 0 unconnected items, 82 library/footprint mismatch warnings."],
            ["Gerbers, drill, drill map, stackup, impedance notes", "PCB layout / manufacturer CAM", "Generated from reviewed PCB and approved by DFM.", "Post-cleanup Gerber/drill review package generated; stackup and impedance require manufacturer confirmation."],
            ["Placement and assembly outputs", "PCB layout / assembly engineering", "XY placement, centroid, assembly drawings, polarity and DNP markings match signed BOM.", "Placement/fiducials updated; BOM/DNP/populate owner signoff required."],
            ["Procurement BOM", "Component / procurement engineering", "MPN, value, package, quantity, source/AVL, DNP, alternates, revision/date signed.", "Current July_04 BOM review list updated; AVL, quantity, substitutions, and parity require owner signoff."],
            ["Validation report", "Electrical / PCB verification", "DRC 0 errors, unconnected 0, schematic parity closed or signed-waived, ERC reviewed.", "Current validation: 82 DRC warnings, 0 unconnected, 214 parity warnings."],
            ["DFM/DFA closure report", "Manufacturer with engineering review", "CAM, panelization, solder mask, silkscreen, drill, stackup, assembly and test risks closed.", "DFM/DFA review should use post-cleanup Gerber/drill package."],
            ["Release manifest", "Release engineering", "All files listed with SHA256, revision, date, and owner approval.", "Repository checksum manifest regenerated after this cleanup."],
        ],
        [55, 45, 85, 85],
    )

    schematic_overview(
        REPO / "03_schematic_transmittal" / "TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf"
    )

    text_pdf(
        REPO / "01_full_template_outputs" / "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.pdf",
        "Manufacturer Response - Full Template Outputs",
        (REPO / "01_full_template_outputs" / "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.txt").read_text(encoding="utf-8"),
    )
    text_pdf(
        REPO / "02_do_over_vlsi_flow" / "MANUFACTURER_RESPONSE_DO_OVER.pdf",
        "Manufacturer Response - Do-Over Flow",
        (REPO / "02_do_over_vlsi_flow" / "MANUFACTURER_RESPONSE_DO_OVER.txt").read_text(encoding="utf-8"),
    )


if __name__ == "__main__":
    main()
