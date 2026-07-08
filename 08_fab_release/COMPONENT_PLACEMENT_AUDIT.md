# Component Placement Audit

**Source:** `../07_engineering_reconcile/00_OPEN_IN_KICAD_PATCHED/TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pcb`
**Question answered:** *Is every component placed on the PCB?*
**Answer:** Yes — all 82 netlisted BOM components are placed. Nothing is missing.

## Method

Every `(footprint …)` block in the board file was parsed for its reference
designator, position, rotation, layer, and attributes. Placements were then
cross-checked against the Step-01 BOM (`Grouped BOM` / `Expanded Placements`).

## Result

| Category | Count | On the board? |
| --- | ---: | --- |
| Total footprints in the PCB | 9,021 | yes |
| **Netlisted BOM components** | **82** | **all 82 placed — 0 missing** |
| `board_only` reference footprints | 8,939 | yes (intentional, no schematic symbol) |

### The 82 netlisted parts (all present)

| Qty | Refs | Part |
| ---: | --- | --- |
| 16 | C1–C16 | 100 nF 0402 decoupling |
| 4 | J20–J23 | PCIe x16 slot |
| 2 | U1, U4 | NCE Gen3 SpikingBrain (BGA-2500) |
| 1 | U3 | TFLN PIC 4×MZM (custom optical) |
| 12 | U30–U35, U40–U45 | HBM4 16 GB (BGA-1024) |
| 4 | U50–U53 | HMC8410 RF driver (QFN) |
| 4 | U200–U203 | ISL69260 PWM controller (QFN) |
| 24 | U210–U233 | ISL99390 smart power stage (PQFN) |
| 4 | U240–U243 | ADP7118-0.9V LDO (SOT) |
| 2 | U250, U251 | Si5395A clock (QFN) |
| 4 | U260–U263 | BCM84881 retimer (QFN) |
| 4 | U270–U273 | PEX88096 PCIe switch (QFN) |
| 1 | U380 | AST2600 BMC (QFN) |

A machine-readable centroid / pick-and-place file for these parts is in
`data/centroid_pick_and_place.csv` (Ref, Value, X, Y, rotation, side, populate).
All 82 are on the top side (`F.Cu`).

## The 8,939 `board_only` footprints — what they are and why they are correct

These footprints carry KiCad's **`board_only`** attribute ("Not in schematic").
That is a deliberate flag: they are geometry the board needs but that has no
electrical symbol, so KiCad **excludes them from schematic parity, netlist, and
BOM by design**. They are not "missing from the schematic" — they are declared
board-only. Breakdown by prefix:

| Prefix | Count | What it represents |
| --- | ---: | --- |
| `XP` | 8,326 | Photonic / pad reference array (the dense field visible on the layout) |
| `VG` | 44 | Guard / stitching vias |
| `MH` | 12 | Mounting holes (M3, NPTH 3.2 mm) |
| `UL/UR/RL/RR/JL/JR/CL/CR/DL/DR…` | ~557 | Edge optical / bias **placeholder** clusters (see decision log Q-A) |

This is consistent with the board's own silkscreen, which is stamped
**`REFERENCE RECONSTRUCTION`** and carries **43 `PLACEHOLDER`** legend strings.

## Bottom line

The placement side of "make it fab ready" is **complete**: every real component
is on the board with a valid position and rotation. The remaining work to reach
a production release is **not** placement — it is schematic/netlist closure and
the placeholder/finish sign-offs tracked in `CLARIFICATION_DECISION_LOG.md` and
`FAB_READINESS_ASSESSMENT.md`.
