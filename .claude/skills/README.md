# Vendored Claude Code skills — kicad-happy

This directory vendors the **kicad-happy** skill collection so that every Claude
Code / Claude-on-web session working on this repository has the KiCad design,
review, sourcing, and manufacturing-prep skills available automatically (the
container is cloned fresh each session, so the skills are committed here rather
than installed at runtime).

| | |
| --- | --- |
| Upstream | https://github.com/aklofas/kicad-happy |
| Version vendored | 1.3.2 |
| License | MIT — see `LICENSE.kicad-happy` |
| Added | 2026-07-08 |

## Skills included

`kicad` (schematic/PCB/Gerber/DRC/DFM analysis), `bom`, `spice`, `emc`,
`datasheets`, `digikey`, `mouser`, `lcsc`, `element14`, `jlcpcb`, `pcbway`,
`kidoc`. Each is a self-contained directory with a `SKILL.md` and pure-Python
`scripts/` (no external dependencies, Python 3.10+).

## Direct use (no skill runtime required)

The analysis scripts can be run directly, e.g.:

```
python3 .claude/skills/kicad/scripts/analyze_pcb.py <board.kicad_pcb> \
        --text --stage pre_fab --audience reviewer
python3 .claude/skills/kicad/scripts/analyze_schematic.py <sheet.kicad_sch> --text
```

A pre-fab review of this project's reconciled board was run with this skill; the
output is in `../../08_fab_release/analysis/` and its findings (fiducials,
test-point coverage) are folded into the fab-readiness gate.

## Updating

Re-vendor from upstream and bump the version above:

```
git clone --depth 1 https://github.com/aklofas/kicad-happy /tmp/kh
rm -rf .claude/skills/*/ && cp -r /tmp/kh/skills/* .claude/skills/
cp /tmp/kh/LICENSE .claude/skills/LICENSE.kicad-happy
```

Alternatively, install as a live plugin instead of vendoring:
`/plugin marketplace add aklofas/kicad-happy` then
`/plugin install kicad-happy@kicad-happy`.
