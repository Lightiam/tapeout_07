# LR-P3A Rev 6.3 — Manufacturing & Production Package

This package contains the complete manufacturing and SMT assembly deliverables for the **LR-P3A Rev 6.3** board.

## Package Contents

1. **BOM.csv** — Bill of Materials with Designators, Manufacturer Part Numbers (MPNs), Values, Footprints, and Quantities.
2. **CPL.csv** — Component Placement List (Centroid / XY file) containing designator coordinates (X/Y mm, rotation, board layer).
3. **Assembly_Top.svg** — Top-side SMT assembly placement drawing.
4. **Assembly_Bottom.svg** — Bottom-side SMT assembly placement drawing.
5. **KiCad Source Files** — Full PCB design source:
   - `LR_P3A_Rev6_3.kicad_pro` (KiCad Project file)
   - `LR_P3A_Rev6_3.kicad_sch` (KiCad Schematic file)
   - `LR_P3A_Rev6_3.kicad_pcb` (KiCad PCB Layout file)

## Gerber Export Instructions

Gerber plot parameters are pre-configured inside the `LR_P3A_Rev6_3.kicad_pcb` source file for automatic plotting. To export:
1. Open `LR_P3A_Rev6_3.kicad_pcb` in KiCad Layout Editor.
2. Go to **File → Plot...** (or click the Plot icon).
3. Verify the Output Directory is set to `gerbers/`.
4. Click **Plot** to generate Gerber layers (Copper, Mask, Silk, Paste, Edge.Cuts).
5. Click **Generate Drill Files...** and click **Generate Drill File** to export Excellon drill data.
