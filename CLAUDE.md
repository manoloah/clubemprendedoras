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
brand/scripts/hero-video/build.sh path/to/render.mp4           # rebuild brand/assets/video/club-women.mp4 and copy it to site/
OUT=/tmp/test.mp4 brand/scripts/hero-video/build.sh render.mp4 # same, without touching the repo files
scripts/sync-brand.sh --check                            # is brand/ in step with site/? (drop --check to copy)
.venv/bin/python newsletter/newsletter.py news           # newsletter: this week's news (see newsletter/README.md)
```

No build step, no package.json, no tests. `site/` is deployed as-is to Vercel (see Workflow).

## Layout

- `site/index.html`: all copy and markup.
- `site/assets/tokens.css`: design tokens, mirroring Figma variables. Components use the semantic roles (`--surface-*`, `--brand-*`, `--text-*`), never the primitives.
- `site/assets/styles.css`: components and layout, mobile first, desktop at `@media (min-width: 900px)`. The motion block sits near the end, before the reduced-motion block.
- `site/assets/app.js`: waitlist form (validation, honeypot, UTM capture, success state, step-2 profile modal).
- `site/assets/motion.js`: every animation, plus the hero video's WebGL compositing.
- `site/assets/config.js`: Apps Script `/exec` endpoint. Public by design.
- Nav: logo, a **Menú** dropdown (`<details data-menu>`, same markup on the landing and every receta page) and **Unirme**. The menu has one option on purpose: Recetas de Emprendimiento e IA (`/recetas/`). Close logic lives in both `app.js` and `recetas.js`.
- `site/recetas/`: "Recetas de Emprendimiento e IA" (our tutorials; never call them tutoriales in copy). Hub `index.html`, one folder per receta, `recetas.json` for the newsletter. Pages use absolute `/assets/...` paths. `site/assets/recetas.js` runs the signup gate and "Copiar" buttons. How to add one: `site/recetas/README.md`.
- `brand/`: the brand system (`voice.md`, `foundations.md`, `components.md`, `motion.md`) and a living style guide, `brand/index.html`, rendered with its own copy of the CSS/JS. Not deployed. It is a self-contained, copy-paste folder (`brand/assets/` holds tokens, styles, motion.js, logos, images and the hero video). `site/` is the source for the shared files: after changing `site/assets/{tokens.css,styles.css,motion.js}` or its `brand/`, `img/` or `video/` files, run `scripts/sync-brand.sh`. Preview: `.claude/launch.json` "brand" (port 4180, serves `brand/`). Keep the docs in step when copy, tokens or components change.
- `newsletter/`: weekly Wednesday 08:00 newsletter via Resend Broadcasts (`newsletter.py`, issues in `newsletter/issues/`, the routine in `ROUTINE.md`, process in `README.md`). The recetas (our name for tutorials) it features are listed in `site/recetas/recetas.json`. Secrets in `.env`; Python deps in `.venv`.
- `sheets/Code.gs`: the Apps Script. It isn't deployed from here; it gets pasted into the Sheet (see `sheets/README.md`).

## Conventions

- **Copy:** Mexican Spanish, informal *tú*, warm and direct, written to women. No hype, no get-rich-quick, no tech jargon. Voice and the current copy bank: `brand/voice.md`. (The `emprendeconpm-brand-nuevo` skill is a different brand, "Club de Fundadoras"; don't use it here.)
- **Design:** class names map 1:1 to Figma components (table in `site/README.md`). Nothing is perfectly straight: tilts use the CSS `rotate` property (`.tilt-l`, `.tilt-r`, per-element `rotate:`).
- **Cache busting:** `index.html` loads `tokens.css?v=N`, `styles.css?v=N`, `app.js?v=N`, `config.js?v=N` and `motion.js?v=N`. Bump N whenever you change that file, or returning visitors keep the old one.
- **Keep it static:** no frameworks or bundlers in `site/`. Images are WebP; keep the page light.

## Creating a receta

Use the project skill **`/nueva-receta`** (`.claude/skills/nueva-receta/`): it walks the whole flow and its script scaffolds (`receta.mjs new <slug>`) and checks (`receta.mjs check <slug>`) a receta. The steps live in `site/recetas/README.md` ("Creating a new receta"). The checklist:

- Copy rewritten in the club's voice from the user's draft: keep every fact, link and number, explain or drop jargon, **no kitchen puns** (no ingredientes/hornear/probadita/cocina; Gen Z and direct instead), no hype.
- **Readers are not technical at all** (no terminal, no installs). Any technical step (installing a program, running a command, cloning a repo) goes inside the prompt: she pastes the GitHub/tool link and asks Claude Code or Cowork to do it, and only gives the inputs that are really hers (her idea, her link, her files).
- **Prompts stay general so the AI does the thinking:** point Claude at her data and let it read the columns, pick the charts, take the brand from her website link, etc. Don't make her describe columns, currencies, colours or a list of visualizations; give a goal and a frame ("piensa como el CFO de [empresas que te inspiren]").
- UI how-tos use real screenshots of the Claude app (the user's, or taken with the built-in browser), not mock-ups.
- Screenshots go in `.shot` figures, never bare `<img>`: `.shot` (360px max), `.shot--sm` (260px, tall menus), `.shot--wide` (520px), with a `<figcaption>`; several in a row inside `.shots`. Otherwise they blow up to full column width on desktop.
- New folder `site/recetas/<slug>/` copied from `reel-con-claude-cowork/`: head tags, hero, `.ingredientes` ("Lo que necesitas", public), steps in `.receta__locked` with the first `id="paso-1"`, `data-gate="receta-<slug>"`. Reuse the existing building blocks (`.check-list`, `.frases`, `.prompt` + `data-copy`, `.bubbles`, `.note`, `.receta-ojo`) before adding CSS.
- Hub card at the top of `.receta-list` (alternate pink/lilac/butter, cover in `.receta-cover`), and update the "La receta #N llega…" note.
- Entry appended to `site/recetas/recetas.json` (the newsletter reads it).
- Test at 393 and 320 (plus 1280), gated and with `?utm_source=newsletter`; stub `fetch` before submitting the gate.
- Merge before the Tuesday 17:00 routine. The menu stays one option (the hub) until the user adds more.

## Recetas gate

- An inline script in each receta's `<head>` adds `html.is-gated` before paint unless the URL has `utm_source=newsletter` or `localStorage.club_receta_ok === "1"` (set by the gate, by a landing sign-up, or by a newsletter visit). Gated content is `.receta__locked` (blurred, clipped) with the `.gate` signup card over it.
- The gate posts the same payload as the waitlist (`nombre`, `email`, `source: receta-<slug>`, UTMs) to the Apps Script. Members re-enter their email to unlock: the Sheet dedups and never overwrites. Don't add an "is this email on the list?" endpoint; the backend never returns data.
- `newsletter.py build` appends `utm_source=newsletter&utm_medium=email&utm_campaign=<issue>` to every link to our domain, which is what skips the gate.
- Testing the gate locally posts to the live Sheet. Stub `window.fetch` in the page first.

## Motion rules (learned the hard way)

Durations, staggers and curves are tokens in `tokens.css` (`--dur-*`, `--stagger-*`, `--ease-*`); add a token before using a new value. The pattern catalogue is `brand/motion.md`.

- Transforms are split across properties so they compose. Tilts use `rotate`, idle loops (bob, breathe, hop) animate `translate`/`scale`, and scroll reveals and the ideas heap use `transform`. Don't animate `rotate` on an element that already has a tilt.
- Hidden "before" states exist only under `html.motion`, which `motion.js` adds last. Without JS, or with `prefers-reduced-motion: reduce`, the page is fully static and visible.
- **Nothing may widen the page.** `main > section, .footer { overflow-x: clip }` contains the ideas heap and offset photos. On phones, any overflow makes the browser lay out wider and cuts off the nav. Check that `document.documentElement.scrollWidth === innerWidth` at 320, 393 and 1280px.
- The hero phrase "cero a emprendedora" is `nowrap` (one line, underlined), so `.hero .display` sizes from the column with container units (`9.2cqi`, about 10.5em of phrase width). `.underline` must stay `inline-block`: WebKit gives its `::after` zero width on an inline box.
- Ideas heap (`.chips`): JS measures each chip's slot with `offsetLeft`/`offsetTop`, which ignore transforms, and offsets it into a heap about 150px below the list top. It sorts when that point is inside the top 85% of the viewport.

## Hero video

- `club-women.mp4` is stacked alpha: 1280x640 H.264, colour on the left half (premultiplied on black), mask as grey on the right, a ping-pong loop of 238 frames at 24fps, H.264 High level 4.0. `motion.js` draws it into a WebGL canvas placed over the static `club-women.webp`, under the stickers.
- It's drawn from a plain `requestAnimationFrame` loop, because `requestVideoFrameCallback` may not fire for a video that isn't itself on screen.
- It starts once the art is on screen *and* 0.2s have passed. Safari won't autoplay a video that's off screen or under an opacity-0 ancestor, so refused `play()` calls are retried. The video is created muted (attribute plus `defaultMuted`) before `src` is set.
- **iPhones refuse H.264 above level 5.x** with `video error code=4` (not supported), in Safari and Chrome alike, while desktop browsers play it fine. x264 picked level 6.2 on its own, so `build.sh` now pins `-profile:v high -level:v 4.0` and a constant 24fps. Check with `ffprobe -show_entries stream=level` (expect `40`).
- When the video file changes, bump the `?v=` on the video URL in `motion.js`: images and video are cached for a day.
- Open the page with `?debug` to get an on-screen log of play attempts, video events and frames drawn. Screenshot it on a real phone; no cable needed.
- If autoplay is refused (iPhone Low Power Mode blocks all autoplay), the first tap anywhere starts the video.
- It only works over http(s). From `file://`, WebGL refuses the video's pixels (SecurityError) and the page keeps the static image, logging `[hero] …` to the console. Safari also needs a server with Range requests: `python3 -m http.server` won't do.
- The source render has a fake grey/white checkerboard baked in and a black first frame. `brand/scripts/hero-video/matte.py` keys out the checkerboard and skips the black frame. VP9-alpha WebM and HEVC-alpha were tried first: HEVC alpha from ffmpeg came out without an alpha layer, and the split formats meant Safari couldn't be verified, which is why we use one stacked file.

## Testing

- **Always test at phone size.** Every visual check, including screenshots, happens with the viewport at 393x852 (iPhone 15), and again at 320 for tight layouts; desktop (1280) is only a final sanity check. The built-in browser works: `resize_window` to 393x852 before looking, and take the screenshot at that size. Wait ~10s after loading, because the intro animation delays the hero.
- Check layout and motion in both Chromium and WebKit at iPhone SE (320), iPhone 15 (393) and desktop (1280), served over http. Playwright works well for this (`devices["iPhone 15"]`).
- Playwright's WebKit blocks muted autoplay unless there's a user gesture, even on a plain `<video autoplay muted>`. A static hero there is a false negative; `page.evaluate` counts as a gesture.
- **Video can't be tested on protected Vercel previews from an iPhone:** iOS fetches media through a separate player that doesn't send the share-link cookie, so the MP4 request is redirected to Vercel login and fails with error 4. Test video on production (or a public URL).
- **The form posts to the live Sheet,** including from localhost. Don't submit test sign-ups unless you mean to, or point `config.js` at an empty endpoint locally. With no endpoint set, localhost logs the payload to the console.

## Waitlist backend

- Field names (`name`, `email`, honeypot `company`, profile fields in the modal) must match `COLUMNS` in `sheets/Code.gs`. Change both together, and remember the script has to be redeployed in Apps Script (new version, same `/exec` URL).
- The endpoint can only add a row or fill empty cells, and it never returns data.
- Apps Script deployments: update the existing one (Deploy → Manage deployments → pencil → Version: New version). "New deployment" makes a new `/exec` URL, which then has to go into `config.js` (and bump its `?v=`).
- Each new sign-up goes to Resend right away from `doPost` (`addToNewsletter_`, best effort). `syncResend()` (hourly trigger; not "On change", which ignores rows written by scripts) is the safety net: it pushes missed sign-ups to the Resend newsletter segment and mirrors unsubscribes into "Desuscrita del newsletter". Never send `unsubscribed: false` to Resend: that would re-subscribe people. Spam fallback if needed: Cloudflare Turnstile.

## Newsletter

- Sender `hola@clubdelasemprendedoras.com` (forwards to the `info@` Porkbun mailbox, which is the reply-to). Domain verified in Resend, click tracking via `links.` CNAME. The `.env` key must be **Full access** (contacts + broadcasts); the Apps Script has its own key in Script Properties.
- Personalisation: `{{{contact.first_name|emprendedora}}}` and `{{{RESEND_UNSUBSCRIBE_URL}}}` (Resend's current syntax; `{{{FIRST_NAME}}}` is the old one). They only resolve in broadcasts, so check with `newsletter.py test ISSUE --broadcast --to <email>`, which sends a real broadcast to a throwaway one-person segment. Plain `test` fills them with fallbacks and adds `[PRUEBA]`.
- Edit an issue by changing its `.md`, then `build` (or `test --broadcast`) to look at it. `schedule` refuses while `[[MARKERS]]` remain and exits 3 above `NEWSLETTER_DAILY_LIMIT`.
- Above the limit (free Resend: 100 emails a day, 3 segments), `schedule --split 100` sends in daily parts of 100 at 08:00 (Wed, Thu, Fri…). Parts go by sign-up order, and `sent.json` keeps each part's `cutoff` (created_at, id), never emails. Only two parts fit at once, so the `club-newsletter-partes` task (Thu–Sat 07:00 CDMX) runs `newsletter.py continue` for the rest. Test emails go to manolo7_11@hotmail.com, followed by a Slack post in `#emprendeconpm`, and the send is at least 2 hours later.
- Slack posts go to `#emprendeconpm` (`C0C0Z3LPQ80`) through our bot (`SLACK_BOT_TOKEN`, scopes `chat:write` + `files:write`) and tag Manu (`<@U0AGV3HNYRE>`): the connector posts as Manu, and a self-mention never notifies. `newsletter.py slack "msg"` for notices; `newsletter.py pdf ISSUE --slack "msg"` for the post after the test, with the email as a PDF (headless Chrome). Exit 4 = no token: post with the connector instead.
- Every test email is a real send. Ask before sending to anyone but the address the user gave.
- After a send, `newsletter.py stats` saves delivered/opened/clicked/bounces/unsubscribes and top links into that issue's entry in `sent.json`; commit it.
- Analytics: `newsletter_analytics.py run --slack` (routine in `newsletter/ROUTINE_ANALYTICS.md`) writes per-email CSV logs and the dashboard into `newsletter/analytics/` (gitignored, has emails: never commit or paste them) and posts the dashboard PNG in `#emprendeconpm`.
- Nothing incomplete goes out: `newsletter.py check` (exit 2 = missing) gates the routine. Missing news (new = SENT/APPROVED, last 10 days, `news_date` not in `sent.json`) or a missing receta → no draft, a Slack post in `#emprendeconpm` (`C0C0Z3LPQ80`, via `newsletter.py slack`, which tags Manu) and a stop. A Monday 12:00 reminder task (`club-newsletter-recordatorio`) runs the same check early.
- The routine is a local scheduled task (`club-newsletter-semanal`, Tuesdays 16:00 Mazatlán = 17:00 CDMX) that follows `newsletter/ROUTINE.md`. It only runs while the Claude app is open.
- Deliverability: the domain was registered 2026-10-06, so expect some spam-folder placement at first. DKIM, SPF (via Resend's `send`/`rsend` CNAMEs) and DMARC `p=none` are set.

## Workflow

- One feature branch per change, opened as a PR against `main`.
- **Deploys:** Vercel project `clubemprendedoras` (team `manolo96035-6430s-projects`, id `prj_2wdMdohpqhJ8QiIjznXfhaD8cN7l`), Git-linked, root directory `site/`. Merging to `main` deploys production at https://www.clubdelasemprendedoras.com (bare domain redirects to `www`; DNS at Porkbun; `clubemprendedoras.vercel.app` still works); other branches get preview URLs, which may be behind Vercel login. Config: `site/vercel.json` (no build, headers) and `site/.vercelignore`.
- After a deploy, check the live site the same way as local (Playwright at 320/393/1280), and confirm the video answers a Range request with `206`.
- `.DS_Store` files are tracked even though `.gitignore` lists them. Don't stage their changes (`git checkout -- .DS_Store`).
- Secrets live only in `.env.local` (gitignored), e.g. `TYPESAFE_API_KEY`.
