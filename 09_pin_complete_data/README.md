# Step 01 Pin-Complete Data Resolution

This folder is the controlled output for sequential step (1): resolve the data needed to promote the current LightRail AI v0.1 package to a pin-complete design basis before schematic capture.

## Result

Step (1) is started, but v0.1 is not pin-complete yet.

The blocker is not formatting. The blocker is missing authoritative pin/ball/pad data for the custom and vendor-controlled devices that define the electrical design:

1. Dual LightRail NCE BGA-2500 devices.
2. Twelve HBM4 stack placements.
3. TFLN photonic PIC/module.
4. System interconnect and rail assignment between NCE, HBM, PCIe/fabric, clocks, BMC, retimers, and regulators.

Public datasheets resolve only some support parts. They do not resolve the NCE/HBM/TFLN pin-level connectivity.

## Files

- `pin_data_resolution_matrix.csv` - the four required data items, current status, and the exact engineering input needed.
- `datasheet_source_manifest.csv` - public/vendor source manifest used during this step.
- `production_82_pin_data_inventory.csv` - the 82 production placements cross-checked against the current PCB analyzer output.
- `mpn_inventory_from_pcb.csv` - raw PCB MPN extraction from the analyzer, including broader placeholders/service objects.
- `STEP_01_PIN_COMPLETION_STATUS.md` - engineer-facing status and handoff instructions.
- `ENGINEERING_DATA_REQUEST.md` - concise request that can be sent to the design owner/vendor team.

## Engineering decision

Do not proceed to hierarchical schematic capture as if the design is pin-complete. Capture can start only as a skeleton hierarchy until the blocked pin/ball/pad data is supplied.

The highest-risk correction found in public sourcing is the HMC8410 entry. The current PCB/BOM describes and footprints it as a high-speed driver placeholder, but the Analog Devices datasheet identifies HMC8410 as a 6-lead, 2 mm x 2 mm LFCSP low-noise amplifier. That must be corrected before schematic capture.

