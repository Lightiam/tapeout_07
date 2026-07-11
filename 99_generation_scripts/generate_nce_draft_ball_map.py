#!/usr/bin/env python3
"""
Generate a DRAFT ball-out for the LightRail NCE Gen3 "SpikingBrain" die
(U1/U4, footprint LightRail:BGA-2500_40x40mm_P0.8mm).

This is a SYSTEMATIC PLACEHOLDER for engineering review, NOT an
authoritative vendor/foundry ball map. LightRail's NCE is a proprietary,
not-yet-taped-out ASIC. No real ball map exists. Every row in the output
is tagged DRAFT-PENDING-IP-OWNER-SIGNOFF.

Grid: BGA-2500 laid out on a standard JEDEC alpha-row grid, ~50x50 = 2500
positions, with the "I/O/Q/Z/1" columns/letters some vendors skip omitted
(kept simple here: rows A..BX skipping letters I,O,Q,Z per common JEDEC
convention, columns 1..~54 to reach 2500 usable positions after
depopulating the four corner keep-out zones typical of large BGAs).

Zone allocation (approximate, proportioned from the LightRail architecture
docs: 22-layer stack, dual-HBM-channel compute die, TFLN/optical SerDes,
PCIe/fabric fanout):
  - Outer 2 rings              -> POWER / GND (VDD, VDDQ, VSS rings)
  - Next ring in                -> CLOCK / RESET / STRAP / DEBUG (JTAG, etc.)
  - Four side blocks            -> HBM channel A/B/C/D (maps toward
                                    U30-U35 / U40-U45 HBM stack positions)
  - One edge block              -> TFLN / optical SerDes lanes (maps
                                    toward U3 TFLN PIC)
  - One edge block              -> PCIe / fabric lanes (maps toward
                                    U270-U273 PEX88096 switches)
  - Remaining interior          -> NC / RESERVED (padding, unassigned)
"""
import csv

OUT_PATH = "09_pin_complete_data/NCE_BGA2500_DRAFT_BALL_MAP.csv"

# JEDEC BGA row-letter sequence skips I, O, Q, Z, and (once past Z) the
# double-letter sequence also skips any second letter that would collide.
SKIP = set("IOQZ")


def jedec_rows(n):
    rows = []
    letters = [c for c in "ABCDEFGHJKLMNPRTUVWY"]  # single-letter set (skips I,O,Q)
    for L in letters:
        rows.append(L)
    # double-letter continuation: AA, AB, AC, ... skipping the same letters
    i = 0
    while len(rows) < n:
        first = letters[i // len(letters)]
        second = letters[i % len(letters)]
        rows.append(first + second)
        i += 1
    return rows[:n]


def classify(row_idx, col_idx, n_rows, n_cols):
    """Return (category, signal_group, voltage_bank, direction) for a ball
    at grid position (row_idx, col_idx), 0-indexed."""
    ring = min(row_idx, col_idx, n_rows - 1 - row_idx, n_cols - 1 - col_idx)

    if ring == 0:
        return ("POWER", "VDD_CORE_RING", "VDD_0V75", "PWR")
    if ring == 1:
        return ("GROUND", "VSS_RING", "GND", "PWR")
    if ring == 2:
        # alternate power rail and clock/reset/strap/debug around this ring
        if (row_idx + col_idx) % 2 == 0:
            return ("POWER", "VDDQ_IO_RING", "VDD_1V1", "PWR")
        else:
            return ("CTRL", "CLK_RST_STRAP_DEBUG", "VDD_1V1", "BIDIR")

    # Interior zones by quadrant/edge, proportioned per architecture:
    # top edge block -> HBM channel A/B, bottom edge -> HBM channel C/D,
    # left edge -> TFLN/optical SerDes, right edge -> PCIe/fabric, deep
    # interior -> NC/reserved.
    is_top = row_idx < n_rows * 0.30
    is_bottom = row_idx > n_rows * 0.70
    is_left = col_idx < n_cols * 0.22
    is_right = col_idx > n_cols * 0.78

    if is_top and not (is_left or is_right):
        half = "A" if col_idx < n_cols / 2 else "B"
        return ("HBM_CHANNEL", f"HBM_CH{half}_DQ_DQS_CA", "VDDQ_HBM_0V4", "BIDIR")
    if is_bottom and not (is_left or is_right):
        half = "C" if col_idx < n_cols / 2 else "D"
        return ("HBM_CHANNEL", f"HBM_CH{half}_DQ_DQS_CA", "VDDQ_HBM_0V4", "BIDIR")
    if is_left:
        return ("OPTICAL_SERDES", "TFLN_PIC_SERDES_LANE", "VDD_0V9_SERDES", "BIDIR")
    if is_right:
        return ("PCIE_FABRIC", "PCIE_GEN6_FABRIC_LANE", "VDD_0V9_SERDES", "BIDIR")

    return ("NC_RESERVED", "UNASSIGNED", "N/A", "NC")


def main():
    n_rows, n_cols = 50, 50  # 2500 positions
    rows = jedec_rows(n_rows)

    counts = {}
    with open(OUT_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "ball_id", "row", "col", "category", "signal_group",
            "voltage_bank", "direction", "status",
        ])
        for r_idx, r_letter in enumerate(rows):
            for c_idx in range(1, n_cols + 1):
                ball_id = f"{r_letter}{c_idx}"
                category, sig_group, vbank, direction = classify(
                    r_idx, c_idx - 1, n_rows, n_cols
                )
                counts[category] = counts.get(category, 0) + 1
                w.writerow([
                    ball_id, r_letter, c_idx, category, sig_group,
                    vbank, direction, "DRAFT-PENDING-IP-OWNER-SIGNOFF",
                ])

    total = sum(counts.values())
    print(f"Wrote {total} balls to {OUT_PATH}")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:16s} {v:5d}  ({100*v/total:.1f}%)")


if __name__ == "__main__":
    main()
