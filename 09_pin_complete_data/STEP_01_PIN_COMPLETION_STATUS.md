# Step 01 Pin-Completion Status

Status: BLOCKED on authoritative pin data.

Date: 2026-07-08

Scope: LightRail AI v0.1 pin-complete promotion before hierarchical KiCad schematic capture.

## Decision

Start with data resolution, not schematic capture.

Capturing the current files first would create a clean-looking hierarchy around incomplete electrical intent. The current repository has placements and partial placeholder connectivity, but it does not contain enough pin-level design data to produce ERC-clean, parity-0 schematic/PCB alignment.

## Evidence from current files

- Production placement subset: 82 parts from `08_fab_release/analysis/centroid_kicad9_netlisted.csv`.
- KiCad PCB analyzer summary: 380 nets, 0 unrouted nets, but this reflects the current placeholder/partial net structure, not a complete production schematic.
- Prior repo audit: only U1, U3, and U4 carry meaningful connectivity; 79 of 82 production components had no real netlist linkage.
- New production inventory: `production_82_pin_data_inventory.csv`.

## Critical fixes before capture

1. Replace the HMC8410 driver placeholder.
   - Current repo description/footprint: high-speed driver placeholder using QFN-32.
   - Official ADI datasheet: HMC8410 is a 6-lead 2 mm x 2 mm LFCSP low-noise amplifier.
   - Action: choose the real TFLN RF driver/amp MPN, then update symbol, footprint, BOM, and net intent.

2. Replace placeholder high-pin-count packages with real package definitions.
   - NCE named BGA-2500 parses as 174 pads in the current analyzer output.
   - HBM4 stack placements parse as 17 pads each.
   - Several support ICs use placeholder QFN-48 footprints where the public part information indicates other packages.
   - Action: install or generate package-accurate symbols/footprints from authoritative datasheets/ball maps.

3. Resolve custom/vendor pin data.
   - NCE BGA-2500: owner ball map and bank table.
   - HBM4: exact orderable MPN and package ball/channel map.
   - TFLN: module/PIC pad table and electro-optic interface.
   - System architecture: lane map, rail map, PMBus/I2C map, clocks, resets, debug/test points.

## Gate to step (2)

Step (2), hierarchical KiCad schematic capture, should start only after these artifacts are supplied:

- NCE ball map CSV/PDF.
- HBM4 vendor package ball map and channel assignment.
- TFLN module pad map and package drawing.
- Rail/lane/clock/reset/system allocation table.
- Corrected MPN for the TFLN RF front-end device currently represented by HMC8410 placeholders.

Once those are available, the next work package is:

1. Build hierarchical KiCad sheets for NCE, HBM, TFLN, power, clocks, BMC, PCIe/fabric, management, and connectors.
2. Run ERC until clean.
3. Back-annotate to PCB and drive schematic/PCB parity to 0.
4. Choose the layer target and impedance stackup from actual escape/routing requirements.
5. Route, pour planes, run DRC/DFM, and regenerate Gerbers.

