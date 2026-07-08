# Fabrication Notes — TFLN_AI_NODE_X2_SERVER_CHASSIS_IO

Values marked **[from files]** are extracted directly from the released Gerber/
drill/board files and are authoritative. Values marked **[SIGN-OFF]** are
recommended engineering defaults that must be confirmed before production.

## Board summary

| Parameter | Value | Source |
| --- | --- | --- |
| Board name | TFLN_AI_NODE_X2_SERVER_CHASSIS_IO | [from files] |
| Outline size | **295.15 mm × 140.15 mm** | [from files] `.gbrjob` GeneralSpecs |
| Edge.Cuts bbox (board coords) | 295.0 × 141.0 mm | [from files] board Edge.Cuts |
| Layer count | 4 (copper) | [from files] |
| Board thickness | 1.60 mm | [from files] |
| Surface finish | **ENIG** | [SIGN-OFF] — job file shipped `"None"` |
| Revision | **X2-ENG-A** (engineering reference; bump for production) | [SIGN-OFF] — job file shipped `"rev?"` |
| Generator | KiCad 10.0.3 / Pcbnew | [from files] |

## Layer stackup (as defined in the board)

| # | Gerber file function | KiCad layer | User net-class name |
| --- | --- | --- | --- |
| L1 (Top) | Copper, L1, Top | F.Cu | EO_Bias_Monitor |
| L2 (Inner) | Copper, L2, Inner | In1.Cu | Electrical_GND |
| L3 (Inner) | Copper, L3, Inner | In2.Cu | Electrical_Power |
| L4 (Bottom) | Copper, L4, Bottom | B.Cu | Slow_Control |

**[SIGN-OFF] Mechanical stackup / impedance:** the copper layer order is defined,
but no dielectric thicknesses, copper weights, or target impedances are specified
in the design. Because the board carries an RF driver chain (HMC8410), PCIe Gen5
(x16 slots), and BCM84881 retimer links, a controlled-impedance 4-layer stackup
must be defined with the fabricator. Provide, at minimum:
- Dielectric material (e.g., low-loss laminate for the RF/PCIe nets), core/prepreg
  thicknesses summing to 1.60 mm ± tolerance.
- Copper weights (e.g., 1 oz outer / 0.5 oz inner) — confirm against current needs
  of the power planes (24× ISL99390 smart power stages).
- Target single-ended and differential impedances for the high-speed net classes
  and which layers reference which plane.

## Design rules (from Gerber job file) [from files]

| Rule | Outer | Inner |
| --- | --- | --- |
| Pad-to-pad | 0.20 mm | 0.20 mm |
| Pad-to-track | 0.20 mm | 0.20 mm |
| Track-to-track | 0.20 mm | 0.20 mm |
| Min line width | 0.10 mm | — |

Minimum feature is 0.10 mm (≈4 mil) track / 0.20 mm (≈8 mil) clearance — a
standard fabricator capability; no advanced HDI class is implied by these rules.

## Drill table [from files]

See `data/drill_report.csv`.

| Tool | Ø (mm) | Qty | Plating | Notes |
| --- | ---: | ---: | --- | --- |
| T1 | 0.350 | 180 | PTH | via / small PTH |
| T2 | 0.450 | 44 | PTH | PTH |
| T3 | 0.500 | 16 | PTH | PTH |
| T4 | 0.900 | 8 | PTH | PTH |
| T5 | 3.200 | 12 | **NPTH** | M3 mounting holes |
| **Total** | | **260** | | |

Smallest plated hole 0.35 mm; drill format is absolute metric, decimal (KiCad
`FSLAX46`). Mixed plating, layer span 1→4.

## Gerber layer manifest (Step-01 drop) [from files]

Copper: `-EO_Bias_Monitor` (F.Cu), `-Electrical_GND` (In1), `-Electrical_Power`
(In2), `-Slow_Control` (B.Cu). Plus `-F_Mask`/`-B_Mask`, `-F_Paste`/`-B_Paste`,
`-F_Silkscreen`/`-B_Silkscreen`, `-Edge_Cuts`, `-User_Comments`, `-User_Drawings`,
`-User_Eco1`/`-User_Eco2`, the `.gbrjob`, and the `.drl` NC drill file (17 files).

**Recommended additions before production release** (require KiCad regeneration):
- Fabrication drawing sheet (drill map + notes) as PDF.
- IPC-2581 or IPC-D-356 netlist for bare-board electrical test.
- Assembly drawings (top/bottom) + this centroid file for the CM.

## Assembly / DFA

- 82 netlisted placements, all top-side (`F.Cu`). Centroid file:
  `data/centroid_pick_and_place.csv`.
- Fine-pitch/area-array packages present (BGA-2500, BGA-1024, multiple QFN/PQFN)
  → ENIG finish and controlled reflow profile recommended; confirm CM capability
  for the BGA-2500 pitch.
- Placeholder parts (see `CLARIFICATION_DECISION_LOG.md` Q-A) must have final
  populate/DNP state before the pick-and-place is released.

## Notes for the fabricator

- Board is currently a **reference reconstruction** — do **not** fabricate for
  production against this drop until the schematic-parity and placeholder sign-off
  items in `FAB_READINESS_ASSESSMENT.md` are closed and files are re-issued marked
  FINAL.
- The corrected job file `data/…-job_REV_X2-ENG-A.gbrjob` supersedes the shipped
  job file's `Finish`/`Revision` fields once the ENIG + revision sign-off is made.
