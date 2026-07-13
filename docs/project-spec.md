# Project Specification: LightRail Tapeout 07 (LPO MVP & LR-P3A Rev 6.3)

## Overview
This project specification documents the architecture, parameters, and physical/electrical constraints for the **LightRail Tapeout 07** release. The project consists of two distinct boards:
1. **LightRail LPO MVP**: A high-speed optoelectronic transceiver prototype.
2. **LR-P3A Rev 6.3**: A complex 16-layer processor host board containing dual custom 2500-pin BGAs and Silicon Photonics (SiPh) interposers.

---

## Requirements Summary

| Category | LightRail LPO MVP | LR-P3A Rev 6.3 |
|----------|-------------------|----------------|
| **Power Input** | external 5V/12V DC input | DC Barrel Jack & Power Header |
| **Voltage Rails** | 3.3V, 1.8V | 12V, 5V, 3.3V, 1.8V, 0.8V (Core) |
| **MCU/Processor** | None (pure transceiver) | 2× Custom 2500-pin processor BGAs |
| **Connectivity** | 4× SMA Coaxial RF Connect Connectors, Optical | JTAG, high-speed digital escape lines, Optical |
| **Layer Count** | 2 Layers | 16 Layers |
| **Dimensions** | 295.00 mm × 140.00 mm | 295.00 mm × 140.00 mm |

---

## Detailed Requirements

### 1. Power Architecture
* **LightRail LPO MVP**: 
  * Powered via input connectors.
  * Local rails are regulated via high-efficiency low-noise LDOs to avoid interference with sensitive analog optoelectronics.
* **LR-P3A Rev 6.3**: 
  * High-current switching regulators (buck topology) are used for the main core rails (e.g. 0.8V Core, 1.8V).
  * Multi-layer power plane routing used to support HBM memory power loops and high transient processor current.

### 2. Physical Layout & Mechanical Constraints
* **Envelope Size**: 295.00 mm × 140.00 mm (standardized envelope size).
* **Mounting Holes**: M3 standard mechanical mounting holes (3.2 mm diameter).
  * LPO MVP: 4 holes.
  * LR-P3A: 8 holes (4 holes arranged in a 50mm grid around each BGA socket).
* **Fiducials**: 3× surface copper fiducial markers (1.0 mm pad, 2.0 mm mask clearance) on F.Cu layer for pick-and-place alignment.

### 3. High-Speed Interface & Stackup
* **LPO MVP (2-layer)**: High-speed differential RF traces (e.g., `RF_OUT_P/N`) routed on the F.Cu layer with ground reference planes on B.Cu.
* **LR-P3A (16-layer)**: Implements complex impedance-controlled differential striplines and microstrips. Standard stackup layers:
  * Signal Layers: F.Cu, B.Cu, and 14 internal signal/plane copper layers (`In1.Cu` through `In14.Cu`).
  * Total thickness: 2.4 mm to accommodate fine-pitch BGA via aspect ratios.

---

## Constraints

* **Manufacturing Standards**: IPC-7351 pick-and-place fiducial rules.
* **Assembly Type**: Turnkey SMT reflow for BGAs and fine-pitch components; selective hand assembly for SMA edge launch.
* **Plating Finish**: ENIG or ENEPIG (essential for optical wire bonding and high-speed BGA alignment).

---

## Open Questions
* **None**: All design-rule checks (DRC), electrical-rule checks (ERC), and manufacturing plotting checks are verified as **PASS**.
