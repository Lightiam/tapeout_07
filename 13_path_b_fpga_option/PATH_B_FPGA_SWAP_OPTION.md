# Path B: Interim FPGA Swap — Documented Option (NOT APPLIED)

**Status: PROPOSAL ONLY. No files in `07_engineering_reconcile/` or the locked reference
layout have been modified. Nothing described here may be implemented without explicit
written sign-off from the IP owner (Bola Olatunji), per the zero-deviation lock on
`TFLN_AI_NODE_X2_SERVER_CHASSIS_IO`.**

---

## 1. Purpose

The NCE (BGA-2500, U1/U4) is LightRail's own unfinished ASIC. A real ball map cannot
exist until it has synthesized RTL, a locked floorplan, and licensed I/O IP on its pad
ring (see prior discussion) — that is a multi-month, real-money engagement (Path A).

Path B is a **parallel, faster option**: build a V0 prototype board using a real,
purchasable part with a genuine, public ball map in place of the NCE, so the rest of
the board — HBM channel routing, PCIe fabric, power delivery, thermal design — can be
validated on real silicon now, while Path A proceeds independently. This document
specs out that option for review. It does not authorize any change.

## 2. What Path B actually changes vs. what it doesn't

| Stays locked, untouched | Would require owner-approved deviation |
|---|---|
| TFLN optical engine (U3, HyperLight target) | Compute die footprint at U1/U4 (BGA-2500 → larger package) |
| HMC8410/HXT45430 driver interface (U50–U53) | PCB keepout/placement site for U1/U4 |
| PCIe fabric slot, power topology, chassis I/O | Possibly local decoupling/power-plane detail under the new footprint |
| HBM4/HBM3E memory sites (U30–U35, U40–U45) — same DDR-style interface either way | Nothing else — HBM sites, TFLN, PCIe slot, chassis stay as-is |

**Important finding from real part data below: no off-the-shelf HBM-in-package FPGA
matches the locked BGA-2500 footprint (40 mm × 40 mm, 0.8 mm pitch).** Every realistic
candidate is physically larger. So Path B is *not* a drop-in swap — it is a genuine
footprint deviation and must go through the same owner sign-off as any other locked-layout
change before a single line of the reference PCB is touched.

## 3. Candidate parts (real, currently available)

| Part family | Specific devices | Package | Balls | Package size | Pitch | In-package memory | Notes |
|---|---|---|---|---|---|---|---|
| AMD Versal HBM Series | VH1522 / VH1542 / VH1582 / VH1742 / VH1782 | VSVA3697 | 3,697 | 57.5 × 57.5 mm | 0.92 mm | 8/16/32 GB HBM2e | [AMD Versal HBM Series](https://www.amd.com/en/products/adaptive-socs-and-fpgas/versal/hbm-series.html), [product selection guide](https://docs.amd.com/api/khub/documents/jEulezc2bGbehGd8brzgZw/content) |
| AMD Versal HBM Series (larger) | same family, LSVA package option | LSVA4737 | 4,737 | 70 × 70 mm | 1.0 mm | 8/16/32 GB HBM2e | same source |
| Intel Agilex 7 M-Series | AGM032 / AGM039 | R47A / R47B | 4,700 | 56 × 66 mm | 0.92 mm | 16 or 32 GB HBM2e (two stacks, 8 channels each, ~410 GB/s per stack / ~820 GB/s total) | [Intel package/pinout guide](https://docs.altera.com/r/docs/814028/current/agilextm-7-fpgas-and-soc-fpgas-package-pinout-and-pcb-design-user-guide/agilextm-7-m-series-devices-with-hbm2e), [Next Platform analysis](https://www.nextplatform.com/compute/2022/03/08/a-cornucopia-of-memory-and-bandwidth-in-the-agilex-m-fpga/1634695) |

**Reference (locked) NCE footprint:** `BGA-2500_40x40mm_P0.8mm` — 40 × 40 mm, 0.8 mm pitch,
confirmed directly from `LightRail.pretty/BGA-2500_40x40mm_P0.8mm.kicad_mod` in this repo.

Every real candidate above is **larger in both footprint area and ball pitch** than the
locked NCE site. There is no part on the market today that drops into the existing
keepout without a footprint change.

## 4. What Path B would and wouldn't validate

**Would validate on real silicon:**
- HBM channel electrical routing/topology from the compute site to U30–U35/U40–U45 (memory interface class is comparable — HBM2e/HBM3E/HBM4 share the same PHY-level channel structure, differing mainly in per-pin data rate)
- PCIe fabric routing and link-up to the PCIe slot
- Power delivery network and thermal design at 4kW+ class loads, consistent with the liquid-cooled chassis design described in the LightRail pitch deck ("100% Liquid Cooled... engineered for 4kW+ class chip demands")
- Board mechanical/assembly flow end-to-end

**Would NOT validate:**
- The TFLN direct-drive optical interface as literally specified (100+ GHz thin-film lithium niobate modulators driven directly from the compute die's SerDes). FPGA transceivers (AMD GTM 112G, Intel F-Tile/R-Tile PAM4) are standard electrical PAM4/NRZ SerDes — they do not natively drive TFLN modulators. The HXT45430-class driver ASIC at U50–U53 would still sit between the compute die and the optical engine either way, so this part of the design is testable independent of which compute die is present.
- The actual NCE die's real electrical/thermal/timing behavior — an FPGA is a stand-in, not a model of the ASIC's real silicon characteristics.

## 5. Required changes if this option is approved (not yet done)

1. Formal owner sign-off documenting the deviation: footprint change at U1/U4 from
   `BGA-2500_40x40mm_P0.8mm` to the selected real part's package (with exact P/N).
2. New footprint library entry added to `LightRail.pretty/` for the chosen part, sourced
   from the vendor's official pinout/footprint files (e.g. AMD's published
   `xcvp1902vsvb6865pkg.txt`-style pinout files, or Intel's Agilex M-Series package guide) —
   never hand-invented.
3. Placement/keepout re-check on the reference PCB for the larger footprint (up to
   70 × 70 mm vs. the current 40 × 40 mm site) — likely affects adjacent component
   clearance and may require re-running placement audit.
4. Updated BOM line replacing the NCE placeholder with the real, purchasable part number
   and vendor.
5. Re-run ERC/DRC against the modified board and document new baseline numbers (same
   honest-reporting standard used for the `ad580da`/`537b341` baselines already in this repo).
6. NCE ball map (`09_pin_complete_data/NCE_BGA2500_DRAFT_BALL_MAP.csv`) stays
   `DRAFT-PENDING-IP-OWNER-SIGNOFF` regardless — Path B does not touch or resolve that
   file. It remains gated on Path A (real RTL/floorplan/package co-design).

## 6. Rough cost/timeline shape (order-of-magnitude, not quotes)

- Devkit-based bring-up (Agilex 7 M-Series HBM2e Edition dev kit, or Versal HBM
  evaluation board): weeks, lowest cost, does not require the custom PCB change at all —
  fastest way to validate HBM/PCIe/firmware concepts before touching the locked layout.
- Custom PCB revision with the swapped footprint: real design-cycle time (placement
  re-audit, re-route of affected nets, new DRC/ERC pass, one PCB fab+assembly turn) —
  weeks to a couple of months depending on manufacturer lead time, separate from and
  much faster than the Path A full-custom-ASIC timeline.

## 7. Recommendation

Before touching the locked PCB at all, the lowest-risk first step is the **devkit path**:
bring up HBM/PCIe/firmware concepts on an off-the-shelf Agilex M-Series or Versal HBM
devkit with zero impact on the reference layout. Only if that validates useful learnings
would a custom-PCB footprint swap (Section 5) be worth the deviation-approval process.

**No action will be taken on this option without your explicit go-ahead.**

---

## 8. Decision recorded (2026-07-10)

Owner selected: **Devkit-first, no PCB change.** Approved scope is limited to bringing up HBM/PCIe/firmware concepts on an off-the-shelf devkit. No footprint deviation, no change to the locked reference layout, no change to the NCE ball map status.

### Recommended kit

AMD Versal HBM Series VHK158 Evaluation Kit (part number EK-VHK158-G), built around the VH1582 device: 32GB HBM, 112G PAM4 transceivers, PCIe Gen5x8/x16, dual QSFP-DD plus quad QSFP28, 32GB DDR4. List price 14,995 USD, 16-26 week lead time depending on distributor. [AMD VHK158 product page](https://www.amd.com/en/products/adaptive-socs-and-fpgas/evaluation-boards/vhk158.html), [product brief PDF](https://www.amd.com/content/dam/amd/en/documents/products/adaptive-socs-and-fpgas/boards-kits/product-briefs/2504082-vhk158-product-brief.pdf). Alternative: Intel Agilex 7 FPGA M-Series Development Kit, HBM2e Edition (AGM039, 4700A BGA package) if the Intel/Quartus toolchain is preferred over AMD Vivado/Vitis. [Intel product page](https://www.intel.com/content/www/us/en/products/details/fpga/development-kits/agilex/agm039.html).

### Bring-up plan (zero PCB impact)

1. Order the kit; while in transit, review the VHK158 example designs/tutorials and the board's BEAM system-controller tool.
2. Validate HBM bring-up: run the vendor reference design exercising the full 32GB HBM stack, capture bandwidth/latency numbers as a real-silicon reference point against LightRail's target memory bandwidth.
3. Validate PCIe: bring up the Gen5 x8/x16 edge-connector link to a host, confirm enumeration and sustained throughput.
4. If useful, prototype firmware/driver concepts that would eventually run against the real NCE, using the devkit as a stand-in compute target.
5. Document results in this repo (new subfolder under `13_path_b_fpga_option/`) with real captured numbers, not projections — same honest-reporting standard as the ERC/DRC baselines already committed.
6. Report findings back before any decision on whether a PCB-level footprint swap (Section 5) is worth pursuing. The locked reference layout stays untouched throughout this step.

### 8b. RISC-V architecture validation on FPGA fabric (added per owner input)

Owner confirmed the NCE core is RISC-V based, and pointed to two references: Etched's
approach of validating chip behavior on **massive FPGA clusters before silicon comes
back**, and a many-core RISC-V cluster project (bitluni's 8,192-MCU build) as an
architecture pattern. See `11_production_fab_roadmap/NCE_RISCV_CORE_IP_OPTIONS.md` for
the real core-IP options this points to (Tenstorrent TT-Ascalon/Tensix Neo, Esperanto
ET-SoC-1 pattern, SiFive Intelligence).

This step stays entirely within Path B's zero-PCB-impact scope: it uses the *programmable
logic fabric* of the same devkit(s) recommended above (Versal HBM VHK158 or Agilex M-Series),
not the hardened Arm/host processor, to synthesize an open RISC-V soft-core array and
validate the many-core architecture pattern before committing to any real RTL/tapeout
under Path A.

Real, citable prior art for this kind of FPGA-based many-core RISC-V validation:
- **GRVI Phalanx** — up to 400 RV32I RISC-V soft cores on a single Kintex UltraScale FPGA. [arXiv:1606.01037](https://arxiv.org/pdf/1606.01037.pdf)
- **HERO** (ETH Zurich) — FPGA research platform combining clusters of RISC-V soft cores with a hard ARM host processor, silicon-proven and fully reconfigurable. [HERO paper](https://iis-people.ee.ethz.ch/~andkurt/publications/carrv-hero.pdf)
- **HammerBlade** — fully open-source RISC-V manycore architecture, silicon-validated at 2,048 cores (14/16nm ASIC), with an FPGA emulation path. [Cornell HammerBlade paper](https://www.csl.cornell.edu/~zhiruz/pdfs/hammerblade-isca2024.pdf)
- **EMiX** — distributed emulation of multi-core RISC-V designs across *multiple interconnected FPGAs* when a design exceeds one board's capacity, directly mirroring Etched's "massive FPGA clusters" validation approach. [arXiv:2604.27012](https://arxiv.org/pdf/2604.27012v1.pdf)

**Suggested addition to the bring-up plan:** after single-board HBM/PCIe validation
(steps 1-4 above), if a many-core RISC-V pattern is the chosen direction, scale to
multiple networked devkits (2+ Versal/Agilex boards) using an EMiX/HERO-style
multi-FPGA partitioning approach to emulate the eventual NCE core count at real scale —
same philosophy as Etched's pre-silicon FPGA cluster validation, still zero impact on
the locked PCB since this all runs on off-the-shelf boards, not the reference layout.

---
*Prepared as a documented option per request. Sources cited inline above.*
