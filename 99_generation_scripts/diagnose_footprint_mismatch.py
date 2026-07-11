#!/usr/bin/env python3
"""Diagnose exactly why kicad-cli flags 'lib_footprint_mismatch' for a given
reference, by loading both the board-embedded footprint and the current
library copy via the pcbnew API and comparing field-by-field."""
import sys
import pcbnew

BOARD = "/home/user/workspace/tapeout_07/07_engineering_reconcile/00_OPEN_IN_KICAD_PATCHED/TFLN_AI_NODE_X2_SERVER_CHASSIS_IO.kicad_pcb"
LIB_DIR = "/home/user/workspace/tapeout_07/07_engineering_reconcile/00_OPEN_IN_KICAD_PATCHED"

REF = sys.argv[1] if len(sys.argv) > 1 else "U35"

board = pcbnew.LoadBoard(BOARD)
fp = None
for f in board.GetFootprints():
    if f.GetReference() == REF:
        fp = f
        break
if fp is None:
    print(f"Reference {REF} not found on board")
    sys.exit(1)

fpid = fp.GetFPID()
lib_nick = fpid.GetLibNickname().wx_str()
fp_name = fpid.GetLibItemName().wx_str()
lib_path = f"{LIB_DIR}/{lib_nick}.pretty"

print(f"Reference: {REF}")
print(f"Board footprint lib_id: {lib_nick}:{fp_name}")
print(f"Resolved library path: {lib_path}")

lib_fp = pcbnew.FootprintLoad(lib_path, fp_name)
if lib_fp is None:
    print("Could not load footprint from library path!")
    sys.exit(1)


def pad_signature(footprint):
    sig = {}
    for pad in footprint.Pads():
        name = pad.GetNumber()
        sig[name] = (
            pad.GetShape(),
            (pad.GetSize().x, pad.GetSize().y),
            (pad.GetOffset().x, pad.GetOffset().y),
            pad.GetAttribute(),
            pad.GetLayerSet().FmtHex(),
            pad.GetDrillSizeX(),
            pad.GetDrillSizeY(),
        )
    return sig


board_sig = pad_signature(fp)
lib_sig = pad_signature(lib_fp)

print(f"\nBoard pad count: {len(board_sig)}  Library pad count: {len(lib_sig)}")

only_board = set(board_sig) - set(lib_sig)
only_lib = set(lib_sig) - set(board_sig)
if only_board:
    print("Pads only on board:", only_board)
if only_lib:
    print("Pads only in library:", only_lib)

diffs = []
for name in sorted(set(board_sig) & set(lib_sig)):
    if board_sig[name] != lib_sig[name]:
        diffs.append((name, board_sig[name], lib_sig[name]))

if diffs:
    print(f"\n{len(diffs)} pad(s) differ:")
    for name, b, l in diffs:
        print(f"  pad {name}:")
        print(f"    board:   {b}")
        print(f"    library: {l}")
else:
    print("\nAll shared pads are IDENTICAL (shape/size/offset/attr/layer/drill).")

# Compare footprint-level attributes
print("\n--- Footprint-level attribute comparison ---")
for attr_name in ["GetAttributes", "GetLayer", "GetLocalClearance",
                   "GetLocalSolderMaskMargin", "GetLocalSolderPasteMargin",
                   "GetZoneConnection", "AllowMissingCourtyard",
                   "IsBoardOnly", "IsExcludedFromPosFiles",
                   "IsExcludedFromBOM"]:
    try:
        b_val = getattr(fp, attr_name)()
        l_val = getattr(lib_fp, attr_name)()
        marker = "  <-- DIFFERS" if b_val != l_val else ""
        print(f"{attr_name}: board={b_val} lib={l_val}{marker}")
    except Exception as e:
        print(f"{attr_name}: (error: {e})")

# Compare 3D models
board_models = [m.m_Filename for m in fp.Models()]
lib_models = [m.m_Filename for m in lib_fp.Models()]
print(f"\n3D models board: {board_models}")
print(f"3D models lib:   {lib_models}")

# Compare graphic item counts (fp_line, fp_text, etc.)
print(f"\nGraphic items - board: {len(list(fp.GraphicalItems()))}, "
      f"library: {len(list(lib_fp.GraphicalItems()))}")
