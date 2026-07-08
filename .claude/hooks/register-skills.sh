#!/usr/bin/env bash
# SessionStart hook: register the repo-vendored skills into the user skills dir
# so they are invocable (not just present on disk). Idempotent, non-fatal.
# Without this, .claude/skills/* in the repo are on disk but Claude may not list
# them as invocable skills (that was the "kicad-happy not in the invocation" gap).
set -u
SRC=".claude/skills"
DEST="$HOME/.claude/skills"
[ -d "$SRC" ] || exit 0
mkdir -p "$DEST"
for d in "$SRC"/*/; do
  name="$(basename "$d")"
  [ -f "$d/SKILL.md" ] || continue
  if [ ! -e "$DEST/$name" ]; then
    cp -r "$d" "$DEST/$name" && echo "[register-skills] registered: $name"
  fi
done
exit 0
