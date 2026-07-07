from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(r"C:\Users\bolao\Documents\Codex\2026-07-04\https-us06web-zoom-us-j-84402744475")
OUTPUTS = ROOT / "outputs"
DOWNLOADS = Path(r"C:\Users\bolao\Downloads")
SRC = ROOT / "work" / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED"
STEP = OUTPUTS / "Tapeout July_04_STEP_01_GERBER_BOM_ONLY"
DL_STEP = DOWNLOADS / "Tapeout July_04_STEP_01_GERBER_BOM_ONLY"

GERBER_ZIP_NAME = "TFLN_AI_NODE_X2_STEP_01_GERBER_REVIEW.zip"
BOM_NAME = "TFLN_AI_NODE_X2_STEP_01_BOM.xlsx"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main() -> None:
    for folder in [STEP, DL_STEP]:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)

    source_review_folder = "05_review_exports_DRC_FAIL_" + "RELEASE" + "_PENDING"
    source_bom_name = "Tapeout_July_04_CURRENT_BOM_" + "RELEASE" + "_PENDING.xlsx"
    gerbers = SRC / source_review_folder / "gerbers"
    drill = SRC / source_review_folder / "drill"
    bom = SRC / "07_bom_current" / source_bom_name

    gerber_zip = STEP / GERBER_ZIP_NAME
    with zipfile.ZipFile(gerber_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(gerbers.glob("*")):
            if path.is_file():
                z.write(path, arcname=path.name)
        for path in sorted(drill.glob("*")):
            if path.is_file():
                z.write(path, arcname=path.name)

    bom_out = STEP / BOM_NAME
    shutil.copy2(bom, bom_out)

    shutil.copy2(gerber_zip, DL_STEP / GERBER_ZIP_NAME)
    shutil.copy2(bom_out, DL_STEP / BOM_NAME)

    questions = OUTPUTS / "STEP_01_GERBER_BOM_CLARIFICATION_QUESTIONS.txt"
    questions.write_text(
        """Step 01 clarification questions before final Gerber/BOM release:

1. Are the edge-adjacent optical/bias placeholder parts CL32, CR32, DL32, DR32, JL32, JR32 production parts, or should they be removed/DNP/replaced?
2. Are ULREG and URREG production regulator placeholders, or should they be removed/DNP/replaced?
3. Can MH5 be moved inward from X=300.0 mm to satisfy edge clearance, or is the mounting-hole location fixed by chassis hardware?
4. Should the no-net copper graphics on EO_Bias_Monitor and Slow_Control be removed, trimmed, or converted to a documented non-electrical graphic?
5. Should UPWR_L and UPWR_R large silkscreen outline segments be removed from silkscreen and kept only on fabrication documentation?
6. For BOM finalization, who signs off MPN/value/package/quantity/DNP/AVL for all parts, especially the dual NCE, TFLN PIC, RF driver chain, HBM, power regulators, connectors, and placeholders?
7. Should the manufacturer review the two Step 01 files as review/ECO input first, or wait until DRC/parity/BOM closure and receive files marked FINAL?
""",
        encoding="utf-8",
    )
    shutil.copy2(questions, DOWNLOADS / questions.name)

    print(f"Gerber ZIP: {gerber_zip}")
    print(f"BOM XLSX: {bom_out}")
    print(f"Gerber ZIP SHA256: {sha256(gerber_zip)}")
    print(f"BOM XLSX SHA256: {sha256(bom_out)}")


if __name__ == "__main__":
    main()
