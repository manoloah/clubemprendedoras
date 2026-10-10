# Recetas de Emprendimiento e IA

Our tutorials, called **recetas**. Each one is a short, hands-on guide: what you need, up to
5 steps, and a prompt to copy. The newsletter features one every Wednesday.

```
site/recetas/index.html                 the hub: one big card per receta, newest first
site/recetas/<slug>/index.html          one receta
site/recetas/recetas.json               the list the newsletter reads
site/assets/recetas.js                  signup gate, "Copiar" buttons, nav menu
```

## Creating a new receta

You can ask Claude: *"Crea la receta #N a partir de este documento"* and attach the draft.
It follows these steps.

### 1. Write the copy

- Voice: `brand/voice.md`. Mexican Spanish, *tú*, written to women, warm and direct, at most one "¡".
- No tech jargon: explain it in one line ("¿Qué es Remotion? …") or drop it.
- No kitchen puns. The section is called "recetas", but the copy doesn't play with food
  (no ingredientes, hornear, probadita). Keep it Gen Z and direct: "dale play", "cero rollo", "spoiler".
- Keep every fact, link and number from the original draft. Don't invent results.

### 2. Create the page

Copy `reel-con-claude-cowork/` to `site/recetas/<slug>/` (short, lowercase, hyphens) and edit:

| Part | What to change |
|---|---|
| `<head>` | `<title>`, `description`, `canonical`, `og:url`, `og:title`, `og:description`. Keep the inline gate script as is. |
| Hero (`.receta-hero`) | Kicker `Receta #N · Gratis para el club`, the `h1`, the lead, 2–3 meta stickers, the author line. |
| What you need (`.ingredientes`) | Visible to everyone: it's the teaser before the gate. Add `.receta-why` if there's a "why this tool" note. |
| Steps (`.receta__locked`) | Everything behind the gate. One `<li class="paso" id="paso-N">` per step; the first **must** be `id="paso-1"` (the page scrolls there after unlocking). |
| Gate (`.gate`) | Set `data-gate="receta-<slug>"`. That value lands in the Sheet's "Origen" column. |
| Closing CTA | Usually unchanged. |

Building blocks for the steps (all styled already):

- `.check-list` for bullet lists with green ticks
- `.frases` > `.frase` for 2–4 example cards (kicker, `.frase__what`, `.frase__eg`)
- `.prompt` for a prompt to copy: a `<pre id="prompt-<x>">` plus a button with `data-copy="prompt-<x>"`
- `.bubbles` > `.bubble` for "say it like this" chat messages
- `.note note--butter|pink|lilac` for a handwritten tip, `.receta-ojo` for a warning

Images go in `site/assets/img/` as WebP, and the pages use absolute paths (`/assets/...`).

### 3. Add it to the hub

In `site/recetas/index.html`, add a new `<li>` at the **top** of `.receta-list`, copying the
existing one:

- `href` to `/recetas/<slug>/`.
- Card color: alternate `receta-feature--pink`, `--lilac`, `--butter` so two neighbours never match.
- Cover (`.receta-cover`): a phone mockup. Put a photo or screenshot inside `.receta-cover__screen`,
  a short caption in `.receta-cover__sub` (one word in `<em>`), and a sticker.
- Kicker `Receta #N · X pasos`, title, one-line summary, meta stickers, "Ver la receta →".
- Update the note under the list ("La receta #N+1 llega el miércoles a tu correo ♡").

The nav menu doesn't change: it has a single option, the hub.

### 4. Add it to `recetas.json`

Append an entry (newest last). The Tuesday newsletter routine picks the newest one that isn't in
`newsletter/sent.json` yet.

```json
{ "numero": 2, "slug": "…", "titulo": "…", "resumen": "One or two sentences for the email.",
  "fecha": "2026-10-21", "url": "/recetas/…/" }
```

### 5. Check it and ship it

- Serve locally (`npx serve -l 4173 site`) and look at the hub and the receta at **393px and 320px**,
  then desktop. `document.documentElement.scrollWidth === innerWidth` at every size.
- Check the gate both ways: a fresh visit (clear `localStorage`) shows the gate; adding
  `?utm_source=newsletter` opens it. Submitting the gate writes to the live Sheet, so stub
  `window.fetch` in the console before testing it.
- Only bump `?v=` on shared files (`styles.css`, `recetas.js`, `motion.js`) if you changed them,
  and run `scripts/sync-brand.sh` after changing them.
- Open a PR and merge it **before Tuesday 17:00** (CDMX) so the routine finds it for Wednesday.

## The signup gate

- Anyone can read the hero and "Lo que necesitas". The steps are blurred behind a signup card
  (name + email) that posts to the waitlist Apps Script with `source: receta-<slug>`, so every
  new reader joins the waitlist and, from the next daily sync, the newsletter.
- Already on the list? She types her email again. The Sheet never duplicates or overwrites a row,
  so it just unlocks. The Apps Script still never tells the page who's on the list.
- Links in the newsletter carry `utm_source=newsletter` (added by `newsletter.py`), which skips
  the gate. Signing up on the landing page also unlocks every receta on that browser
  (`localStorage` key `club_receta_ok`).
- It's a soft gate: the content is in the page. Without JavaScript everything is visible.
