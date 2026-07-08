# Netlist Status — the definitive answer to "what do we need for fab-ready"

I extracted the connectivity directly from the reconciled board
(`kicad_pcb` pad → net walk, board-only reference geometry excluded). This is the
authoritative picture of the board's *electrical* state, independent of the
schematic.

## The finding

**Only 3 of the 82 production components carry any net. The other 79 are
completely unconnected.**

| Metric | Value |
| --- | ---: |
| Production components (BOM) | 82 |
| …with ≥1 net-assigned pad | **3** (U1, U3, U4) |
| …with **zero** nets | **79** |
| Pads on production components | 686 |
| …net-assigned | 212 |
| …unconnected (net 0) | **474 (69%)** |
| Functional nets among production parts | **64** |

### What connectivity *does* exist

The entire functional netlist is two bundles:

```
U1 (NCE Gen3) ──32 nets (L_TFLN_CTRL_xx)── U3 (TFLN PIC) ──32 nets── U4 (NCE Gen3)
```

That is the NCE ↔ TFLN photonic control interface only. Even there, U1/U4 are
74/174 pins netted and U3 is 64/82 — roughly half-wired. See
`netlist_extracted_real.csv` and `netlist_connectivity_graph.png`.

### What is entirely missing (0 nets)

- **Power delivery** — 24× ISL99390 stages, 4× ISL69260, 4× ADP7118 LDOs: no rails.
- **Memory** — all 12× HBM4 (U30–U35, U40–U45): no data/command/power.
- **Host / fabric** — 4× PCIe x16 (J20–J23), 4× PEX88096 switches, 4× BCM84881 retimers.
- **Clocking** — 2× Si5395A.
- **Management** — AST2600 BMC (U380).
- **Decoupling** — all 16× 100 nF (C1–C16).
- Several footprints (e.g. U200, U210, U380) have **0 pads at all** — they are
  empty placeholder outlines, not real land patterns.

## Why this is the gate — and why it can't be auto-generated

A netlist is a statement of *design intent*: which ball of the NCE BGA-2500
connects to which HBM4 ball, which power stage feeds which rail, how the PCIe
lanes map to the retimers. **That information does not exist anywhere in this
repository** — not in the schematic (a 2,310-line stub, 43 wires), not in any
zip, not on the PCB pads. It cannot be inferred, extracted, or synthesized,
because there is nothing to infer it from. It has to be *designed*.

No tool — KiCad, kicad-happy, or otherwise — can invent it without corrupting the
design. Fabricating connections would produce a board that is electrically wrong,
which is worse than one that is honestly incomplete.

## So, concretely, what we need for fab-ready

1. **The electrical design.** A complete schematic that connects all 82
   components — power tree, HBM interfaces, PCIe/host, clocking, management,
   decoupling — captured from the real design intent (or an existing design
   database if one exists outside this repo). This closes steps 1 & 4 and is the
   prerequisite for everything below. *(Owner: engineering / design source.)*
2. **Constrained routing + planes** once the netlist exists — route the ~hundreds
   of real nets across 4 layers, pour GND/Power planes, add vias. *(SI-aware P&R.)*
3. **Real footprints** for the placeholder parts that currently have 0 pads.
4. Then the mechanical items I can prepare in parallel (stackup + ENIG finish,
   fiducials, test points, silk fixes) become meaningful, and DRC/parity/DFM can
   be driven to green.

## Bottom line

The back end (placement, DRC-clean geometry, Gerber generation) is real and done.
The **front-end electrical design is ~96% absent** (79/82 parts unconnected). This
board is a *reference reconstruction*; turning it into a fabricable product is a
board-design effort, not a file or tooling fix. The netlist I extracted here is
the honest starting inventory for that effort.
