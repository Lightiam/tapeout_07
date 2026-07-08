# Release Gate Checklist

Single-page go/no-go for `TFLN_AI_NODE_X2_SERVER_CHASSIS_IO`.
Status legend: ✅ met · ⚠️ conditional / documented · ⛔ blocking.

## Design / electrical

| # | Gate item | Status | Note |
| --- | --- | :---: | --- |
| 1 | All components placed on PCB | ✅ | 82/82 netlisted parts placed (audit) |
| 2 | DRC errors = 0 | ✅ | reconciled KiCad source |
| 3 | Unconnected items = 0 | ✅ | reconciled KiCad source |
| 4 | Schematic parity = 0 | ⛔ | 214 warnings (148 net_conflict + 66 extra_footprint) |
| 5 | DRC warnings cleared | ⚠️ | 88 warnings (82 library + 6 silk_over_copper), non-fatal |
| 6 | Reference-reconstruction status cleared | ⛔ | board still marked REFERENCE RECONSTRUCTION / PLACEHOLDER |

## Fabrication data

| # | Gate item | Status | Note |
| --- | --- | :---: | --- |
| 7 | Complete Gerber layer set | ✅ | 4 cu + masks + pastes + silks + edge + drill + job |
| 8 | NC drill valid | ✅ | 5 tools / 260 holes / plating attributed |
| 9 | Board revision set | ⚠️ | was `rev?`; corrected job = `X2-ENG-A` (bump for production) |
| 10 | Surface finish specified | ⚠️ | was `None`; corrected job = ENIG (needs sign-off) |
| 11 | Controlled-impedance stackup defined | ⛔ | not specified; required for RF/PCIe/retimer nets |
| 12 | Fab drawing / drill map PDF | ⛔ | not in drop; regenerate from KiCad |
| 13 | Bare-board test netlist (IPC-D-356) | ⛔ | not in drop; regenerate from KiCad |

## Assembly

| # | Gate item | Status | Note |
| --- | --- | :---: | --- |
| 14 | Centroid / pick-and-place file | ✅ | `data/centroid_pick_and_place.csv` (82 parts) |
| 15 | BOM MPN coverage | ✅ | 0 missing MPNs |
| 16 | BOM status sheets current | ⛔ | workbook still shows pre-reconciliation numbers (Q-F) |
| 17 | Placeholder populate/DNP resolved | ⛔ | pending Q-A sign-off |
| 18 | Mounting-hole clearance (MH5) confirmed | ⛔ | pending Q-C mechanical sign-off |

## Overall gate

**⛔ NOT RELEASED for production fabrication.** Placement and DRC-error gates are
green and the fabrication-data package is documentation-complete, but items
4, 6, 11, 12, 13, 16, 17, 18 are open. All are bounded engineering tasks — see
`FAB_READINESS_ASSESSMENT.md` §5 for the ordered path to close them.
