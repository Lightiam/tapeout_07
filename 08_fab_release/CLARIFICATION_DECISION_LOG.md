# Clarification Decision Log

Recommended engineering defaults for the seven Step 01 manufacturer questions
(`../05_manufacturer_messages/STEP_01_GERBER_BOM_CLARIFICATION_QUESTIONS.txt`).
Every item still requires named engineering/procurement/mechanical signoff before
it becomes binding on the fabricator.

| ID | Question | Recommended default | Rationale | Signoff |
| --- | --- | --- | --- | --- |
| Q-A | Are edge optical/bias placeholders and ULREG/URREG production parts? | Mark DNP/no-populate for this reference build; keep footprints for envelope review. | They are board-only placeholders in a reference reconstruction. Populating them requires real part selection and schematic capture. | Eng |
| Q-B | Surface finish? | ENIG. | Fine-pitch BGA and QFN placement benefits from a planar finish. Engineering and manufacturer should confirm process details. | Eng |
| Q-C | Can MH5 move inward from X=300.0 mm for edge clearance, or is it fixed by chassis? | Confirm against chassis. If unconstrained, move inward to meet the mechanical clearance rule. | Mounting-hole position is a mechanical-fit decision owned by the chassis team. | Mech |
| Q-D | No-net copper graphics on EO_Bias_Monitor / Slow_Control: remove, trim, or document? | Convert to documented non-electrical graphics or move to a documentation layer. | Floating copper intent should be explicit for DFM and test review. | Eng |
| Q-E | UPWR_L / UPWR_R large outline segments: keep on silkscreen or move to fab documentation only? | Keep on fab documentation. | The post-cleanup KiCad source moved the overlapping graphics off production silkscreen. | Eng |
| Q-F | Who signs off MPN / value / package / qty / DNP / AVL for all parts? | Engineering owns BOM signoff; procurement owns AVL signoff. | Current Step 01 BOM workbook was updated to the reconciled state: 0 DRC errors, 0 unconnected items, 82 library/footprint warnings, 214 schematic-parity warnings, and current chassis-fit wording. | Eng / Proc |
| Q-G | Should the manufacturer review Step 01 as ECO input first, or wait for a later production package? | Use Step 01 as controlled engineering review input. Production package approval follows parity closure, BOM owner signoff, and DFM/DFA closure. | The board still has 214 schematic-parity warnings and needs complete schematic/netlist source for electrical closure. | Eng |

## Effect of Applying the Defaults

Q-A, Q-D, and Q-E close placeholder/documentation intent. Q-B feeds stackup and surface-finish review. Q-F controls BOM/AVL ownership. Q-C is mechanical and independent. Q-G defines the controlled review path for the manufacturer.
