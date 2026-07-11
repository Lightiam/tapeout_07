# Production Fab Roadmap

This folder is the real-world path from the current engineering scaffold to an
actual, working prototype board. It exists because the electrical blockers in
[`10_fab_readiness/FAB_READINESS_STATUS_2026-07-08.md`](../10_fab_readiness/FAB_READINESS_STATUS_2026-07-08.md)
are not file-formatting problems — they are missing design-source data that
only the IP owner or specific component vendors can supply.

Start here:

- [`PART_SOURCING_DECISIONS_2026-07-10.md`](./PART_SOURCING_DECISIONS_2026-07-10.md) —
  what real parts are targeted for each blocked component, and why.
- [`CODEX_PROMPT_LOCK_LAYOUT.md`](./CODEX_PROMPT_LOCK_LAYOUT.md) — a single,
  ready-to-run agent prompt that locks the existing `TFLN_AI_NODE_X2_REFERENCE`
  layout with zero deviation and resolves the sourcing gaps above without
  inventing proprietary IP.

## Ground rule carried over from `10_fab_readiness/`

The NCE BGA-2500 ball map is LightRail's own proprietary IP for a chip that
has not been taped out. No agent may mark it "final" — it must always be
generated and tagged as a draft pending explicit IP-owner signoff until the
real map is supplied. Every other blocker (HBM4, TFLN PIC, HMC8410) has a
real, named, sourceable path and does not require invented data.
