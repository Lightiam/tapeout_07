from __future__ import annotations

import json
import re
import shutil
import uuid
from pathlib import Path


ROOT = Path(r"C:\Users\bolao\Documents\Codex\2026-07-04\https-us06web-zoom-us-j-84402744475")
REPO = ROOT / "work" / "github_tapeout_07"
OPEN = REPO / "07_engineering_reconcile" / "00_OPEN_IN_KICAD_PATCHED"
PCB = OPEN / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pcb"
SCH = OPEN / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_sch"


def find_matching(text: str, start: int) -> int:
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError(f"No matching paren from {start}")


def iter_blocks(text: str, token: str):
    start = 0
    while True:
        idx = text.find(token, start)
        if idx == -1:
            return
        end = find_matching(text, idx)
        yield idx, end, text[idx:end]
        start = end


def ref_from_block(block: str) -> str | None:
    m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
    return m.group(1) if m else None


def top_at(block: str) -> tuple[float, float, str] | None:
    ref_idx = block.find('(property "Reference"')
    area = block[:ref_idx] if ref_idx != -1 else block[:400]
    m = re.search(r'\(at\s+([-0-9.]+)\s+([-0-9.]+)(?:\s+([-0-9.]+))?\)', area)
    if not m:
        return None
    return float(m.group(1)), float(m.group(2)), m.group(3) or ""


def collect_footprint_blocks(text: str) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for _, _, block in iter_blocks(text, "\t(footprint "):
        m = re.match(r'\t\(footprint\s+"([^"]*)"', block)
        if not m or ":" not in m.group(1):
            continue
        lib, name = m.group(1).split(":", 1)
        result.setdefault((lib, name), block)
    return result


def make_library_footprint(board_block: str, short_name: str) -> str:
    block = board_block
    block = re.sub(r'^\t\(footprint\s+"[^"]*"', f'(footprint "{short_name}"', block, count=1)
    block = re.sub(r'\n\t\t(?:locked\s+)?\(at\s+[-0-9.]+\s+[-0-9.]+(?:\s+[-0-9.]+)?\)', '', block, count=1)
    block = re.sub(r'\n\t\t\(uuid\s+"[^"]+"\)', '', block, count=1)
    block = re.sub(r'\n\t\t\(path\s+"[^"]+"\)', '', block)
    block = re.sub(r'\n\t\t\(attr\s+[^)]*\)', '', block)
    block = re.sub(r'\n\t\t\(property\s+"Reference"[\s\S]*?\n\t\t\)', '', block, count=1)
    block = re.sub(r'\n\t\t\(property\s+"Value"[\s\S]*?\n\t\t\)', '', block, count=1)
    block = block.replace("\n\t\t", "\n\t").replace("\n\t", "\n  ")
    return block + "\n"


def write_fp_lib_table(libs: list[str]) -> None:
    fp_table = [
        "(fp_lib_table",
        *[
            f'  (lib (name "{lib}")(type "KiCad")(uri "${{KIPRJMOD}}/{lib}.pretty")(options "")(descr "Project-local library for reconciled PCB package"))'
            for lib in sorted(set(libs))
        ],
        ")",
        "",
    ]
    (OPEN / "fp-lib-table").write_text("\n".join(fp_table), encoding="utf-8", newline="\n")


def write_local_libraries(pcb_text: str) -> list[str]:
    libs = collect_footprint_blocks(pcb_text)
    written = []
    by_lib: dict[str, list[tuple[str, str]]] = {}
    for (lib, name), block in libs.items():
        by_lib.setdefault(lib, []).append((name, block))
    for lib, entries in sorted(by_lib.items()):
        pretty = OPEN / f"{lib}.pretty"
        if pretty.exists():
            shutil.rmtree(pretty)
        pretty.mkdir(parents=True, exist_ok=True)
        for name, block in sorted(entries):
            (pretty / f"{name}.kicad_mod").write_text(make_library_footprint(block, name), encoding="utf-8", newline="\n")
        written.append(lib)

    return written


def patch_stackup_and_process(pcb_text: str) -> str:
    stackup = """\
		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (thickness 0.0100))
			(layer "F.Cu" (type "copper") (thickness 0.0350))
			(layer "dielectric 1" (type "prepreg") (thickness 0.1800) (material "High-Tg-FR4") (epsilon_r 4.2) (loss_tangent 0.015))
			(layer "In1.Cu" (type "copper") (thickness 0.0350))
			(layer "dielectric 2" (type "core") (thickness 1.0900) (material "High-Tg-FR4") (epsilon_r 4.2) (loss_tangent 0.015))
			(layer "In2.Cu" (type "copper") (thickness 0.0350))
			(layer "dielectric 3" (type "prepreg") (thickness 0.1800) (material "High-Tg-FR4") (epsilon_r 4.2) (loss_tangent 0.015))
			(layer "B.Cu" (type "copper") (thickness 0.0350))
			(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.0100))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "ENIG")
			(dielectric_constraints yes)
		)
"""
    setup_idx = pcb_text.find("\t(setup\n")
    if setup_idx == -1:
        raise RuntimeError("PCB setup block not found")
    setup_end = find_matching(pcb_text, setup_idx)
    setup = pcb_text[setup_idx:setup_end]
    if "\t\t(stackup" in setup:
        s_idx = setup.find("\t\t(stackup")
        s_end = find_matching(setup, s_idx)
        setup = setup[:s_idx] + stackup + setup[s_end:]
    else:
        insert = setup.find("\t\t(pad_to_mask_clearance")
        setup = setup[:insert] + stackup + setup[insert:]
    setup = re.sub(r'\(pad_to_mask_clearance\s+[-0-9.]+\)', '(pad_to_mask_clearance 0.05)', setup, count=1)
    if "(solder_mask_min_width" not in setup:
        setup = setup.replace("\t\t(pad_to_mask_clearance 0.05)\n", "\t\t(pad_to_mask_clearance 0.05)\n\t\t(solder_mask_min_width 0.05)\n", 1)
    return pcb_text[:setup_idx] + setup + pcb_text[setup_end:]


def patch_title_blocks(pcb_text: str, sch_text: str) -> tuple[str, str]:
    title = """\
	(title_block
		(title "TFLN_AI_NODE_X2 Server Chassis IO")
		(date "2026-07-07")
		(rev "July_04-ENG-RECONCILE-01")
		(company "LightRail AI")
		(comment 1 "4-layer High-Tg FR4 review stackup, ENIG finish")
		(comment 2 "Connectivity source/netlist required to close schematic parity")
	)
"""
    paper_end = pcb_text.find("\n\t(layers")
    if paper_end == -1:
        raise RuntimeError("PCB layers block not found")
    if "\n\t(title_block" in pcb_text[:paper_end]:
        idx = pcb_text.find("\n\t(title_block")
        end = find_matching(pcb_text, idx + 1)
        pcb_text = pcb_text[: idx + 1] + title + pcb_text[end:]
    else:
        pcb_text = pcb_text[:paper_end] + "\n" + title + pcb_text[paper_end:]

    sch_text = re.sub(r'\(rev\s+"[^"]*"\)', '(rev "July_04-ENG-RECONCILE-01")', sch_text, count=1)
    sch_text = re.sub(r'\(comment 3\s+"[^"]*"\)', '(comment 3 "Connectivity source/netlist required to close schematic parity")', sch_text, count=1)
    sch_text = re.sub(r'\(comment 4\s+"[^"]*"\)', '(comment 4 "4-layer High-Tg FR4 review stackup | ENIG finish")', sch_text, count=1)
    return pcb_text, sch_text


def fiducial_block(ref: str, x: float, y: float, layer: str) -> str:
    side = "front" if layer == "F.Cu" else "back"
    mask_layer = "F.Mask" if layer == "F.Cu" else "B.Mask"
    text_layer = "F.Fab" if layer == "F.Cu" else "B.Fab"
    return f'''	(footprint ""
		(layer "{layer}")
		(uuid "{uuid.uuid4()}")
		(at {x:.3f} {y:.3f})
		(attr smd board_only exclude_from_pos_files exclude_from_bom)
		(property "Reference" "{ref}"
			(at 0 -2.0 0)
			(layer "{text_layer}")
			(hide yes)
			(uuid "{uuid.uuid4()}")
			(effects (font (size 1 1) (thickness 0.15)){" (justify mirror)" if side == "back" else ""})
		)
		(property "Value" "FIDUCIAL_1MM"
			(at 0 2.0 0)
			(layer "{text_layer}")
			(hide yes)
			(uuid "{uuid.uuid4()}")
			(effects (font (size 1 1) (thickness 0.15)){" (justify mirror)" if side == "back" else ""})
		)
		(pad "" smd circle
			(at 0 0)
			(size 1 1)
			(layers "{layer}" "{mask_layer}")
			(uuid "{uuid.uuid4()}")
		)
	)
'''


def add_fiducials(pcb_text: str) -> str:
    patches: list[tuple[int, int]] = []
    for start, end, block in iter_blocks(pcb_text, "\t(footprint "):
        ref = ref_from_block(block)
        if ref and re.fullmatch(r"FID[TB]\d", ref):
            patches.append((start, end))
    for start, end in reversed(patches):
        pcb_text = pcb_text[:start] + pcb_text[end:]
    fiducials = [
        ("FIDT1", 30.0, 36.5, "F.Cu"),
        ("FIDT2", 275.0, 36.5, "F.Cu"),
        ("FIDT3", 30.0, 237.0, "F.Cu"),
        ("FIDB1", 35.0, 41.5, "B.Cu"),
        ("FIDB2", 270.0, 41.5, "B.Cu"),
        ("FIDB3", 35.0, 232.0, "B.Cu"),
    ]
    blocks = [fiducial_block(ref, x, y, layer) for ref, x, y, layer in fiducials]
    insert_idx = pcb_text.rfind("\n)")
    return pcb_text[:insert_idx] + "\n" + "\n".join(blocks) + pcb_text[insert_idx:]


def move_silk_to_fab(pcb_text: str) -> str:
    for silk_uuid in [
        "01b8d434-7d38-41a7-8c89-a7f9ef1c6120",
        "4f424786-df7e-4c8a-8946-0a5273cf0954",
    ]:
        needle = f'(uuid "{silk_uuid}")'
        pos = pcb_text.find(needle)
        if pos == -1:
            continue
        start = pcb_text.rfind("\t\t(fp_line", 0, pos)
        if start == -1:
            continue
        end = find_matching(pcb_text, start)
        block = pcb_text[start:end].replace('(layer "F.SilkS")', '(layer "F.Fab")')
        pcb_text = pcb_text[:start] + block + pcb_text[end:]
    return pcb_text


def write_fiducial_library() -> None:
    pretty = OPEN / "Fiducial.pretty"
    pretty.mkdir(exist_ok=True)
    mod = '''(footprint "Fiducial_1mm_Mask2mm"
  (version 20241229)
  (generator "codex")
  (descr "1 mm copper fiducial with 2 mm solder mask opening")
  (attr smd exclude_from_bom)
  (fp_circle (center 0 0) (end 1 0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd") (uuid "11111111-1111-4111-8111-111111111111"))
  (pad "" smd circle (at 0 0) (size 1 1) (layers "F.Cu" "F.Mask"))
)
'''
    (pretty / "Fiducial_1mm_Mask2mm.kicad_mod").write_text(mod, encoding="utf-8", newline="\n")


def main() -> None:
    pcb_text = PCB.read_text(encoding="utf-8")
    sch_text = SCH.read_text(encoding="utf-8")

    pcb_text = patch_stackup_and_process(pcb_text)
    pcb_text, sch_text = patch_title_blocks(pcb_text, sch_text)
    pcb_text = add_fiducials(pcb_text)
    pcb_text = move_silk_to_fab(pcb_text)

    PCB.write_text(pcb_text, encoding="utf-8", newline="\n")
    SCH.write_text(sch_text, encoding="utf-8", newline="\n")

    libs = write_local_libraries(pcb_text)
    write_fiducial_library()
    if "Fiducial" not in libs:
        libs.append("Fiducial")
    write_fp_lib_table(libs)
    print(json.dumps({"local_libraries": sorted(libs), "updated": [str(PCB), str(SCH)]}, indent=2))


if __name__ == "__main__":
    main()
