# NCE RISC-V Core IP Options — Path A Input

**Status: RESEARCH/OPTIONS DOCUMENT. Records real, current RISC-V core IP vendors and
architecture patterns to inform the NCE's eventual RTL/floorplan (Path A). Does not
select a final core, license anything, or touch any locked file. The NCE ball map stays
`DRAFT-PENDING-IP-OWNER-SIGNOFF` regardless of which core IP is eventually chosen — an
ISA/core decision is necessary but not sufficient for a real pad ring.**

Prompted by owner input: NCE is RISC-V based, plus two reference videos supplying two
different architecture philosophies worth weighing against each other.

## 1. Two philosophies from the reference material

- **bitluni's "ultra-cluster" project** (home-built GPU-style cluster of **8,192 RISC-V
  MCUs**, WCH CH570 chips, 100MHz each, controlled by 256 bigger cores with FPUs) —
  the "many cheap simple RISC-V cores" philosophy: massive core count, minimal
  per-core complexity, huge aggregate parallelism.
- **Etched (Gavin Uberti / Robert Wachen) interview** — a real, funded ($800M raised)
  AI inference chip company. Two lessons directly applicable here, independent of ISA:
  they validated chip behavior on **massive FPGA clusters before silicon came back**,
  and they treat the **whole rack (chip + board + interconnect + power) as the product**,
  not just the die — consistent with LightRail's own rack-level TFLN/CPO framing.

Both patterns point toward the same real, production RISC-V AI-core landscape below —
just at different points on the "many small cores" vs. "fewer, larger cores" spectrum.

## 2. Real, current RISC-V core IP options

| Option | What it is | Core pattern | Status |
|---|---|---|---|
| **Tenstorrent TT-Ascalon + Tensix Neo** | TT-Ascalon: out-of-order superscalar RISC-V CPU, RVA23 profile, productized as licensable IP (X and compute-dense S variants). Tensix Neo: scalable AI compute core mesh, connects over Tenstorrent's NoC. | Few high-performance RISC-V control cores + a scalable AI-compute mesh | Actively licensed — Tenstorrent licensed Ascalon to Japan's LSTC for an edge AI accelerator; also offers RISC-V CPU + Tensix + chiplet IP directly. [Tenstorrent IP](https://tenstorrent.com/en/ip), [TT-Ascalon](https://tenstorrent.com/en/ip/tt-ascalon), [AnandTech on LSTC license](https://www.anandtech.com/show/21281/tenstorrent-licenses-risc-vcpu-ip-to-build-2nm-edge-ai-accelerator) |
| **Esperanto ET-SoC-1 pattern** | Real shipping product: **1,088 low-power "ET-Minion" RISC-V cores** (each with its own vector/tensor unit) + **4 high-performance "ET-Maxion" RISC-V cores**, on one 7nm chip, ~15W, for datacenter AI inference. This is the real, production-silicon analog of bitluni's "many cheap cores" idea. | Many small RISC-V+tensor cores + a few control cores | Shipping/sampling to customers since 2022; Intel strategic partnership. [Esperanto](https://www.esperanto.ai/), [Forbes on ET-SoC-1](https://www.forbes.com/sites/karlfreund/2022/04/20/risc-v-startup-esperanto-technologies-samples-first-ai-silicon/), [Hot Chips 33 paper](https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf) |
| **SiFive Intelligence (X280/X160/X180/X390/XM Gen 2)** | RISC-V vector + matrix compute IP blocks, licensable individually, meant to be embedded as building blocks inside a custom SoC/ASIC rather than delivered as a full core+mesh package. | Building-block IP, integrator controls the array topology | Actively licensed — Sophgo licensed SiFive Performance P670 + Intelligence X280 for its SG2380 AI processor. [SiFive Intelligence](https://www.sifive.com/blog/whats-new-in-ai--ml-from-sifive), [Sophgo license](https://www.sifive.com/press/sophgo-licenses-sifive-risc-v-processor-cores-to-drive) |

## 3. Fit against LightRail's stated NCE architecture

The pitch deck describes "NCE double-GPU configurations" in a liquid-cooled, HBM4 +
TFLN-optical rack — i.e. a compute-dense AI accelerator, not a simple MCU array. Against
that framing:

- **Closest fit:** Tenstorrent TT-Ascalon (RISC-V control CPU) + Tensix Neo (AI compute
  mesh) — a proven "few control cores + scalable AI compute mesh" pattern already
  licensed by others for custom silicon, and structurally similar to what "NCE" appears
  to be from the deck (a dense AI compute die, not a many-tiny-MCU array).
- **Alternative if a many-core inference array is actually intended:** Esperanto's
  ET-SoC-1 pattern (many small vector/tensor RISC-V cores + few control cores) is the
  real, shipping proof that the bitluni-style "many cheap cores" philosophy works at
  production AI-inference scale.
- **If LightRail wants to own RTL down to the core level** rather than integrate a
  vendor's full core+mesh IP: SiFive Intelligence blocks are the most flexible
  building-block option, at the cost of more in-house design work.

This is not a recommendation to license any specific IP — it is a mapping of real
options against your stated architecture, for your decision.

## 4. What this does and doesn't unlock

Choosing a core IP path is a necessary step toward a real NCE floorplan (Path A), but
by itself does not produce a real pad ring or ball map — that still requires actual
RTL integration, synthesis, and floorplanning with the chosen IP, per the Path A steps
already documented in this repo (`11_production_fab_roadmap/README.md`,
`CODEX_PROMPT_LOCK_LAYOUT.md`). No change to the NCE ball map status follows from this
document alone.
