# Missing Fab Data Risk and Request Prompts

Date: 2026-07-08

Purpose: explain why the missing files matter and provide paste-ready requests
for the design owner, package partners, memory vendor, and photonics vendor.

## Why These Missing Files Matter

These are not paperwork gaps. Each missing item gates a specific physical or
electrical risk.

| Missing item | Why it matters | Risk if guessed |
| --- | --- | --- |
| NCE BGA-2500 ball map | Defines ball name, signal, direction, voltage bank, ground, power, NC status, pair mapping, and package orientation. | Incorrect routing, rail-to-signal shorts, wrong voltage-bank assignment, or unusable BGA escape. |
| HBM4 package ball/channel map | Defines vendor-specific channel and pseudo-channel assignment, power pins, reference clocks, reset/training/control pins, and stack mechanicals. | Memory interface failure, signal-integrity violation, or memory-controller bring-up failure. |
| TFLN PIC/module pad map | Defines RF, bias, heater, monitor, ground/shield, optical orientation, and handling constraints. | RF/bias pad swap, optical die overdrive, damaged modulator, or untestable photonic path. |
| Rail/lane/clock/reset allocation | Defines power sequencing, clock dependencies, sideband buses, debug access, and lane mapping. | Board may power but never boot, or may be impossible to debug after assembly. |
| Corrected RF-front-end MPN | The current HMC8410 placeholder does not match the stated RF-front-end function/package. | Final BOM may order an unusable part and force board rework/redesign. |
| Final BOM/AVL and lifecycle check | Confirms parts are orderable, active, stocked, and acceptable for assembly. | Procurement delay, EOL parts, unavailable alternates, or assembly quote rejection. |

Gerbers describe geometry. They do not prove electrical intent. A fabricator can
manufacture a geometrically valid board whose pinout or BOM is electrically
wrong. The readiness gate exists to catch that error before NRE, lead time, and
prototype cost are spent.

## Request 1: NCE BGA-2500 Ball Map

Send to: ASIC/package design partner, OSAT, or internal package owner.

```text
We need the authoritative ball map for the LightRail NCE BGA-2500 package
used as U1/U4 on TFLN_AI_NODE_X2.

Please provide:
- ball name,
- signal name,
- direction: input, output, bidirectional, power, ground, or NC,
- IO standard,
- voltage bank,
- differential pair mate where applicable,
- package orientation marker and A1 location,
- reserved/service balls,
- escape-routing constraints including pitch, via-in-pad requirements, and keepouts.

We are finalizing schematic capture and cannot route or close PCB/schematic
parity without this source data.
```

## Request 2: HBM4 Package and Channel Map

Send to: HBM4 memory vendor under NDA.

```text
We are integrating HBM4 into a custom LightRail AI accelerator board.

Please provide the exact orderable MPN and, under NDA if required:
- vendor package ball map,
- stack height and package drawing,
- channel and pseudo-channel assignment,
- power rail requirements,
- reference clock inputs,
- reset, training, and control pins,
- sequencing requirements,
- recommended escape or interposer constraints.

We need this to complete NCE-to-HBM channel assignment before schematic signoff.
```

## Request 3: TFLN PIC/Module Pad Map

Send to: TFLN photonics foundry/module vendor.

```text
For the TFLN PIC/module used as U3 in TFLN_AI_NODE_X2, please provide the
authoritative package pad map.

Required fields:
- pad number/name,
- function,
- direction,
- RF impedance target,
- bias voltage/current range and polarity,
- heater pins,
- monitor pins,
- ground/shield pin assignment,
- optical port orientation,
- package mechanical drawing,
- ESD and handling limits.

This gates RF-front-end part selection, bias architecture, PCB stackup, and
schematic signoff.
```

## Request 4: Internal Rail, Lane, Clock, and Reset Allocation

Send to: internal system architect or design owner.

```text
Please define the complete power, clock, reset, and lane architecture for
TFLN_AI_NODE_X2.

Output as tables keyed by final net name:

1. Power tree:
   - every rail name,
   - voltage,
   - typical and maximum current,
   - source regulator,
   - VRM phase count,
   - PMBus/I2C address,
   - enable and power-good dependencies.

2. PCIe/fabric lane map:
   - source device and pin/ball,
   - destination device and pin/ball,
   - lane number,
   - polarity,
   - reference clock source,
   - retimer or switch path.

3. Clock plan:
   - clock source,
   - destination,
   - frequency,
   - voltage level,
   - jitter requirement,
   - enable/reset dependency.

4. Reset and boot:
   - power-up order,
   - PG-to-reset dependencies,
   - boot strap states,
   - JTAG/debug header pinout,
   - test point list.

This table will be used directly for hierarchical KiCad schematic capture.
```

## Request 5: Correct RF-Front-End Part Selection

Send to: electrical engineering/component selection owner.

```text
The current BOM uses HMC8410 as a placeholder for the TFLN RF driver or
modulator interface, but the HMC8410 datasheet identifies it as a 6-lead
2 mm x 2 mm LFCSP low-noise amplifier. This is the wrong function/package
for the stated placeholder role.

Please propose 2-3 candidate RF driver, amplifier, or modulator-interface
parts suitable for the TFLN interface. For each candidate, provide:
- MPN,
- manufacturer,
- datasheet link,
- bandwidth,
- output swing or drive capability,
- supply rails,
- package,
- lifecycle status,
- stock or quote status,
- why it fits the TFLN interface.

After approval, update symbol, footprint, BOM, and schematic nets.
```

## Request 6: Distributor Lifecycle and Stock Verification

Send to: sourcing/procurement owner or run after API credentials are available.

```text
Please provide current distributor verification for the 82-part production BOM:
- stock,
- lifecycle status,
- lead time,
- unit price at prototype and production quantities,
- minimum order quantity,
- acceptable alternates,
- assembly-house approved vendor list status.

If using DigiKey/Mouser/element14 APIs, provide credentials or a current export
so the lifecycle and AVL status can be updated in 10_fab_readiness/.
```

## Optional Drafting Aid

Use this only to create a review template. It is not authoritative design data.

```text
Generate a draft, clearly marked non-authoritative, for the BGA-2500 ball-map
matrix and rail/lane/clock/reset allocation table. Mark every assumed field
as ASSUMED so engineering can review and replace it with vendor-approved data.
```

