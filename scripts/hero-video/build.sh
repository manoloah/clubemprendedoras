#!/usr/bin/env bash
# Rebuild site/assets/video/club-women.mp4 from a source MP4.
#
#   scripts/hero-video/build.sh path/to/source.mp4
#
# Output is a "stacked alpha" H.264: colour on the left half, the alpha matte
# (as grey) on the right, 640px each, played forward then backward so it loops
# without a jump. site/assets/motion.js turns it back into transparency in WebGL.
#
# Needs: ffmpeg, python3. Python deps go into a throwaway venv in the temp dir.
set -euo pipefail

SRC="${1:?usage: build.sh source.mp4}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${OUT:-$ROOT/site/assets/video/club-women.mp4}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "→ extracting frames"
mkdir -p "$WORK/frames"
ffmpeg -v error -i "$SRC" -map 0:v:0 "$WORK/frames/%03d.png"

echo "→ removing the checkerboard background"
python3 -m venv "$WORK/venv"
"$WORK/venv/bin/pip" install -q numpy scipy pillow opencv-python-headless
"$WORK/venv/bin/python" "$(dirname "$0")/matte.py" "$WORK/frames" "$WORK/matte" 720

echo "→ encoding stacked-alpha ping-pong loop"
N=$(ls "$WORK/matte" | wc -l | tr -d ' ')
ffmpeg -v error -y -framerate 24 -i "$WORK/matte/%03d.png" -f lavfi -i "color=c=black:s=640x640:r=24" \
  -filter_complex "[0:v]scale=640:640:flags=lanczos,format=rgba,split[c][m0];\
[m0]alphaextract,format=yuv420p[m];\
[1:v][c]overlay=shortest=1,format=yuv420p[col];\
[col][m]hstack,split[a][b];\
[b]reverse,trim=start_frame=1:end_frame=$((N - 1)),setpts=PTS-STARTPTS[r];\
[a][r]concat=n=2:v=1:a=0[o]" \
  -map "[o]" -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -movflags +faststart -an "$OUT"

ls -lh "$OUT"
echo "Done. Bump the ?v= on motion.js in site/index.html only if motion.js changed;"
echo "for a new video, rename the file or add a query string in motion.js so browsers refetch it."
