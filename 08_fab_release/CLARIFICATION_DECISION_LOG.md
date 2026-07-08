# Clarification Decision Log

Resolves the 7 open Step-01 manufacturer questions
(`../05_manufacturer_messages/STEP_01_GERBER_BOM_CLARIFICATION_QUESTIONS.txt`)
with a **recommended engineering default** for each. Every item requires a named
sign-off before it is binding on the fabricator.

| ID | Question | Recommended default | Rationale | Sign-off |
| --- | --- | --- | --- | --- |
| Q-A | Are edge optical/bias placeholders (CL32, CR32, DL32, DR32, JL32, JR32 …) and ULREG/URREG production parts? | **Mark DNP** (do not populate) for this reference build; keep footprints for envelope. | They are `board_only` placeholders on a reference reconstruction; no MPNs assigned. Populating requires real part selection + schematic capture. | ☐ Eng ______ |
| Q-B | Surface finish? | **ENIG** | Multiple fine-pitch area-array BGAs (BGA-2500, BGA-1024) require a planar, wire-bondable-grade finish; ENIG is the standard choice and coplanarity-friendly. | ☐ Eng ______ |
| Q-C | Can MH5 move inward from X=300.0 mm for edge clearance, or is it fixed by chassis? | **Confirm against chassis**; if not mechanically constrained, move inward to meet ≥ edge-clearance rule. | Mounting-hole position is a mechanical-fit decision only the chassis owner can make. | ☐ Mech ______ |
| Q-D | No-net copper graphics on EO_Bias_Monitor / Slow_Control — remove, trim, or document? | **Convert to documented non-electrical graphic** (or move to User/Fab layer). | Floating copper with no net can create acid traps / test ambiguity; documenting intent removes DFM risk. | ☐ Eng ______ |
| Q-E | UPWR_L / UPWR_R large silkscreen outlines — keep on silk or move to fab doc only? | **Move to Fab layer**, remove from production silkscreen. | Large outline segments trigger the 6 `silk_over_copper` warnings; belongs on fabrication documentation, not the legend. | ☐ Eng ______ |
| Q-F | Who signs off MPN / value / package / qty / DNP / AVL for all parts (dual NCE, TFLN PIC, RF chain, HBM, regulators, connectors, placeholders)? | **Engineering owns BOM sign-off; procurement owns AVL.** Also correct the stale BOM status sheets (943-DRC / 188×111 mm) to the reconciled state (0 errors / 295.15×140.15 mm). | The shipped BOM workbook's status is pre-reconciliation and out of date. | ☐ Eng ______ / ☐ Proc ______ |
| Q-G | Should the manufacturer review Step-01 as ECO input first, or wait for FINAL after DRC/parity/BOM closure? | **Treat Step-01 as review/ECO input only.** Do not fabricate for production until parity=0 and files re-issued FINAL. | Board is a reference reconstruction with 214 parity warnings; premature production fabrication risks scrap. | ☐ Eng ______ |

## Effect of applying the defaults

Applying Q-A/Q-D/Q-E in KiCad would also clear the 6 `silk_over_copper` warnings
and remove the floating-copper DFM ambiguity. Q-B/Q-F feed directly into the
corrected `.gbrjob` (Finish=ENIG) and the BOM status correction. Q-C is
mechanical and independent. Q-G is the release-gating policy decision.
