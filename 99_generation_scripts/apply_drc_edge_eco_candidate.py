from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(r"C:\Users\bolao\Documents\Codex\2026-07-04\https-us06web-zoom-us-j-84402744475")
SOURCE = ROOT / "work" / "Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED"
TARGET = ROOT / "work" / "Tapeout July_04_ECO_FIX_CANDIDATE"
PCB = TARGET / "00_OPEN_IN_KICAD" / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pcb"


FOOTPRINT_MOVES = {
    # Move bottom-edge optical/bias placeholders inward. Coordinates are candidate ECO values.
    "CR32": (267.0, 155.0),
    "DR32": (290.0, 155.0),
    "CL32": (43.0, 155.0),
    "DL32": (20.0, 155.0),
    "JR32": (296.0, 154.8),
    "JL32": (14.0, 154.8),
    "ULREG": (60.0, 155.0),
    "URREG": (230.0, 155.0),
    # Move right-edge mounting hole inward. Requires mechanical/chassis confirmation before final release.
    "MH5": (299.0, 89.0),
}

# No-net copper graphics that touched/crossed board edges. Coordinates are trimmed inside the 0.5 mm rule.
GR_LINE_COORDS = {
    "eba88c54-09da-43cd-a155-8b7d59a4d3fd": ((85.0, 45.0), (85.0, 17.8)),
    "530e62ba-4f27-4d27-b194-9e9384dd78cf": ((128.0, 17.8), (135.0, 23.0)),
    "25cb34e2-f4c6-4868-8b18-936d8329489c": ((182.0, 17.8), (175.0, 23.0)),
    "8a095189-51e1-472e-9a72-61394f7af9c0": ((225.0, 45.0), (225.0, 17.8)),
    "01c417a9-b8da-464e-8e2b-ff9aeef07dcf": ((145.0, 156.0), (165.0, 156.0)),
    "416262e2-e666-4a3c-b211-f7758c9e07cc": ((145.0, 156.0), (145.0, 149.0)),
    "2b099dd7-c910-413d-8503-0a15f8fa7dbd": ((165.0, 156.0), (165.0, 149.0)),
}

# Two vertical outline segments in each power marker clip the board edge. Move them to F.Fab in the candidate.
SILK_TO_FAB_UUIDS = {
    "9c9f8483-e325-4a08-8883-c7a5044c4772",
    "dbd50bb0-651b-41dc-87d4-febc2dfb307b",
    "41497c1f-a491-4786-a1c1-d549eee9a254",
    "ed642785-5dee-4c5c-b9e6-85b096de2b74",
}


def fmt(v: float) -> str:
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.6f}".rstrip("0").rstrip(".")


def find_matching_paren(text: str, start: int) -> int:
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
    raise ValueError("No matching closing paren")


def iter_blocks(text: str, token: str):
    start = 0
    while True:
        idx = text.find(token, start)
        if idx == -1:
            return
        end = find_matching_paren(text, idx)
        yield idx, end, text[idx:end]
        start = end


def replace_footprint_at(text: str, ref: str, xy: tuple[float, float]) -> tuple[str, bool]:
    needle = f'(property "Reference" "{ref}"'
    for start, end, block in iter_blocks(text, "\t(footprint"):
        if needle not in block:
            continue
        new_at = f"(at {fmt(xy[0])} {fmt(xy[1])})"
        new_block, count = re.subn(r"\(at\s+[-0-9.]+\s+[-0-9.]+(?:\s+[-0-9.]+)?\)", new_at, block, count=1)
        if count != 1:
            raise RuntimeError(f"Could not update at() for {ref}")
        return text[:start] + new_block + text[end:], True
    return text, False


def replace_gr_line_coords(text: str, uuid: str, start_xy: tuple[float, float], end_xy: tuple[float, float]) -> tuple[str, bool]:
    needle = f'(uuid "{uuid}")'
    for start, end, block in iter_blocks(text, "\t(gr_line"):
        if needle not in block:
            continue
        new_block, c1 = re.subn(r"\(start\s+[-0-9.]+\s+[-0-9.]+\)", f"(start {fmt(start_xy[0])} {fmt(start_xy[1])})", block, count=1)
        new_block, c2 = re.subn(r"\(end\s+[-0-9.]+\s+[-0-9.]+\)", f"(end {fmt(end_xy[0])} {fmt(end_xy[1])})", new_block, count=1)
        if c1 != 1 or c2 != 1:
            raise RuntimeError(f"Could not update gr_line {uuid}")
        return text[:start] + new_block + text[end:], True
    return text, False


def move_fp_line_to_fab(text: str, uuid: str) -> tuple[str, bool]:
    needle = f'(uuid "{uuid}")'
    for start, end, block in iter_blocks(text, "\t\t(fp_line"):
        if needle not in block:
            continue
        new_block = block.replace('(layer "F.SilkS")', '(layer "F.Fab")')
        if new_block == block:
            raise RuntimeError(f"Could not change layer for fp_line {uuid}")
        return text[:start] + new_block + text[end:], True
    return text, False


def main() -> None:
    if TARGET.exists():
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET)

    text = PCB.read_text(encoding="utf-8")
    log: list[dict[str, str]] = []

    for ref, xy in FOOTPRINT_MOVES.items():
        text, ok = replace_footprint_at(text, ref, xy)
        if not ok:
            raise RuntimeError(f"Missing footprint {ref}")
        log.append({"Item": ref, "Action": "move_footprint", "Candidate ECO": f"at {fmt(xy[0])} {fmt(xy[1])}"})

    for uuid, (start_xy, end_xy) in GR_LINE_COORDS.items():
        text, ok = replace_gr_line_coords(text, uuid, start_xy, end_xy)
        if not ok:
            raise RuntimeError(f"Missing gr_line {uuid}")
        log.append({"Item": uuid, "Action": "trim_no_net_copper_graphic", "Candidate ECO": f"start {start_xy} end {end_xy}"})

    for uuid in SILK_TO_FAB_UUIDS:
        text, ok = move_fp_line_to_fab(text, uuid)
        if not ok:
            raise RuntimeError(f"Missing fp_line {uuid}")
        log.append({"Item": uuid, "Action": "move_silkscreen_edge_segment_to_fab", "Candidate ECO": "F.SilkS -> F.Fab"})

    PCB.write_text(text, encoding="utf-8", newline="\n")

    log_path = TARGET / "ECO_CANDIDATE_CHANGE_LOG.json"
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Wrote candidate: {TARGET}")
    print(f"Changed items: {len(log)}")


if __name__ == "__main__":
    main()
