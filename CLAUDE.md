# CLAUDE.md

Working notes for Claude Code in this repo. Human-facing overview: `README.md`.

## Project

Waitlist landing for **El Club de las Emprendedoras** (Pame and Manu, @emprendeconpm): an 8-week
taller in 2027 where non-technical women turn an idea into a mobile app with AI. The only
conversion is the waitlist form. Audience: Spanish-speaking women in Mexico/LATAM, 28–42, not
technical, reading on their phone from Instagram.

## Commands

```bash
npx serve -l 4173 site                                   # local preview (also .claude/launch.json "landing")
node scripts/rank-hero.mjs                               # score hero copy; needs TYPESAFE_API_KEY in .env.local
scripts/hero-video/build.sh path/to/render.mp4           # rebuild site/assets/video/club-women.mp4
OUT=/tmp/test.mp4 scripts/hero-video/build.sh render.mp4 # same, without touching the repo file
```

No build step, no package.json, no tests. `site/` is deployed as-is to Vercel (see Workflow).

## Layout

- `site/index.html`: all copy and markup.
- `site/assets/tokens.css`: design tokens, mirroring Figma variables. Components use the semantic roles (`--surface-*`, `--brand-*`, `--text-*`), never the primitives.
- `site/assets/styles.css`: components and layout, mobile first, desktop at `@media (min-width: 900px)`. The motion block sits near the end, before the reduced-motion block.
- `site/assets/app.js`: waitlist form (validation, honeypot, UTM capture, success state, step-2 profile modal).
- `site/assets/motion.js`: every animation, plus the hero video's WebGL compositing.
- `site/assets/config.js`: Apps Script `/exec` endpoint. Public by design.
- `sheets/Code.gs`: the Apps Script. It isn't deployed from here; it gets pasted into the Sheet (see `sheets/README.md`).

## Conventions

- **Copy:** Mexican Spanish, informal *tú*, warm and direct, written to women. No hype, no get-rich-quick, no tech jargon. If the `emprendeconpm-brand-nuevo` skill is available, use it for brand and copy rules.
- **Design:** class names map 1:1 to Figma components (table in `site/README.md`). Nothing is perfectly straight: tilts use the CSS `rotate` property (`.tilt-l`, `.tilt-r`, per-element `rotate:`).
- **Cache busting:** `index.html` loads `styles.css?v=N`, `app.js?v=N`, `config.js?v=N` and `motion.js?v=N`. Bump N whenever you change that file, or returning visitors keep the old one.
- **Keep it static:** no frameworks or bundlers in `site/`. Images are WebP; keep the page light.

## Motion rules (learned the hard way)

- Transforms are split across properties so they compose. Tilts use `rotate`, idle loops (bob, breathe, hop) animate `translate`/`scale`, and scroll reveals and the ideas heap use `transform`. Don't animate `rotate` on an element that already has a tilt.
- Hidden "before" states exist only under `html.motion`, which `motion.js` adds last. Without JS, or with `prefers-reduced-motion: reduce`, the page is fully static and visible.
- **Nothing may widen the page.** `main > section, .footer { overflow-x: clip }` contains the ideas heap and offset photos. On phones, any overflow makes the browser lay out wider and cuts off the nav. Check that `document.documentElement.scrollWidth === innerWidth` at 320, 393 and 1280px.
- The hero phrase "cero a emprendedora" is `nowrap` (one line, underlined), so `.hero .display` sizes from the column with container units (`9.2cqi`, about 10.5em of phrase width). `.underline` must stay `inline-block`: WebKit gives its `::after` zero width on an inline box.
- Ideas heap (`.chips`): JS measures each chip's slot with `offsetLeft`/`offsetTop`, which ignore transforms, and offsets it into a heap about 150px below the list top. It sorts when that point is inside the top 85% of the viewport.

## Hero video

- `club-women.mp4` is stacked alpha: 1280x640 H.264, colour on the left half (premultiplied on black), mask as grey on the right, a ping-pong loop of 238 frames at 24fps. `motion.js` draws it into a WebGL canvas placed over the static `club-women.webp`, under the stickers.
- It starts once the art is on screen *and* 0.2s have passed. Safari won't autoplay a video that's off screen or under an opacity-0 ancestor, so refused `play()` calls are retried. The video is created muted (attribute plus `defaultMuted`) before `src` is set.
- It only works over http(s). From `file://`, WebGL refuses the video's pixels (SecurityError) and the page keeps the static image, logging `[hero] …` to the console. Safari also needs a server with Range requests: `python3 -m http.server` won't do.
- The source render has a fake grey/white checkerboard baked in and a black first frame. `scripts/hero-video/matte.py` keys out the checkerboard and skips the black frame. VP9-alpha WebM and HEVC-alpha were tried first: HEVC alpha from ffmpeg came out without an alpha layer, and the split formats meant Safari couldn't be verified, which is why we use one stacked file.

## Testing

- Check layout and motion in both Chromium and WebKit at iPhone SE (320), iPhone 15 (393) and desktop (1280), served over http. Playwright works well for this (`devices["iPhone 15"]`).
- Playwright's WebKit blocks muted autoplay unless there's a user gesture, even on a plain `<video autoplay muted>`. A static hero there is a false negative; `page.evaluate` counts as a gesture.
- **The form posts to the live Sheet,** including from localhost. Don't submit test sign-ups unless you mean to, or point `config.js` at an empty endpoint locally. With no endpoint set, localhost logs the payload to the console.

## Waitlist backend

- Field names (`name`, `email`, honeypot `company`, profile fields in the modal) must match `COLUMNS` in `sheets/Code.gs`. Change both together, and remember the script has to be redeployed in Apps Script (new version, same `/exec` URL).
- The endpoint can only add a row or fill empty cells, and it never returns data. Spam fallback if needed: Cloudflare Turnstile.

## Workflow

- One feature branch per change, opened as a PR against `main`.
- **Deploys:** Vercel project `clubemprendedoras` (team `manolo96035-6430s-projects`, id `prj_2wdMdohpqhJ8QiIjznXfhaD8cN7l`), Git-linked, root directory `site/`. Merging to `main` deploys production at https://clubemprendedoras.vercel.app; other branches get preview URLs, which may be behind Vercel login. Config: `site/vercel.json` (no build, headers) and `site/.vercelignore`.
- After a deploy, check the live site the same way as local (Playwright at 320/393/1280), and confirm the video answers a Range request with `206`.
- `.DS_Store` files are tracked even though `.gitignore` lists them. Don't stage their changes (`git checkout -- .DS_Store`).
- Secrets live only in `.env.local` (gitignored), e.g. `TYPESAFE_API_KEY`.
