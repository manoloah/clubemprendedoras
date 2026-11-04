#!/bin/sh
# Renders og.html (1200x630) to site/assets/img/og-curso.jpg with headless Chrome.
# Usage: brand/scripts/og/build.sh   (then scripts/sync-brand.sh)
# A new design should get a new file name: WhatsApp, Instagram and Facebook
# cache link previews by URL, so updating og-curso.jpg in place may not show.
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
TMP=$(mktemp -d)
sed "s#SITE/#file://$ROOT/site/#g" "$ROOT/brand/scripts/og/og.html" > "$TMP/og.html"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --hide-scrollbars --allow-file-access-from-files --virtual-time-budget=6000 \
  --window-size=1200,630 --force-device-scale-factor=1 --user-data-dir="$TMP/chrome" \
  --screenshot="$TMP/og.png" "file://$TMP/og.html" 2>/dev/null
sips -s format jpeg -s formatOptions 85 "$TMP/og.png" --out "$ROOT/site/assets/img/og-curso.jpg" >/dev/null
rm -rf "$TMP"
echo "site/assets/img/og-curso.jpg"
