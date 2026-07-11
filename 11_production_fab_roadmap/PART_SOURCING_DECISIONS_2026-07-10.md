# Part Sourcing Decisions — 2026-07-10

Decision owner: Bola Olatunji (LightRail AI Labs). Recorded here so the
sourcing rationale travels with the repo instead of living only in chat.

## Layout: locked, zero deviation

`TFLN_AI_NODE_X2_REFERENCE.kicad_pcb` is the final physical layout target.
Placement, footprint outlines, and topology are not to be changed. The work
remaining is making every net in that layout electrically real.

## 1. NCE compute die (U1/U4, BGA-2500 footprint)

- **Status:** LightRail's own proprietary NCE ASIC. Not yet taped out.
- **Decision:** No vendor ball map exists and none may be invented as final.
  A DRAFT ball map will be generated from the known system architecture (the
  22-layer intelligence stack: HBM4 channels, TFLN/optical SerDes lanes,
  PCIe/fabric lanes, power/ground per BGA-2500 JEDEC-style grid conventions),
  tagged `DRAFT — PENDING IP OWNER SIGNOFF` in every file it touches, until
  Bola approves or corrects it against the real NCE design intent.

## 2. HBM4 (U30–U35, U40–U45)

- **Market reality:** Samsung, SK hynix, and Micron's entire 2026 HBM4 output
  is allocated to hyperscale customers (NVIDIA/AMD-class volume). Micron has
  publicly stated its 2026 capacity is sold out, and NVIDIA has certified all
  three suppliers specifically for its Vera Rubin platform — there is no open
  retail/small-quantity channel for raw HBM4 dies right now.
  ([TrendForce](https://www.trendforce.com/news/2026/01/09/news-nvidia-demand-fuels-hbm4-race-12-layer-ramps-16-layer-push-by-sk-hynix-samsung-and-micron/),
  [Yahoo Finance / Investing.com](https://finance.yahoo.com/sectors/technology/articles/nvidia-certifies-samsung-sk-hynix-133001560.html))
- **Decision:** Populate with **HBM3E** as a pin-compatible prototype
  substitute for this build, tagged `SUBSTITUTE PENDING HBM4 ALLOCATION` in
  the BOM. Pull the real vendor ball/channel map for the exact HBM3E MPN used
  and match footprints to it precisely.
- **Path to real HBM4 later:** engage through an ASIC design-services house
  that already holds HBM4 PHY IP licenses and vendor relationships (e.g. GUC,
  Alchip, Faraday) rather than approaching Samsung/SK hynix/Micron directly —
  they are a realistic channel to real package data without hyperscaler-scale
  volume commitments.

## 3. TFLN PIC module (U3)

- **Primary target:** **HyperLight** — the most commercially mature TFLN
  modulator/driver vendor, with real shippable products and established
  high-speed optical supply relationships.
  ([optics.org](https://optics.org/news/hyperlight-looks-to-scale-thin-film-lithium-niobate-with-taiwan-foundries))
- **Fallback if small-quantity sampling isn't available:** Ligentec/CSEM
  (custom PIC foundry run) or POET Technologies (photonic interposer
  approach).
  ([360iResearch TFLN foundry list](https://www.360iresearch.com/library/intelligence/tfln-photonic-chip-foundry))
- **Decision:** Request the datasheet pad map for the specific module SKU
  from whichever vendor is confirmed, and update the U3 footprint/pinout to
  match exactly.

## 4. Rail/lane/clock/reset allocation

- **Decision:** Derive the full power tree, PCIe/fabric lane map, clock plan,
  and reset/sequencing table consistent with the draft NCE map (item 1) and
  the real HBM3E/TFLN pinouts (items 2–3). Tag this DRAFT as well, pending
  IP-owner signoff, since it depends on item 1.

## 5. HMC8410 correction

- **Status:** Confirmed function/package mismatch — HMC8410 is a 6-lead 2mm
  LFCSP low-noise amplifier, not a driver/modulator interface part.
- **Decision:** Replace with a real TFLN driver/modulator-interface IC
  (search Analog Devices / MACOM for a bandwidth/voltage-swing/package match),
  update symbol, footprint, BOM, and nets.

## What "fab-ready" requires before this is called done

The board may not be marked fab-ready in any status file until the NCE ball
map row moves from `DRAFT` to IP-owner-approved. Every other item above can
reach a real, verified state without further IP-owner input once the vendor
data requests are answered.
