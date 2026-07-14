# LightRail LPO MVP — Manufacturing & Production Package

This package contains the complete manufacturing and SMT assembly deliverables for the **LightRail LPO MVP** board.

## Package Contents

1. **BOM.csv** — Bill of Materials with Designators, Manufacturer Part Numbers (MPNs), Values, Footprints, and Quantities.
2. **CPL.csv** — Component Placement List (Centroid / XY file) containing designator coordinates (X/Y mm, rotation, board layer).
3. **Assembly_Top.svg** — Top-side SMT assembly placement drawing.
4. **Assembly_Bottom.svg** — Bottom-side SMT assembly placement drawing.
5. **KiCad Source Files** — Full PCB design source:
   - `LightRail_LPO_MVP.kicad_pro` (KiCad Project file)
   - `LightRail_LPO_MVP.kicad_sch` (KiCad Schematic file)
   - `LightRail_LPO_MVP.kicad_pcb` (KiCad PCB Layout file)

## Gerber Export Instructions

Gerber plot parameters are pre-configured inside the `LightRail_LPO_MVP.kicad_pcb` source file for automatic plotting. To export:
1. Open `LightRail_LPO_MVP.kicad_pcb` in KiCad Layout Editor.
2. Go to **File → Plot...** (or click the Plot icon).
3. Verify the Output Directory is set to `gerbers/`.
4. Click **Plot** to generate Gerber layers (Copper, Mask, Silk, Paste, Edge.Cuts).
5. Click **Generate Drill Files...** and click **Generate Drill File** to export Excellon drill data.
