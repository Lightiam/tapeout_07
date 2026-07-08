# LightRail Netlist v0.1 Engineering Basis

This note documents the current LightRail AI v0.1 architectural netlist basis
and the remaining engineering inputs required to promote it to a pin-complete
KiCad schematic.

## 1. Current LightRail v0.1 Netlist Basis

Output artifacts:

- `lightrail_netlist.csv`
- `lightrail_netlist.json`
- `lightrail_netlist_architecture.png`

Current v0.1 status:

| Item | Before current netlist work | LightRail v0.1 |
| --- | ---: | ---: |
| Production components referenced | 3 / 82 | 82 / 82 |
| Nets | 64 partial nets | 155 architectural nets |
| Pin connections | 212 partial nodes | 594 architectural nodes |

The v0.1 netlist is an engineering scaffold. It is useful for organizing the
design into power, clocking, management, PCIe/fabric, NCE, HBM, and TFLN
subsystems, but it still needs authoritative pin/ball/pad data before it can be
treated as a production schematic source.

## 2. Defined Architectural Areas

- Power tree: `+12V_IN`, NCE core rails, HBM rails, RF/PLL LDO rails, and IO rails.
- Clocking: Si5395A reference, NCE clocks, HBM reference clocks, and PCIe reference clocks.
- TFLN control: NCE-to-TFLN control nets and RF front-end placeholders.
- PCIe/fabric: slot, switch, retimer, and NCE lane placeholders.
- Management: AST2600 sideband, PMBus/I2C, reset, and debug placeholders.
- Decoupling: C1-C16 assigned by rail intent.
- Global reference: all production components tied to a common ground intent.

## 3. Required Inputs Before Pin-Complete Capture

Each item below must be resolved against real device documentation or owner
design data:

1. HBM4 package ball map and NCE-to-HBM channel assignment.
2. LightRail NCE BGA-2500 ball map, voltage-bank table, and package orientation.
3. TFLN PIC/module pad map, RF/bias/heater/monitor pins, and package drawing.
4. PCIe/fabric lane map, including lane order, polarity, refclk, reset, and sideband mapping.
5. Corrected TFLN RF front-end MPN and package. The current HMC8410 placeholder
   does not match the required function/package.
6. Power tree details: rail voltages, current budget, VRM phase map, PMBus/I2C
   addresses, enables, power-good signals, sequencing, and telemetry.

## 4. Sequential Path

1. Resolve the required data items and promote v0.1 to a pin-complete netlist.
2. Capture the design as a hierarchical KiCad schematic and run ERC clean.
3. Back-annotate to the PCB and drive schematic/PCB parity to 0.
4. Choose the layer target and impedance stackup from actual routing/escape needs.
5. Route, pour planes, regenerate Gerbers/drill/IPC-netlist, and run DRC/DFM/DFA.

Engineering validation is required before production release.
