# Tapeout 07

Controlled repository upload for the Tapeout July_04 work performed so far.

## Start Here

For the manufacturer's current request, use only:

- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip`
- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_BOM.xlsx`

Those are the controlled Step 01 Gerber/BOM review files. The Gerber zip has been refreshed from the post-cleanup KiCad export, and the BOM workbook has been updated to remove stale caution wording, old DRC counts, and old mechanical-reference wording.

## Other Folders

- `01_full_template_outputs`: full template-output package and indexes.
- `02_do_over_vlsi_flow`: VLSI/PCB do-over flow package and response docs.
- `03_schematic_transmittal`: schematic transmittal package and clear dual-NCE/TFLN overview.
- `04_rebuild_eco_required`: reference-envelope rebuild package requiring engineering ECO closure.
- `05_manufacturer_messages`: sendable manufacturer messages and clarification questions.
- `06_engineering_notes`: ECO candidate traceability evidence.
- `07_engineering_reconcile`: latest patched KiCad source and KiCad validation delta.
- `08_fab_release`: fabrication-readiness package — placement audit, fab notes, drill/centroid data, decision log, and release gate. **Start here for fab status.**
- `99_generation_scripts`: scripts used to generate/assemble these artifacts.

## Engineering Status

Current validated status as of 2026-07-07:

- The repo does not contain a complete design-source schematic or external netlist. The checked KiCad schematic is a connectivity stub: 2,311 lines, 28 wire objects, 82 schematic symbols, and 0 explicit net entries.
- Non-netlist manufacturability cleanup has been applied in `07_engineering_reconcile/00_OPEN_IN_KICAD_PATCHED/`: 4-layer High-Tg FR4 review stackup, ENIG finish metadata, six board-only fiducials, project-local footprint libraries, and silkscreen cleanup.
- The Step 01 BOM workbook now carries current review/signoff language and current validation counts instead of the earlier stale status wording.
- `07_engineering_reconcile/after_non_netlist_fab_readiness_drc.json` reports 0 DRC errors, 0 unconnected items, 82 DRC warnings, and 214 schematic-parity warnings.
- The 82 remaining DRC warnings are all `lib_footprint_mismatch`. The 214 schematic-parity warnings require a real schematic/netlist source and cannot be closed by file cleanup alone.

Post-cleanup Gerber/drill engineering-review export:

- `07_engineering_reconcile/TFLN_AI_NODE_X2_AFTER_NON_NETLIST_CLEANUP_GERBER_DRILL.zip`

## Fabrication Readiness

The `08_fab_release/` package from the remote branch remains in the repo as the fabrication-readiness evidence package: placement audit, fab notes, drill/centroid data, decision log, and release gate. Treat it together with `07_engineering_reconcile/`: production approval still depends on complete schematic/netlist source, parity closure or signed waiver, BOM owner signoff, chassis/mechanical signoff, and manufacturer DFM/DFA closure.
