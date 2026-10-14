---
name: nueva-receta
description: Create a new receta (our name for tutorials) for El Club de las Emprendedoras from a draft: a doc, a Notion or Google Docs link, a file or pasted text. Rewrites the copy in the club's voice, builds site/recetas/<slug>/ from the first receta, adds the hub card and the recetas.json entry, checks it at phone size and opens the PR. Use when the user says "crea la receta #N", "nueva receta", "haz una receta con este documento", "make a new receta/tutorial", or attaches a guide meant for /recetas/.
---

# Nueva receta

A receta is a short hands-on guide: a hero, a public "Lo que necesitas", up to 5 gated steps
with a prompt to copy, and a closing. The first one, `site/recetas/reel-con-claude-cowork/`,
is the template for structure, tone and markup. The newsletter features the newest one each
Wednesday, so a receta has to be **merged (deployed) before Tuesday 17:00 CDMX**.

Helper script (no deps): `node .claude/skills/nueva-receta/scripts/receta.mjs next | new <slug> | check <slug>`.
HTML for every block: [reference/blocks.md](reference/blocks.md).

Work through the steps without stopping for approval; the PR is where the user reviews.
Ask only when something is truly missing (no draft at all, or it's unclear who the author is).

## 0. Gather

1. **The draft.** Read all of it. A Notion, Google Docs or Drive link → read it with that connector;
   a file → Read it; pasted text → use it. Note every fact, link, number, tool name and prompt.
2. **Read the voice guide** `brand/voice.md`, and reread the template page
   `site/recetas/reel-con-claude-cowork/index.html` for tone.
3. **Numbers and date:** run `receta.mjs next`. It prints the next `numero`, the `fecha` (the
   next Wednesday), the hub card colour and the current `?v=` of each shared asset.
4. **Author:** Pame unless the draft says otherwise. **Cover image:** any photo or screenshot the
   user gave; otherwise reuse the author's photo and say so in the final message.
5. **Branch** from an up-to-date `main`: `git switch main && git pull && git switch -c receta/<slug>`.
   Slug: 3–5 lowercase words with hyphens that say what she makes (`reel-con-claude-cowork`).

## 1. Write the copy (the part that matters most)

Map the draft onto the receta's shape before touching HTML:

| Piece | What it says |
|---|---|
| `h1` | What she gets, as a full sentence, with the hook in `.accent`: "Así hicimos el reel de Pame *sin editar ni un segundo*" |
| Lead | 2–3 sentences: what she does, what the AI does, what she takes away |
| Meta stickers | "N pasos" + the tool or "Sin saber X" + the time it takes |
| Lo que necesitas | 3–5 items: the tool (link, free or which plan), what she already has, the time. Public, so it has to sell the receta |
| `.receta-why` | Optional: "¿Por qué X y no Y?" or "¿Qué es X?" in 1–2 sentences, plus a note with the real result |
| Pasos | Up to 5. Title starts with a verb in *tú*. Each one short: a line of context, then a block (check list, cards, prompt, bubbles) and at most one note |
| Prompt | Exactly the draft's prompt, with what she changes in [corchetes] |
| Closing | "¿Lo hiciste?" + ask her to share the result with @emprendeconpm |
| Hub summary / `resumen` | One or two sentences, ends with what she gets ("…y el prompt listo para copiar.") |

Rules (from `brand/voice.md` and the first receta):

- **Keep every fact, link and number** from the draft. Never invent results, users, prices or
  times. If the draft has a real result (a number, a view count), use it; it's what sells.
- **Mexican Spanish, *tú*, written to women** (emprendedora, lista, tú misma). Warm and direct.
- **She is not technical at all.** No terminal, no installers, no commands in the steps. Put every
  technical step inside the prompt: give the GitHub repo or tool link and ask Claude Code (or Cowork)
  to install and set it up, then she only supplies her own inputs (her link, her files, her idea).
- **Keep prompts general so the AI thinks, not her.** Have Claude read her data itself (columns,
  periods, currency), take her brand from her website link, and choose what to build from a goal
  and a frame ("piensa como el CFO de [empresas que te inspiren]"). Don't make her list columns,
  colours or visualizations.
- **Real screenshots for UI steps** (where a menu or button is): use the user's screenshots or take
  them with the built-in browser. Don't draw mock-ups of Claude's UI.
- **Screenshot layout:** never drop a bare `<figure><img>` in a step; app screenshots are huge next to
  the text on desktop. Use `.shot` (max 360px, navy border, hard shadow, `<figcaption>` saying what
  to look at), `.shot--sm` (260px) for tall menus, `.shot--wide` (520px) for wide strips. Two or more
  screenshots in a row go inside `.shots` (tall one left, others stacked right on desktop; stacked on
  phones). Convert to WebP, check at 393 and 1280.
- **No jargon.** Explain a technical word in one plain line the first time ("Cowork trabaja
  directo en una carpeta de tu compu") or drop it. API, backend, deploy, repo, stack: never bare.
- **No kitchen puns,** even though it's a "receta": no ingredientes, hornear, probadita, cocina,
  sazón. Gen Z and direct instead: "dale play", "cero rollo", "spoiler", "sin darle más vueltas".
- **No hype:** no "hazte rica", "en 5 minutos", "secreto". Honest about effort ("1 tarde").
- At most one "¡" per screen, digits for numbers (5 pasos, 22 segundos), no em dashes,
  `♡` only in notes and stickers. "Tutorial" → receta; "curso" → taller.
- Cut what doesn't help her do it: history of the tool, long feature lists, repeated tips.
  Five tight steps beat eight. Merge or move extras into a note or "Ojo".

## 2. Build the page

1. `node .claude/skills/nueva-receta/scripts/receta.mjs new <slug>`: copies the template into
   `site/recetas/<slug>/`, and sets the canonical/og URLs, `data-gate="receta-<slug>"`, the
   "Receta #N" kicker and the current `?v=` versions.
2. Edit the new `index.html`:
   - `<head>`: `<title>` = "h1 text · Recetas del Club"; `description` (~150 chars, ends with
     "N pasos y el prompt listo para copiar." or similar); `og:title` = h1; `og:description`.
     Leave the inline gate script, `og:image` and the asset tags alone.
   - Hero, Lo que necesitas, steps, closing: replace all of the template's content using the
     blocks in [reference/blocks.md](reference/blocks.md). Keep `id="paso-1"` on the first step
     and every step inside `.receta__locked`.
   - Gate card and final CTA section: unchanged.
3. **Images** go in `site/assets/img/` as WebP, named `receta-<slug>[-what].webp`, referenced as
   `/assets/img/…` with their real `width`/`height`. Cover for the hub (portrait, ~600 wide):
   `cwebp -q 80 -resize 600 0 input.jpg -o site/assets/img/receta-<slug>.webp`
   (crop to about 600x1140 first if it's landscape; the phone shows the top). Screenshots
   inside steps: max ~900px wide. Get real sizes with `cwebp -info` or `file`.
4. **No new CSS** unless a block truly doesn't exist. If you add some: put it with the other
   `.receta-*` rules in `site/assets/styles.css`, use tokens only, bump `styles.css?v=` on
   **every** page (landing, hub, all recetas), run `scripts/sync-brand.sh`, and add the component
   to `brand/components.md`.

## 3. Hub card

In `site/recetas/index.html`, add a new `<li>` at the **top** of `.receta-list` (template in
blocks.md): colour from `receta.mjs next`, title = h1, kicker "Receta #N · X pasos", the summary,
2 meta stickers, the cover. Then update the note under the list to "La receta #N+1 llega el
miércoles a tu correo ♡". The nav menu does not change.

## 4. recetas.json

Append (newest last) to `site/recetas/recetas.json`:

```json
{ "numero": N, "slug": "<slug>", "titulo": "<h1 text>", "resumen": "<hub summary>",
  "fecha": "<from receta.mjs next>", "url": "/recetas/<slug>/" }
```

## 5. Check

1. `node .claude/skills/nueva-receta/scripts/receta.mjs check <slug>` → fix until `OK`.
   Read every warning; each one is either fixed or deliberately kept (say which in the PR).
2. **In the browser**, at phone size first (CLAUDE.md "Testing"). `preview_start` name `landing`
   (port 4173), `resize_window` 393x852, then:
   - **Gated view:** open `http://localhost:4173/recetas/<slug>/`, run
     `localStorage.removeItem("club_receta_ok"); location.reload()`, wait ~3s, screenshot the
     hero, scroll to the gate and screenshot it (steps blurred, card on top).
   - **No overflow:** `document.documentElement.scrollWidth === innerWidth` must be `true`.
   - **Gate unlock, without touching the live Sheet:** stub first, then submit:
     `window.fetch = async () => new Response('{"ok":true}', { headers: { "Content-Type": "application/json" } })`,
     fill name + email in the gate, click "Quiero la receta". Expect the steps unblurred and a
     scroll to Paso 1. **Never submit without the stub**: it writes a row to the real waitlist.
   - **Newsletter link:** clear `club_receta_ok`, open `/recetas/<slug>/?utm_source=newsletter`
     → no gate.
   - **Unlocked read-through:** scroll the whole page and screenshot each step; check the prompt's
     "Copiar" button turns into a confirmation, and that the prompt box doesn't push the page wide.
   - **Hub:** `/recetas/` at 393: the new card on top, cover looks right, colours alternate.
   - Repeat the overflow check and a quick look at **320x568** (receta + hub), then **1280x800**.
   - `read_console_messages` with `onlyErrors`: none.
3. Reset with `localStorage.removeItem("club_receta_ok")` and `resize_window` preset `desktop`.

## 6. Ship

1. Stage only the receta files (`site/recetas/…`, new images, any CSS/brand files you changed).
   Never stage `.DS_Store` (`git checkout -- .DS_Store` if it shows up).
2. Commit: `Receta #N: <título corto>` plus a line on what it teaches; end with the attribution
   line from the system reminder.
3. Push and open a PR against `main` with: what the receta teaches, the source draft, what was
   cut or reworded from it and why, any warnings kept, the sizes checked, and a reminder that it
   must be merged before Tuesday 17:00 CDMX (`newsletter.py` reads `recetas.json` from the live
   site). Bind it with the ccd_pr tools.
4. **Don't merge yourself**: merging deploys production. After the user merges, check
   `https://www.clubdelasemprendedoras.com/recetas/<slug>/` and `/recetas/recetas.json` on the
   live site (with `?utm_source=newsletter` to see the steps) at 393px.

Final message to the user: the preview of the hero and hub card (screenshots), the PR link,
anything you assumed (author, cover image, cut steps), and the merge deadline.
