# Engineering Data Request

Please provide the following final, authoritative data so the LightRail AI board can be promoted from v0.1 placeholder state to pin-complete schematic capture.

## Required files

1. NCE BGA-2500 ball map for U1 and U4.
   - Ball name, signal name, direction, IO standard, voltage bank, power/ground/NC status, differential pair mate, package orientation, and escape constraints.

2. HBM4 stack package data for U30-U35 and U40-U45.
   - Exact orderable MPN, vendor package drawing, stack height, ball map, channel map, power rails, reference clocks, reset/training/control pins, and NCE-to-HBM channel assignment.

3. TFLN PIC/module data for U3.
   - Pad number/name, function, RF impedance, bias range/polarity, heater/monitor pins, ground/shield pins, optical orientation, package drawing, and ESD/handling constraints.

4. System allocation tables.
   - Power tree with voltages and current budgets.
   - VRM phase map and PMBus/I2C addresses.
   - PCIe/fabric lane map.
   - Clock output plan.
   - Reset, boot strap, JTAG/debug, and test point map.
   - Populate/DNP options.

5. Corrected TFLN RF front-end part selection.
   - The current HMC8410 placeholder does not match the required function/package. Please provide the intended driver/amp/modulator interface IC MPN and datasheet.

## Why this is needed

The current package has placements and partial placeholder nets, but not enough pin-level electrical intent to create an ERC-clean schematic or a parity-0 PCB. These files are required before routing, stackup selection, and final Gerber regeneration can be treated as production work.

