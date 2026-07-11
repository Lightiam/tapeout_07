# Generic-Parts POC Sourcing Option

**Status: proposal only. No locked files modified. Nothing ordered.**

## 0. Framing (per owner instruction, 2026-07-10)

> "I am building an MVP, the next iteration will be costly but this time, it is simply a POC."
> "Cant we buy generic parts since we already have a manufacturer? and just brand it — I still want to stick to the ASIC plan NCE."

This document treats the ask strictly as **internal engineering validation hardware for an MVP/POC** — not as a substitute chip to be presented externally as the real NCE. The standing rules from `13_path_b_fpga_option/PATH_B_FPGA_SWAP_OPTION.md` still apply unchanged:

- The NCE (BGA-2500, U1/U4) is LightRail's own proprietary ASIC, not taped out. No generic part is "the NCE" or gets called that in any spec, deck, or customer-facing material.
- No generic part validates the TFLN direct-drive optical interface — pluggable optics below are standard PAM4 electrical-to-optical modules, not lithium-niobate direct-drive modulators. The HXT45430-class driver stays in the real design regardless.
- This is a **cheaper alternative Path B target**, not a change to the locked `TFLN_AI_NODE_X2_SERVER_CHASSIS_IO` layout or the ball-map draft status.

The manufacturer identity referenced by the owner ("we already have a manufacturer") was not resolved in conversation — the options below are all orderable directly from AMD or standard electronics distributors (Avnet, Arrow, Mouser, Digi-Key), so no specific manufacturer relationship is required to act on this.

## 1. Why generic parts, and what changes vs. the VHK158 plan

Section 8 of `PATH_B_FPGA_SWAP_OPTION.md` recommended the AMD Versal HBM VHK158 Evaluation Kit ($14,995, 16–26 week lead time) as the devkit-first validation target. For a POC (vs. a fuller pre-tapeout validation), a smaller AMD Alveo HBM2-based accelerator card is a legitimate, much cheaper stand-in that still exercises the same three things Path B cares about: real HBM silicon behind a compute fabric, PCIe host interface, and pluggable-optics networking — at a fraction of the cost and lead time, and all in-stock through normal distribution rather than a 4-6 month order.

## 2. Compute + HBM card options (cheapest to most capable)

All are real AMD/Xilinx UltraScale+ or Versal parts with genuine HBM2 on-die — not simulated or "generic" memory. Prices are current AMD direct-store list prices.

| Card | Price | FPGA | HBM2 capacity / bandwidth | PCIe | Network I/O | Form factor | Power |
|---|---|---|---|---|---|---|---|
| **Alveo U50** | **$2,965** ([AMD store](https://shop-us-en.amd.com/adaptive-embedded-computing/data-center-accelerator-cards/), part A-U50-P00G-PQ-G) | UltraScale+ XCU50, 872K LUTs | 8 GB / 316 GB/s peak (201 GB/s nominal) | Gen3 x16, 2×Gen4 x8, CCIX | 1× QSFP28 (100GbE) | Half-height, half-length, single slot | 75W max, passive |
| **Alveo U55C** | **$4,747** (part A-U55C-P00G-PQ-G) | Virtex UltraScale+ XCU55C, 1,304K LUTs | 16 GB / 460 GB/s | Gen3 x16, 2×Gen4 x8 | 2× QSFP28 (100GbE each, 200Gb/s total) | Full-height, half-length, single slot | 150W max / 115W typical, passive |
| **Alveo V80** | **$9,495** (part A-V80-P64G-PQ-G) | Versal HBM (AI Engines + FPGA fabric) | 32 GB HBM2e (highest of the Alveo line) | PCIe Gen5 | Multiple high-speed network ports | Full-height, full-length | Active cooling |
| **VCK5000** | **$13,195** (part DK-VCK5000-G-ED) | Versal AI Core (AI Engines + FPGA fabric, no HBM) | — (no HBM; DDR only) | PCIe Gen4 | Network-capable | Full-height | Active cooling |
| VHK158 (existing plan) | $14,995 | Versal HBM VH1582 | 32 GB / full Versal HBM bandwidth class | PCIe Gen5 x8/x16 | Dual QSFP-DD + quad QSFP28 | Eval-kit chassis | 16–26 wk lead time |

Sources: [AMD Alveo U55C data sheet DS978](https://docs.amd.com/r/en-US/ds978-u55c/Product-Details), [AMD U55C product page](https://www.amd.com/en/products/accelerators/alveo/u55c/a-u55c-p00g-pq-g.html), [AMD Alveo U50 data sheet DS965](https://docs.amd.com/r/en-US/ds965-u50/Product-Details), [AMD data center accelerator cards store listing](https://shop-us-en.amd.com/adaptive-embedded-computing/data-center-accelerator-cards/), [ServeTheHome U50 review](https://www.servethehome.com/xilinx-alveo-u50-fpga-card-for-data-center-acceleration/).

**Recommendation for a first POC pass: Alveo U55C ($4,747).** It's the best balance — real 16GB HBM2 at 460GB/s (same bandwidth class as the U50/V80, double the U50's capacity), dual 100G QSFP28 ports for the optical-interconnect stand-in below, PCIe Gen4, and it's a standard in-stock catalog part (no 4-6 month wait). Both AMD's own Vitis/Vivado tooling and the same open-source RISC-V soft-core approach documented in Section 8b of `PATH_B_FPGA_SWAP_OPTION.md` (GRVI Phalanx, HammerBlade-style many-core, etc.) apply directly — the U55C's UltraScale+ fabric (1,304K LUTs) is comparable in FPGA fabric size to what those projects target.

If budget allows a bit more headroom for a second, more capable POC unit later, **Alveo V80 ($9,495)** is the next step up (32GB HBM2e, PCIe Gen5) before jumping to the full VHK158.

## 3. Generic optical-interconnect stand-in (TFLN placeholder)

None of these are TFLN or direct-drive photonics — they are standard pluggable transceivers that let the POC demonstrate "optical networking between nodes" at the systems level while the real TFLN engine remains a separate, unvalidated-by-this-POC workstream.

| Option | Price | Speed | Notes |
|---|---|---|---|
| Standard QSFP28 100G optical module | ~$100–300 (typical distributor pricing) | 100GbE | Drops directly into the U50/U55C's onboard QSFP28 cages — no extra hardware needed |
| Asterfusion 800G QSFP-DD 2FR4 module | **$1,480** ([Asterfusion](https://cloudswit.ch/product/qsfdd-800g-2fr4-sm-optical-transceiver-module/)) | 800G | For a higher-bandwidth stand-in if the POC wants to gesture at the eventual 800G+ per-lane target |
| Intel Silicon Photonics 400G DR4 QSFP-DD | list via Intel/distributor ([Intel product page](https://www.intel.com/content/www/us/en/products/sku/135329/intel-silicon-photonics-400g-dr4-qsfpdd-optical-transceiver/ordering.html)) | 400G | Actual silicon-photonics (not TFLN) — closest "generic photonics" analog available off the shelf, useful if you want the POC to at least be photonics-based rather than pure copper/VCSEL |

Since the Alveo U50/U55C already expose QSFP28 cages on-card, the cheapest path is simply a standard 100G QSFP28 optical module or DAC cable — no separate optical dev board is needed for the POC.

## 4. Suggested POC bill of materials (first pass)

| Item | Price | Purpose |
|---|---|---|
| AMD Alveo U55C | $4,747 | Compute + real HBM2 + dual 100G optical I/O |
| 2× QSFP28 100G optical modules | ~$200–600 | Populate both onboard ports for the optical-interconnect demo |
| Host server / workstation with open PCIe Gen3/4 x16 slot | (assume already available) | Card host |
| **Total incremental hardware** | **~$5,000–5,500** | vs. $14,995 for the VHK158 kit alone |

This is roughly a third of the VHK158 cost, ships from stock rather than a 16–26 week lead time, and still exercises real HBM + PCIe + optical networking for the POC narrative — with the same "not the real NCE, not the real TFLN" caveats carried over from Path B.

## 5. What this does and doesn't prove (same caveat structure as Path B)

**Validates:**
- Host software / driver bring-up against a real HBM-backed PCIe accelerator
- RISC-V soft-core synthesis and bring-up on FPGA fabric (per Section 8b's many-core approach)
- Basic optical-networking-between-nodes demo using standard pluggable optics

**Does not validate:**
- The actual NCE ASIC (still not taped out — this remains proprietary, unbuilt silicon)
- TFLN direct-drive modulation (pluggable optics are conventional PAM4 electrical-to-optical, not lithium-niobate)
- The locked board layout, footprint, or ball map in any way — this is a separate devkit-based sandbox, not a PCB change

## 6. Open items

- **Manufacturer identity:** still unresolved which "manufacturer we already have" the owner meant. Not required to act on this option (AMD direct store + standard distributors cover it), but worth clarifying if there's an existing purchasing relationship/discount to route through.
- **No order has been placed.** This document is sourcing research only, per standing policy that any purchase needs explicit execution instructions plus payment/shipping/checkout method.
