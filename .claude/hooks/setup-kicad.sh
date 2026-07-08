#!/usr/bin/env bash
# SessionStart hook: ensure KiCad 9 (kicad-cli) is available in this session's
# ephemeral container. Idempotent and non-fatal — if anything fails (e.g. no
# network) it logs and exits 0 so the session still starts.
#
# Installs KiCad 9.0.x from the official Launchpad PPA (matches this project's
# board generator, KiCad 9.0.9). Headless: --no-install-recommends, no GUI use.
set -u
LOG=/tmp/setup-kicad.log
exec > >(tee -a "$LOG") 2>&1

if command -v kicad-cli >/dev/null 2>&1; then
  echo "[setup-kicad] kicad-cli already present: $(kicad-cli version 2>/dev/null)"
  exit 0
fi

# Only attempt on Debian/Ubuntu with apt.
command -v apt-get >/dev/null 2>&1 || { echo "[setup-kicad] no apt-get; skipping"; exit 0; }

echo "[setup-kicad] installing KiCad 9 (kicad-cli)…"
. /etc/os-release 2>/dev/null || true
CODENAME="${UBUNTU_CODENAME:-noble}"

# Add the KiCad 9 PPA with its signing key (avoids add-apt-repository, which can
# be broken by a missing apt_pkg module in some minimal images).
if [ ! -f /etc/apt/sources.list.d/kicad-9.list ]; then
  FP=$(curl -fsSL --max-time 20 \
      "https://api.launchpad.net/1.0/~kicad/+archive/ubuntu/kicad-9.0-releases" \
      | python3 -c "import sys,json;print(json.load(sys.stdin)['signing_key_fingerprint'])" 2>/dev/null)
  if [ -z "${FP:-}" ]; then echo "[setup-kicad] could not fetch PPA key fingerprint; skipping"; exit 0; fi
  mkdir -p /etc/apt/keyrings
  curl -fsSL --max-time 20 "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x${FP}" \
      | gpg --dearmor -o /etc/apt/keyrings/kicad-9.gpg || { echo "[setup-kicad] key import failed; skipping"; exit 0; }
  echo "deb [signed-by=/etc/apt/keyrings/kicad-9.gpg] https://ppa.launchpadcontent.net/kicad/kicad-9.0-releases/ubuntu ${CODENAME} main" \
      > /etc/apt/sources.list.d/kicad-9.list
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -y || echo "[setup-kicad] apt-get update returned non-zero (continuing)"
if apt-get install -y --no-install-recommends kicad; then
  echo "[setup-kicad] done: $(kicad-cli version 2>/dev/null)"
else
  echo "[setup-kicad] kicad install failed; see $LOG"
fi
exit 0
