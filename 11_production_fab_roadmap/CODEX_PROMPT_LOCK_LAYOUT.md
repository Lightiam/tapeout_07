# Codex / Claude Code Prompt — Lock Layout, Resolve Sourcing

Paste the block below into your coding agent session on this repo. It locks
the existing reference layout with zero deviation and resolves the sourcing
gaps in [`PART_SOURCING_DECISIONS_2026-07-10.md`](./PART_SOURCING_DECISIONS_2026-07-10.md)
without inventing proprietary IP for the NCE ASIC.

---

```
Lock TFLN_AI_NODE_X2_REFERENCE.kicad_pcb as the final physical layout for the
LightRail AI NCE prototype board. Do not change placement, footprint outlines,
or topology from this file — zero deviation from this layout. Make every
component and net in it electrically real/complete using these decisions:

1. NCE compute die (U1/U4, BGA-2500 footprint):
   This is LightRail's own NCE ASIC, not yet taped out — no vendor ball map
   exists. Do NOT invent a "final" map. Instead generate a DRAFT ball map
   derived from the known architecture (22-layer stack: HBM4 channels,
   TFLN/optical SerDes lanes, PCIe/fabric lanes, power/ground per BGA-2500
   JEDEC-style grid conventions). Tag every ball "DRAFT - PENDING IP OWNER
   SIGNOFF" in BOM/schematic notes. Output as an editable table (ball, signal,
   bank, voltage, direction) for owner review before it's ever treated as final.

2. HBM4 (U30-U35, U40-U45):
   Real HBM4 (Samsung/SK hynix/Micron) is hyperscaler-allocated through 2026
   and not available in small quantities. Populate footprints with HBM3E as a
   pin-compatible prototype substitute, tagged "SUBSTITUTE PENDING HBM4
   ALLOCATION" in the BOM. Pull the real HBM3E vendor ball/channel map for the
   exact MPN used and update footprints to match it precisely.

3. TFLN PIC module (U3):
   Target HyperLight as primary source (mature commercial TFLN modulator/
   driver products). Pull their datasheet pad map for the specific module SKU
   and update the footprint/pinout to match. If HyperLight can't support
   small-quantity sampling, fall back to Ligentec/CSEM (custom PIC foundry
   run) or POET Technologies (photonic interposer).

4. Rail/lane/clock/reset allocation:
   Derive the full power tree, PCIe/fabric lane map, clock plan, and reset/
   sequencing table consistent with the draft NCE map and the real HBM3E/TFLN
   pinouts. Tag this DRAFT too, pending IP owner signoff.

5. HMC8410 correction:
   Replace with a real TFLN driver/modulator-interface part (search Analog
   Devices/MACOM for correct bandwidth/voltage-swing/package match), update
   symbol/footprint/BOM.

6. Finish:
   Re-capture the schematic net-by-net so every pin has a real or clearly-
   tagged-draft connection. Run ERC to clean or list remaining draft-dependent
   warnings explicitly. Back-annotate to PCB parity 0 against the locked
   layout. Regenerate DRC/DFM report and final BOM/AVL, separating REAL/
   VERIFIED parts from DRAFT/PENDING SIGNOFF parts. Do not mark the board
   fab-ready in any status file until the NCE ball map row changes from DRAFT
   to IP-owner-approved.
```
