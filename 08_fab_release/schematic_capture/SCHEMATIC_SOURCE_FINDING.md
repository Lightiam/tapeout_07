# Schematic Source Finding — correction and capture basis

This revises the earlier "no schematic source exists anywhere" conclusion after a
full read of the PDFs in `../../03_schematic_transmittal/`.

## What actually exists

**An authoritative schematic *did* exist — Rev 4.0, KiCad 10.0.3, dated
2026-06-24** — and survives in the repo as a PDF export:

- `03_schematic_transmittal/TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic.pdf`
  — the full A0 sheet. Title block: **Rev 4.0**, file
  `TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_sch`.
- `03_schematic_transmittal/TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf`
  — a readable callout of the critical blocks.

It contains **real design content**, not a block diagram: every component with
named signal pins, a seven-block subsystem partition, and named power/clock nets.
That content is captured here in `component_pin_inventory.csv` and
`interface_net_map.csv`.

## Three problems that stop it from being "the source"

1. **The editable `.kicad_sch` is missing.** Only the PDF export is in the repo.
   The `.kicad_sch` present under `07_engineering_reconcile/` is a **stub**
   (2,311 lines, ~28 wires, 0 explicit nets) — it is *not* the Rev 4.0 source that
   produced this PDF. Its companion files, referenced on the PDF —
   `BOM_USER_SUPPLIED.csv` and `COMPONENT_VALIDATION.md` — are also absent.

2. **It is explicitly preliminary.** The sheet states *"User-supplied MPNs and
   placeholder pins require authoritative validation"* and the overview status is
   *"Engineering ECO required / release pending."* Connectivity is shown largely at
   **bus level** (HBM bus, MZM RF drive, OPT_TX[0..3]) — pin-to-pin nets are only
   partially resolved even in Rev 4.0.

3. **Target conflict — this is the big one.** The schematic title block describes a
   **305 × 280 mm, 22-layer LNOI hybrid, ENIG, IPC Class 3** board
   ("22-Layer Intelligence Stack Motherboard"). The PCB we cleaned up and fab-audited
   (`07_engineering_reconcile`, `08_fab_release`) is a **295 × 140 mm, 4-layer**
   board. **These are two different physical designs.** Before any routing or fab
   approval, engineering must decide which is the real target — the 22-layer
   schematic intent, or the 4-layer reconstruction. They cannot both be the product.

## The two paths (unchanged in spirit, sharper now)

- **Path A — recover the Rev 4.0 source (fastest, authoritative).** Locate the
  original `TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_sch` (Rev 4.0, KiCad 10.0.3)
  plus `BOM_USER_SUPPLIED.csv` and `COMPONENT_VALIDATION.md`. Whoever exported this
  PDF on 2026-06-24 has it. Import → validate placeholder pins → drive ERC/parity to
  0. **Please provide this file if it exists.**
- **Path B — re-capture from the PDF.** If the source is unrecoverable, re-capture
  in KiCad using the extracted inventory here as the seed. This is *far* better than
  from scratch — the components, pinouts, subsystem partition, and named nets are
  all defined — but the placeholder pins and unresolved bus-to-pin mappings must be
  authored against real device datasheets and validated.

## Subsystem partition (for hierarchical capture)

1. NCE-A (U1) + HBM4 group (U30–U35)
2. NCE-B (U4) + HBM4 group (U40–U45)
3. TFLN Photonic IC (U3) + MZM RF driver chain (U50–U53)
4. Power delivery — 24-phase VPD (U200–U203, U210–U233, U240–U243)
5. Clock distribution (U250, U251 — Si5395A, <50 fs jitter)
6. Host / fabric — PCIe 5.0 switches (U270–U273) + x16 slots (J20–J23) + retimers (U260–U263)
7. Management — BMC (U380) + decoupling (C1–C16)

## Named power / clock rails observed on the sheet

`+12V_IN`, `VDD_CORE_0V8`, `VDD_IO_1V8`, `VDD_HBM_1V2`, `VDD_RF_0V9`, `+3V3`,
`CLK_REF_100M`, `CLK_CORE_2G`, `CLK_NOC_1G`.

## Bottom line

The earlier statement "no source exists" was too strong: a **Rev 4.0 schematic
exists as a PDF** and defines the design intent. What is missing is the **editable
source** and **validated pin-level connectivity**, and there is an unresolved
**4-layer vs 22-layer target conflict**. Path A (recover the `.kicad_sch`) is the
correct next step; this folder is the ready-made basis for Path B if it is not.
