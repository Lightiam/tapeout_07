# Post-Cleanup Gerber/Drill Export Manifest

Export date: 2026-07-07  
KiCad CLI: 10.0.3  
Source board: `00_OPEN_IN_KICAD_PATCHED/TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pcb`

## Export Package

- Directory: `01_GERBERS_AFTER_NON_NETLIST_CLEANUP/`
- Zip: `TFLN_AI_NODE_X2_AFTER_NON_NETLIST_CLEANUP_GERBER_DRILL.zip`

## Exported Layers

- `F.Cu`
- `In1.Cu`
- `In2.Cu`
- `B.Cu`
- `F.Paste`
- `B.Paste`
- `F.SilkS`
- `B.SilkS`
- `F.Mask`
- `B.Mask`
- `Edge.Cuts`
- `F.Fab`
- `B.Fab`

## Validation Status

`after_non_netlist_fab_readiness_drc.json` reports 0 DRC errors, 0 unconnected items, 82 DRC warnings, and 214 schematic-parity warnings.

This export reflects the non-netlist manufacturability cleanup: stackup metadata, ENIG finish metadata, fiducials, project-local footprint libraries, and silkscreen cleanup. It does not replace the missing complete schematic/netlist source required to close electrical parity.
