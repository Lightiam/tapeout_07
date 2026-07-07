from __future__ import annotations

import json
import re
import uuid
from collections import defaultdict
from pathlib import Path


ROOT = Path(r"C:\Users\bolao\.gemini\antigravity-ide\scratch\work\Tapeout July_04_REBUILD_295x140_REFERENCE_FULL_ENGINEERING_ECO_REQUIRED")
OPEN = ROOT / "00_OPEN_IN_KICAD"
PCB = OPEN / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pcb"
SCH = OPEN / "TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_sch"
DRC = Path(r"C:\Users\bolao\.gemini\antigravity-ide\scratch\drc_clean_test_final2.json")


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
    raise ValueError(f"No matching paren at {start}")


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


def block_uuid(block: str) -> str | None:
    m = re.search(r'\(uuid\s+"([^"]+)"\)', block)
    return m.group(1) if m else None


def read_parity() -> tuple[dict[str, list[str]], set[str]]:
    data = json.loads(DRC.read_text(encoding="utf-8"))
    missing_pins: dict[str, list[str]] = defaultdict(list)
    extra_refs: set[str] = set()
    for item in data.get("schematic_parity", []):
        if item.get("type") == "extra_footprint":
            for it in item.get("items", []):
                m = re.search(r"Footprint\s+(\S+)", it.get("description", ""))
                if m:
                    extra_refs.add(m.group(1))
        elif item.get("type") == "net_conflict":
            for it in item.get("items", []):
                m = re.search(r"Pad\s+(\S+)\s+\[[^\]]+\]\s+of\s+(\S+)\s+", it.get("description", ""))
                if m:
                    missing_pins[m.group(2)].append(m.group(1))
    return missing_pins, extra_refs


def patch_symbol_instances(text: str, missing_pins: dict[str, list[str]]) -> tuple[str, int]:
    patches: list[tuple[int, int, str]] = []
    patched = 0
    for start, end, block in iter_blocks(text, "(symbol (lib_id"):
        ref = ref_from_block(block)
        if not ref or ref not in missing_pins:
            continue
        existing = set(re.findall(r'\(pin\s+"([^"]+)"', block))
        additions = []
        for pin in missing_pins[ref]:
            if pin in existing:
                continue
            additions.append(f'    (pin "{pin}" (uuid "{uuid.uuid4()}"))')
        if not additions:
            continue
        new_block = block[:-3].rstrip() + "\n" + "\n".join(additions) + "\n  )"
        patches.append((start, end, new_block))
        patched += len(additions)
    for start, end, repl in reversed(patches):
        text = text[:start] + repl + text[end:]
    return text, patched


def schematic_ref_uuids(text: str) -> dict[str, str]:
    refs: dict[str, str] = {}
    for _, _, block in iter_blocks(text, "(symbol (lib_id"):
        ref = ref_from_block(block)
        uid = block_uuid(block)
        if ref and uid:
            refs[ref] = uid
    return refs


def patch_pcb(text: str, sch_uuids: dict[str, str], extra_refs: set[str]) -> tuple[str, int, int, int]:
    patches: list[tuple[int, int, str]] = []
    synced = 0
    board_only = 0
    moved = 0
    moves = {
        "ULREG": (60.0, 147.0),
        "URREG": (230.0, 147.0),
    }
    for start, end, block in iter_blocks(text, "(footprint "):
        ref = ref_from_block(block)
        if not ref:
            continue
        new = block
        if ref in sch_uuids:
            new, n = re.subn(r'\(uuid\s+"[^"]+"\)', f'(uuid "{sch_uuids[ref]}")', new, count=1)
            synced += n
        if ref in extra_refs and ref not in sch_uuids:
            attr = re.search(r'\(attr\s+([^)]+)\)', new)
            if attr:
                if "board_only" not in attr.group(1):
                    new = new[:attr.start()] + f'(attr {attr.group(1)} board_only)' + new[attr.end():]
                    board_only += 1
            else:
                prop_idx = new.find('(property "Reference"')
                if prop_idx != -1:
                    new = new[:prop_idx] + '\t\t(attr board_only)\n' + new[prop_idx:]
                    board_only += 1
        if ref in moves:
            x, y = moves[ref]
            ref_idx = new.find('(property "Reference"')
            at_match = re.search(r'\(at\s+[-0-9.]+\s+[-0-9.]+(?:\s+[-0-9.]+)?\)', new[:ref_idx])
            if at_match:
                replacement = f"(at {x:g} {y:g})"
                new = new[:at_match.start()] + replacement + new[at_match.end():]
                moved += 1
        if new != block:
            patches.append((start, end, new))
    for start, end, repl in reversed(patches):
        text = text[:start] + repl + text[end:]
    return text, synced, board_only, moved


def main() -> None:
    missing_pins, extra_refs = read_parity()

    sch_text = SCH.read_text(encoding="utf-8")
    sch_text, pin_count = patch_symbol_instances(sch_text, missing_pins)
    SCH.write_text(sch_text, encoding="utf-8", newline="\n")

    sch_uuids = schematic_ref_uuids(sch_text)
    pcb_text = PCB.read_text(encoding="utf-8")
    pcb_text, synced, board_only, moved = patch_pcb(pcb_text, sch_uuids, extra_refs)
    PCB.write_text(pcb_text, encoding="utf-8", newline="\n")

    print(f"Added schematic instance pin mappings: {pin_count}")
    print(f"Synced PCB footprint UUIDs to schematic symbols: {synced}")
    print(f"Marked true PCB-only extras board_only: {board_only}")
    print(f"Moved regulator placeholders inward: {moved}")


if __name__ == "__main__":
    main()
