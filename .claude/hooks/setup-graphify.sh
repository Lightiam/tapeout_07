#!/usr/bin/env bash
# SessionStart hook: ensure the graphify CLI is available and its skill is
# registered in this session's ephemeral container. Idempotent and non-fatal.
set -u
LOG=/tmp/setup-graphify.log
exec > >(tee -a "$LOG") 2>&1

if command -v graphify >/dev/null 2>&1; then
  echo "[setup-graphify] already present: $(graphify --help 2>/dev/null | head -1)"
  exit 0
fi
command -v pip3 >/dev/null 2>&1 || { echo "[setup-graphify] no pip3; skipping"; exit 0; }

echo "[setup-graphify] installing graphifyy…"
if pip3 install -q graphifyy 2>/dev/null; then
  # register the skill for Claude (best-effort; the repo also vendors it under .claude/skills/graphify)
  graphify install --platform claude >/dev/null 2>&1 || true
  echo "[setup-graphify] done: graphify $(pip3 show graphifyy 2>/dev/null | awk '/Version/{print $2}')"
else
  echo "[setup-graphify] install failed; the vendored .claude/skills/graphify still provides the skill"
fi
exit 0
