# Release Gate Checklist

Single-page engineering gate for `TFLN_AI_NODE_X2_SERVER_CHASSIS_IO`.
Status legend: met / review / open.

## Design / Electrical

| # | Gate item | Status | Note |
| --- | --- | :---: | --- |
| 1 | All components placed on PCB | met | 82/82 netlisted parts placed in the current audit. |
| 2 | DRC errors = 0 | met | KiCad validation reports 0 DRC errors. |
| 3 | Unconnected items = 0 | met | KiCad validation reports 0 unconnected items. |
| 4 | Schematic parity = 0 | open | 214 warnings remain: 148 net_conflict and 66 extra_footprint. |
| 5 | DRC warnings reviewed | review | 82 warnings remain, all library/footprint mismatch. |
| 6 | Reference-reconstruction status resolved | open | Complete schematic/netlist source is required for electrical closure. |

## Fabrication Data

| # | Gate item | Status | Note |
| --- | --- | :---: | --- |
| 7 | Complete Gerber layer set | met | 4 copper layers, masks, pastes, silks, edge, drill, and job file are present in the post-cleanup package. |
| 8 | NC drill valid | met | Drill file and drill report are included. |
| 9 | Board revision set | review | `July_04-ENG-RECONCILE-01` is set in the patched KiCad source. |
| 10 | Surface finish specified | review | ENIG metadata is set; manufacturer and engineering signoff still required. |
| 11 | Controlled-impedance stackup defined | review | 4-layer High-Tg FR4 review stackup is present; impedance targets need engineering/manufacturer confirmation. |
| 12 | Fab drawing / drill map PDF | met | Drill map PDF is included in the post-cleanup Gerber/drill export. |
| 13 | Bare-board test netlist | open | Regenerate after authoritative schematic/netlist import and parity closure. |

## Assembly

| # | Gate item | Status | Note |
| --- | --- | :---: | --- |
| 14 | Centroid / pick-and-place file | met | `data/centroid_pick_and_place.csv` is present in `08_fab_release`. |
| 15 | BOM MPN coverage | met | Current Step 01 BOM workbook reports 0 missing MPNs. |
| 16 | BOM status sheets current | met | Step 01 BOM workbook was updated with current DRC/parity counts and review/signoff wording. |
| 17 | Placeholder populate/DNP resolved | open | Requires named engineering signoff. |
| 18 | Mounting-hole and chassis constraints confirmed | open | Requires mechanical/chassis signoff. |
| 19 | Fiducials for pick-and-place | met | Six board-only fiducials were added in the patched KiCad source. |
| 20 | Test-point coverage | review | ICT/flying-probe strategy still requires engineering review. |

## Overall Gate

Production approval requires closure or signed waiver for schematic parity, placeholder disposition, chassis/mechanical constraints, stackup/impedance targets, BOM owner signoff, and manufacturer DFM/DFA review. See `FAB_READINESS_ASSESSMENT.md` and `07_engineering_reconcile/ENGINEERING_FIX_SUMMARY.md` for the detailed path.
