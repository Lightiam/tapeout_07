# Tapeout 07

Controlled repository upload for the Tapeout July_04 work performed so far.

## Start Here

For the manufacturer's current request, use only:

- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip`
- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_BOM.xlsx`

Those are the focused Step 01 Gerber/BOM review files.

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

The latest KiCad check reports 0 DRC errors and 0 unconnected items after the regulator-placeholder geometry fix. Remaining warnings and schematic parity items are documented in `07_engineering_reconcile/ENGINEERING_FIX_SUMMARY.md`.

## Fabrication Readiness

All 82 netlisted components are placed on the PCB and the reconciled KiCad check
reports 0 DRC errors / 0 unconnected items. The board is still an explicit
**REFERENCE RECONSTRUCTION** with 214 schematic-parity warnings, so it is
**not yet released for production fabrication**. The full, evidence-backed
assessment, the exact bounded items required to reach a FAB-READY release, and
the supporting manufacturing data (centroid/pick-and-place, drill report,
placement map, corrected Gerber job file with revision + ENIG finish) are in
`08_fab_release/`. See `08_fab_release/RELEASE_GATE_CHECKLIST.md` for the
one-page go/no-go.
