# LightRail AI Fab Readiness Status

Date: 2026-07-08

Repo commit reviewed: `a4a97ec`

## Verdict

Status: NOT READY FOR PRODUCTION FABRICATION OR ASSEMBLY RELEASE.

The current package is suitable for engineering reconciliation and manufacturer
discussion, but it is not a final fab-ready package. The blocking issue is
electrical completeness: the project does not yet contain authoritative
pin/ball/pad data or a complete schematic/netlist for the production design.

This is not a Gerber-format problem. It is a design-source problem.

## Release Gate Matrix

| Gate | Status | Evidence / reason |
| --- | --- | --- |
| Board outline / placement basis | Partial | Placement exists for the 82-part production subset, but several footprints are placeholders or package-inaccurate. |
| Gerbers / drill outputs | Review-only | Back-end geometry and Gerber generation exist, but Gerbers are not a production release without a complete validated netlist and final BOM. |
| Complete schematic | Blocked | Current schematic/netlist is an architectural scaffold, not a pin-complete source of electrical truth. |
| ERC clean | Blocked | ERC-clean capture requires the complete schematic and correct pin data first. |
| PCB/schematic parity 0 | Blocked | Parity cannot be closed until the schematic and PCB share the same authoritative netlist. |
| Final BOM / AVL | Blocked | Several parts are placeholders or need validation; HMC8410 is a confirmed function/package mismatch for the stated RF-front-end use. |
| Distributor stock / lifecycle | Not verified | DigiKey, Mouser, and element14 API credentials are not available in this session, so stock, lead time, pricing, and lifecycle cannot be marked verified. |
| NCE BGA-2500 pinout | Blocked | Owner-approved ball map, voltage-bank table, orientation, NC pins, and escape constraints are missing. |
| HBM4 stack pinout | Blocked | Exact orderable MPN, vendor package ball map, and NCE-to-HBM channel assignment are missing. |
| TFLN PIC/module pad map | Blocked | RF, bias, heater, monitor, ground/shield, optical orientation, and package pad map are missing. |
| Power tree / sequencing | Blocked | Rail voltages, current budgets, phase map, PMBus/I2C map, enables, PG, sequencing, and telemetry are not fully specified. |
| PCIe / fabric / clock lane map | Blocked | Lane order, polarity, reference clocks, resets, sideband signals, and retimer/switch assignments are not fully specified. |
| DRC / DFM / DFA signoff | Pending | Meaningful signoff comes after pin-complete capture, parity closure, final routing, planes, and production BOM. |

## What Has Been Fixed / Clarified

1. Added `09_pin_complete_data/` with:
   - four-item pin-data resolution matrix,
   - public datasheet/source manifest,
   - 82-part production inventory,
   - engineering data request,
   - step-01 pin-completion status.

2. Removed the old reference-board wording from the current repo files and
   replaced it with a LightRail-only engineering-basis note.

3. Identified a concrete part-level correction:
   - Current design use: HMC8410 represented as a high-speed RF driver placeholder.
   - Official datasheet reality: HMC8410 is a 6-lead, 2 mm x 2 mm LFCSP low-noise amplifier.
   - Required fix: choose the real TFLN RF driver/amp/modulator-interface part, then update symbol, footprint, BOM, and nets.

4. Confirmed the immediate path:
   - resolve authoritative pin data,
   - capture hierarchical KiCad schematic,
   - run ERC clean,
   - back-annotate to parity 0,
   - choose layer/stackup from real routing needs,
   - route, pour planes, regenerate Gerbers,
   - run final DRC/DFM/DFA and BOM/AVL validation.

## What I Can Still Fix Without External Design Data

These are useful, but they will not make the board fab-ready by themselves:

1. Normalize known public-part footprints where datasheets are available.
2. Build a hierarchical schematic skeleton with explicit blocked sheets.
3. Add/clean BOM fields for known public parts.
4. Add manufacturing notes, revision fields, stackup draft, fiducials, and silk cleanup.
5. Prepare manufacturer-facing transmittal wording and data-request forms.
6. Run DigiKey/Mouser/element14 lifecycle and stock validation after API
   credentials or distributor reports are supplied.

## What I Cannot Honestly Fix Without Your Engineering Data

These items are the hard limitations:

1. I cannot invent the LightRail NCE BGA-2500 ball map.
2. I cannot infer the HBM4 vendor ball map or channel assignment.
3. I cannot infer the TFLN PIC/module pad map or RF/bias/heater/monitor interface.
4. I cannot know the intended PCIe/fabric lane map, clock plan, reset plan, or power sequencing without the system architecture table.
5. I cannot produce a final procurement BOM while placeholder/wrong-function parts remain unresolved.
6. I cannot certify live distributor stock, lifecycle, lead time, or pricing
   without distributor API credentials or a current supplier quote/report.

If these inputs do not already exist, then achieving fab readiness requires
actual schematic and PCB engineering work from design intent, not file repair.

## Manufacturer-Facing Status

The current LightRail AI package is under engineering reconciliation. Final
Gerbers and final BOM will be released only after the pin-complete schematic,
PCB parity, part validation, and DFM/DFA checks are closed.

The next required deliverable is the authoritative design-source package:

- NCE BGA-2500 ball map,
- HBM4 package ball/channel map,
- TFLN module pad map,
- rail/lane/clock/reset allocation tables,
- corrected RF-front-end MPN and datasheet.

Once those are supplied, the board can move from engineering scaffold to
fab-ready release work.
