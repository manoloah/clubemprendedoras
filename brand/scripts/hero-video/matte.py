"""Cut the hero illustration out of its fake checkerboard background.

The source MP4 (an image-to-video render) has a light-grey/white checkerboard
baked into every frame instead of real transparency. This keys it out per frame:
light, colourless pixels connected to the border (or forming gaps inside the
figure) become transparent; the cream shirt survives because it is warm, not grey.

Usage: python matte.py <frames_dir> <out_dir> <size>
Writes RGBA PNGs 000.png, 001.png, ... at <size>x<size>. See build.sh.
"""
import glob
import os
import sys

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

src, out, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
os.makedirs(out, exist_ok=True)

files = sorted(glob.glob(os.path.join(src, "*.png")))
i = 0
for f in files:
    a = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB).astype(np.int16)
    # The render's first frame shows the background as black instead of the
    # checkerboard; keying would leave a black halo, and it would flash in the loop.
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    if np.median(edge.max(1)) < 40:
        continue
    mx, mn = a.max(2), a.min(2)

    # Checkerboard candidates: near-grey and light.
    cand = ((mx - mn) <= 7) & (mn >= 222)
    lab, n = ndi.label(cand)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    # Gaps inside the figure (between an arm and a head, etc.).
    sizes = ndi.sum(cand, lab, range(1, n + 1))
    bg |= np.isin(lab, [k for k, s in enumerate(sizes, 1) if s > 90])
    # Grab the anti-aliased fringe next to the background.
    bg = (ndi.binary_dilation(bg, iterations=2) & ((mx - mn) <= 14) & (mn >= 190)) | bg

    fg = ndi.binary_opening(~bg, iterations=1)
    lab2, n2 = ndi.label(fg)
    if n2 > 1:  # drop specks
        s2 = ndi.sum(fg, lab2, range(1, n2 + 1))
        fg = np.isin(lab2, [k for k, s in enumerate(s2, 1) if s > 1500])
    holes = ndi.binary_fill_holes(fg) & ~fg  # fill tiny holes only
    hl, hn = ndi.label(holes)
    if hn:
        hs = ndi.sum(holes, hl, range(1, hn + 1))
        fg |= np.isin(hl, [k for k, v in enumerate(hs, 1) if v < 60])

    alpha = cv2.GaussianBlur(ndi.binary_erosion(fg, iterations=1).astype(np.float32), (0, 0), 0.9)
    rgba = np.dstack([a.astype(np.uint8), (alpha * 255).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").resize((size, size), Image.LANCZOS).save(os.path.join(out, f"{i:03d}.png"))
    i += 1

print(f"{i} frames -> {out}")
