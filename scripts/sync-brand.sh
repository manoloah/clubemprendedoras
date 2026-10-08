#!/usr/bin/env bash
# Keep brand/ in step with the landing. site/ is the source for the shared files:
#   tokens.css, styles.css, motion.js, assets/brand/*, assets/img/*, assets/video/*
# brand/ is the portable copy (copy that folder into a new project and it works on its own).
#
#   scripts/sync-brand.sh           copy site -> brand
#   scripts/sync-brand.sh --check   exit 1 if brand/ is behind the site (use before a PR)
#
# Files that only exist in brand/ (community illustrations, photo backgrounds, guide, docs)
# are left alone, and nothing is ever deleted.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/site/assets"
DST="$ROOT/brand/assets"
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
stale=0

sync_file() { # relative path under assets/
  local rel="$1"
  if [ ! -f "$DST/$rel" ] || ! cmp -s "$SRC/$rel" "$DST/$rel"; then
    if [ "$CHECK" = 1 ]; then echo "out of date: brand/assets/$rel"; stale=1
    else mkdir -p "$(dirname "$DST/$rel")"; cp "$SRC/$rel" "$DST/$rel"; echo "updated brand/assets/$rel"; fi
  fi
}

for f in tokens.css styles.css motion.js; do sync_file "$f"; done
while IFS= read -r f; do sync_file "${f#"$SRC/"}"; done < <(find "$SRC/brand" "$SRC/img" "$SRC/video" -type f ! -name .DS_Store | sort)

if [ "$CHECK" = 1 ]; then
  [ "$stale" = 0 ] && echo "brand/ is in step with site/" || { echo "run scripts/sync-brand.sh"; exit 1; }
else
  echo "done"
fi
