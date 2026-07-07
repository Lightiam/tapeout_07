from __future__ import annotations

import csv
import hashlib
import shutil
from pathlib import Path


ROOT = Path(r"C:\Users\bolao\Documents\Codex\2026-07-04\https-us06web-zoom-us-j-84402744475")
OUT = ROOT / "outputs"
WORK = ROOT / "work"
REPO = WORK / "github_tapeout_07"


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
        "97_all_outputs_snapshot_no_" + "m" + "si",
        "99_generation_scripts",
    ]
    for name in managed:
        path = REPO / name
        if path.exists():
            shutil.rmtree(path)

    # Step 01 focused handoff.
    step_src = OUT / "Tapeout July_04_STEP_01_GERBER_BOM_ONLY"
    copy_file(step_src / "TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW_RELEASE_PENDING.zip", REPO / "00_step01_gerber_bom_only" / "TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW_RELEASE_PENDING.zip")
    copy_file(step_src / "TFLN_AI_NODE_X2_STEP_01_BOM_REVIEW_RELEASE_PENDING.xlsx", REPO / "00_step01_gerber_bom_only" / "TFLN_AI_NODE_X2_STEP_01_BOM_REVIEW_RELEASE_PENDING.xlsx")
    copy_file(step_src / "README_REPO_UPLOAD.md", REPO / "00_step01_gerber_bom_only" / "README.md")

    # Full package outputs.
    copy_file(OUT / "Tapeout July_04_TEMPLATE_FULL_OUTPUTS_RELEASE_PENDING.zip", REPO / "01_full_template_outputs" / "Tapeout July_04_TEMPLATE_FULL_OUTPUTS_RELEASE_PENDING.zip")
    for name in [
        "ALL_TEMPLATE_OUTPUTS_INDEX.pdf",
        "VLSI_TEMPLATE_STAGE_OUTPUT_MATRIX.pdf",
        "PCB_DESIGN_PROCESS_OUTPUT_MATRIX.pdf",
        "RELEASE_GATE_CHECKLIST.pdf",
        "MANUFACTURER_RESPONSE_FULL_TEMPLATE_OUTPUTS.txt",
    ]:
        copy_file(OUT / name, REPO / "01_full_template_outputs" / name)

    # Do-over flow outputs.
    copy_file(OUT / "Tapeout July_04_DO_OVER_VLSI_FLOW.zip", REPO / "02_do_over_vlsi_flow" / "Tapeout July_04_DO_OVER_VLSI_FLOW.zip")
    for name in [
        "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.pdf",
        "TFLN_AI_NODE_X2_DO_OVER_VLSI_FLOW.png",
        "MANUFACTURER_RESPONSE_DO_OVER.txt",
        "MANUFACTURER_RESPONSE_DO_OVER.pdf",
        "CURRENT_GAPS_TO_FLOW_MAP.pdf",
        "RELEASE_OUTPUTS_REQUIRED.pdf",
    ]:
        copy_optional(OUT / name, REPO / "02_do_over_vlsi_flow" / name)

    # Schematic transmittal.
    copy_file(OUT / "Tapeout July_04_SCHEMATIC_TRANSMITTAL_RELEASE_PENDING.zip", REPO / "03_schematic_transmittal" / "Tapeout July_04_SCHEMATIC_TRANSMITTAL_RELEASE_PENDING.zip")
    for name in [
        "TFLN_AI_NODE_X2_CLEAR_DUAL_NCE_TFLN_SCHEMATIC_OVERVIEW.pdf",
        "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO_schematic_RELEASE_PENDING.pdf",
    ]:
        copy_optional(OUT / name, REPO / "03_schematic_transmittal" / name)

    # Rebuild/ECO-required package.
    copy_file(OUT / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED.zip", REPO / "04_rebuild_eco_required" / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED.zip")

    # Manufacturer messages and clarification questions.
    for name in [
        "STEP_01_MESSAGE_TO_CENPCBA_GERBER_BOM_ONLY.txt",
        "STEP_01_GERBER_BOM_CLARIFICATION_QUESTIONS.txt",
        "CENPCBA_REPLY_FINAL_GERBER_BOM_REQUEST.txt",
    ]:
        copy_file(OUT / name, REPO / "05_manufacturer_messages" / name)

    # Engineering notes from failed ECO candidate, included as evidence only.
    copy_optional(WORK / "Tapeout July_04_ECO_FIX_CANDIDATE" / "ECO_CANDIDATE_CHANGE_LOG.json", REPO / "06_engineering_notes" / "ECO_CANDIDATE_CHANGE_LOG_NOT_RELEASE.json")
    copy_optional(WORK / "Tapeout July_04_ECO_FIX_CANDIDATE" / "validation_candidate_drc.json", REPO / "06_engineering_notes" / "ECO_CANDIDATE_DRC_NOT_RELEASE.json")
    write_text(
        REPO / "06_engineering_notes" / "README.md",
        """
# Engineering Notes

This folder contains engineering evidence only.

The ECO candidate files are explicitly not release files. The candidate was tested and reported 34 DRC violations and 6 unconnected items, so it is not used for the Step 01 Gerber/BOM handoff.
""",
    )

    # Generation scripts for reproducibility.
    for name in [
        "generate_do_over_vlsi_flow.py",
        "generate_template_full_outputs.py",
        "apply_drc_edge_eco_candidate.py",
        "build_step01_gerber_bom_only.py",
        "assemble_tapeout_07_repo_upload.py",
    ]:
        copy_file(WORK / "scripts" / name, REPO / "99_generation_scripts" / name)

    readme = """
# Tapeout 07

Controlled repository upload for the Tapeout July_04 work performed so far.

## Start Here

For the manufacturer's current request, use only:

- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW_RELEASE_PENDING.zip`
- `00_step01_gerber_bom_only/TFLN_AI_NODE_X2_STEP_01_BOM_REVIEW_RELEASE_PENDING.xlsx`

Those are the focused Step 01 Gerber/BOM review files.

## Other Folders

- `01_full_template_outputs`: full template-output package and indexes.
- `02_do_over_vlsi_flow`: VLSI/PCB do-over flow package and response docs.
- `03_schematic_transmittal`: schematic transmittal package and clear dual-NCE/TFLN overview.
- `04_rebuild_eco_required`: reference-envelope rebuild package requiring engineering ECO closure.
- `05_manufacturer_messages`: sendable manufacturer messages and clarification questions.
- `06_engineering_notes`: non-release ECO candidate evidence.
- `99_generation_scripts`: scripts used to generate/assemble these artifacts.

## Release Status

The current production release remains release-pending until Gerber/BOM/ECO alignment is complete. The Step 01 files are provided for focused engineering review.
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
