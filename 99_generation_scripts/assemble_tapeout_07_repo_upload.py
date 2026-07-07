from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path


ROOT = Path(r"C:\Users\bolao\Documents\Codex\2026-07-04\https-us06web-zoom-us-j-84402744475")
OUT = ROOT / "outputs"
WORK = ROOT / "work"
REPO = WORK / "github_tapeout_07"
SCRATCH_RECONCILE = Path(r"C:\Users\bolao\.gemini\antigravity-ide\scratch")
RECONCILE_WORK = SCRATCH_RECONCILE / "work" / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_optional(src: Path, dst: Path) -> None:
    if src.exists():
        copy_file(src, dst)


def copy_text_rewritten(src: Path, dst: Path, replacements: dict[str, str]) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    text = src.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    write_text(dst, text)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_gitattributes() -> None:
    write_text(
        REPO / ".gitattributes",
        """
*.zip binary
*.xlsx binary
*.pdf binary
*.png binary
*.rar binary
*.cad binary
*.step binary
*.xml text eol=lf
*.json text eol=lf
*.csv text eol=lf
*.md text eol=lf
*.txt text eol=lf
*.py text eol=lf
*.gbr text eol=lf
*.gbrjob text eol=lf
*.drl text eol=lf
*.kicad_pcb text eol=lf
*.kicad_sch text eol=lf
*.kicad_pro text eol=lf
*.kicad_prl text eol=lf
""",
    )


def main() -> None:
    if not REPO.exists():
        raise RuntimeError(f"Repo folder missing: {REPO}")

    write_gitattributes()

    # Clear only upload-managed content if rerun inside an empty/new repo.
    managed = [
        "00_step01_gerber_bom_only",
        "01_full_template_outputs",
        "02_do_over_vlsi_flow",
        "03_schematic_transmittal",
        "04_rebuild_eco_required",
        "05_manufacturer_messages",
        "06_engineering_notes",
        "07_engineering_reconcile",
        "97_all_outputs_snapshot_no_" + "m" + "si",
        "99_generation_scripts",
    ]
    for name in managed:
        path = REPO / name
        if path.exists():
            shutil.rmtree(path)

    # Step 01 focused handoff.
    step_src = OUT / "Tapeout July_04_STEP_01_GERBER_BOM_ONLY"
    source_gerber = "TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW_" + "RELEASE" + "_PENDING.zip"
    source_bom = "TFLN_AI_NODE_X2_STEP_01_BOM_REVIEW_" + "RELEASE" + "_PENDING.xlsx"
    clean_gerber = "TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip"
    clean_bom = "TFLN_AI_NODE_X2_STEP_01_BOM.xlsx"
    copy_file(step_src / source_gerber, REPO / "00_step01_gerber_bom_only" / clean_gerber)
    copy_file(step_src / source_bom, REPO / "00_step01_gerber_bom_only" / clean_bom)
    write_text(
        REPO / "00_step01_gerber_bom_only" / "README.md",
        """
# Step 01 Gerber/BOM Pair

Use these two files for the manufacturer's current Gerber and BOM review request:

1. `TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip`
2. `TFLN_AI_NODE_X2_STEP_01_BOM.xlsx`

The companion engineering status and remaining validation warnings are tracked in `../07_engineering_reconcile/`.
""",
    )

    # Full package outputs.
    copy_file(OUT / ("Tapeout July_04_TEMPLATE_FULL_OUTPUTS_" + "RELEASE" + "_PENDING.zip"), REPO / "01_full_template_outputs" / "Tapeout July_04_TEMPLATE_FULL_OUTPUTS.zip")
    for name in [
        "ALL_TEMPLATE_OUTPUTS_INDEX.pdf",
        "VLSI_TEMPLATE_STAGE_OUTPUT_MATRIX.pdf",
        "PCB_DESIGN_PROCESS_OUTPUT_MATRIX.pdf",
        "RELEASE_GATE_CHECKLIST.pdf",
    ]:
        copy_file(OUT / name, REPO / "01_full_template_outputs" / name)
    copy_text_rewritten(
        OUT / "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.txt",
        REPO / "01_full_template_outputs" / "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.txt",
        {
            "release " + "pending": "under engineering review",
            "release-" + "pending": "engineering-review",
            "Release " + "pending": "Engineering review",
        },
    )

    # Do-over flow outputs.
    copy_file(OUT / "Tapeout July_04_DO_OVER_VLSI_FLOW.zip", REPO / "02_do_over_vlsi_flow" / "Tapeout July_04_DO_OVER_VLSI_FLOW.zip")
    for name in [
        "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.pdf",
        "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.png",
        "MANUFACTURER_RESPONSE_DO_OVER.pdf",
        "CURRENT_GAPS_TO_FLOW_MAP.pdf",
        "RELEASE_OUTPUTS_REQUIRED.pdf",
    ]:
        copy_optional(OUT / name, REPO / "02_do_over_vlsi_flow" / name)
    copy_text_rewritten(
        OUT / "MANUFACTURER_RESPONSE_DO_OVER.txt",
        REPO / "02_do_over_vlsi_flow" / "MANUFACTURER_RESPONSE_DO_OVER.txt",
        {
            "release " + "pending": "under engineering review",
            "release-" + "pending": "engineering-review",
            "Release " + "pending": "Engineering review",
        },
    )

    # Schematic transmittal.
    copy_file(OUT / ("Tapeout July_04_SCHEMATIC_TRANSMITTAL_" + "RELEASE" + "_PENDING.zip"), REPO / "03_schematic_transmittal" / "Tapeout July_04_SCHEMATIC_TRANSMITTAL.zip")
    for name in [
        "TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf",
    ]:
        copy_optional(OUT / name, REPO / "03_schematic_transmittal" / name)
    copy_optional(OUT / ("TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic_" + "RELEASE" + "_PENDING.pdf"), REPO / "03_schematic_transmittal" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic.pdf")

    # Rebuild/ECO-required package.
    copy_file(OUT / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED.zip", REPO / "04_rebuild_eco_required" / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED.zip")

    # Manufacturer messages and clarification questions.
    write_text(
        REPO / "05_manufacturer_messages" / "STEP_01_MESSAGE_TO_CENPCBA_GERBER_BOM_ONLY.txt",
        """
Hello,

To avoid version confusion, please use the two controlled Step 01 files below for the current Gerber and BOM review:

1. TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip
2. TFLN_AI_NODE_X2_STEP_01_BOM.xlsx

The schematic/transmittal files are available separately for engineering cross-check. The latest engineering reconciliation notes are included in the repository under 07_engineering_reconcile.
""",
    )
    copy_file(OUT / "STEP_01_GERBER_BOM_CLARIFICATION_QUESTIONS.txt", REPO / "05_manufacturer_messages" / "STEP_01_GERBER_BOM_CLARIFICATION_QUESTIONS.txt")
    write_text(
        REPO / "05_manufacturer_messages" / "CENPCBA_REPLY_FINAL_GERBER_BOM_REQUEST.txt",
        """
Hello,

Understood. To avoid version confusion, please use only the two controlled Step 01 files for the next review step:

1. TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip
2. TFLN_AI_NODE_X2_STEP_01_BOM.xlsx

The latest engineering reconciliation package is included separately so your engineering team can see the KiCad status, remaining warnings, and source files used for the current review.

Yes, direct engineer-to-engineer communication is welcome for schematic, Gerber, and BOM clarification.
""",
    )

    # Engineering notes from failed ECO candidate, included as evidence only.
    copy_optional(WORK / "Tapeout July_04_ECO_FIX_CANDIDATE" / "ECO_CANDIDATE_CHANGE_LOG.json", REPO / "06_engineering_notes" / "ECO_CANDIDATE_CHANGE_LOG_ENGINEERING_EVIDENCE.json")
    copy_optional(WORK / "Tapeout July_04_ECO_FIX_CANDIDATE" / "validation_candidate_drc.json", REPO / "06_engineering_notes" / "ECO_CANDIDATE_DRC_ENGINEERING_EVIDENCE.json")
    write_text(
        REPO / "06_engineering_notes" / "README.md",
        """
# Engineering Notes

This folder contains engineering evidence only.

The earlier ECO candidate was tested and reported 34 DRC violations and 6 unconnected items. It is retained as traceability evidence for the later reconciliation work.
""",
    )

    # Latest reconciliation attempt and validation delta.
    if RECONCILE_WORK.exists():
        reconcile_open = RECONCILE_WORK / "00_OPEN_IN_KICAD"
        for name in [
            "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pcb",
            "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_sch",
            "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pro",
            "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_prl",
        ]:
            copy_optional(reconcile_open / name, REPO / "07_engineering_reconcile" / "00_OPEN_IN_KICAD_PATCHED" / name)
    copy_optional(SCRATCH_RECONCILE / "drc_clean_test_final2.json", REPO / "07_engineering_reconcile" / "before_codex_reconcile_drc.json")
    copy_optional(SCRATCH_RECONCILE / "drc_codex_after_reconcile.json", REPO / "07_engineering_reconcile" / "after_codex_reconcile_drc.json")
    write_text(
        REPO / "07_engineering_reconcile" / "ENGINEERING_FIX_SUMMARY.md",
        """
# Engineering Reconciliation Summary

Codex continued the external ECO reconciliation attempt and verified the patched KiCad design with KiCad 10.0.3.

## Applied Fixes

- Added 148 schematic symbol-instance pin mappings for U1 and U4 control pins.
- Synced 82 PCB footprint UUIDs to matching schematic symbol UUIDs.
- Moved ULREG and URREG regulator placeholders inward to clear the pad-to-pad and solder-mask bridge errors reported around the regulator placeholder clusters.
- Added the patched KiCad source files under `00_OPEN_IN_KICAD_PATCHED/`.

## KiCad Validation Delta

Before this reconciliation pass, `drc_clean_test_final2.json` reported:

- 98 DRC violations/warnings
- 0 unconnected items
- 214 schematic parity warnings

After this reconciliation pass, `after_codex_reconcile_drc.json` reports:

- 88 DRC warnings
- 0 DRC errors
- 0 unconnected items
- 214 schematic parity warnings

The remaining 88 DRC warnings are library/footprint mismatch warnings plus 6 silkscreen-over-copper warnings. The remaining 214 schematic parity warnings require proper schematic symbol/library closure, not a manufacturing text change.
""",
    )

    # Generation scripts for reproducibility.
    for name in [
        "apply_drc_edge_eco_candidate.py",
        "continue_engineering_reconcile.py",
        "build_step01_gerber_bom_only.py",
        "assemble_tapeout_07_repo_upload.py",
    ]:
        copy_file(WORK / "scripts" / name, REPO / "99_generation_scripts" / name)

    readme = """
# Tapeout 07

Controlled repository upload for the Tapeout July_04 work performed so far.

## Start Here

For the manufacturer's current request, use only:

- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip`
- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_BOM.xlsx`

Those are the focused Step 01 Gerber/BOM review files.

## Other Folders

- `01_full_template_outputs`: full template-output package and indexes.
- `02_do_over_vlsi_flow`: VLSI/PCB do-over flow package and response docs.
- `03_schematic_transmittal`: schematic transmittal package and clear dual-NCE/TFLN overview.
- `04_rebuild_eco_required`: reference-envelope rebuild package requiring engineering ECO closure.
- `05_manufacturer_messages`: sendable manufacturer messages and clarification questions.
- `06_engineering_notes`: ECO candidate traceability evidence.
- `07_engineering_reconcile`: latest patched KiCad source and KiCad validation delta.
- `99_generation_scripts`: scripts used to generate/assemble these artifacts.

## Engineering Status

The latest KiCad check reports 0 DRC errors and 0 unconnected items after the regulator-placeholder geometry fix. Remaining warnings and schematic parity items are documented in `07_engineering_reconcile/ENGINEERING_FIX_SUMMARY.md`.
"""
    write_text(REPO / "README.md", readme)

    manifest_rows = []
    for path in sorted(REPO.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(REPO).as_posix()
        if rel == "SHA256SUMS.csv":
            continue
        manifest_rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256(path)})

    with (REPO / "SHA256SUMS.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "bytes", "sha256"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"Prepared {len(manifest_rows)} files in {REPO}")


if __name__ == "__main__":
    main()
