---
id: 0001
title: "Landing: from \"taller de 8 semanas\" to \"el club 2027\""
status: draft          # waiting on the open questions below; don't implement yet
owner: Manu (with Pame)
created: 2026-10-14
updated: 2026-10-14
branch: docs/club-2027-prd   # implementation goes on its own branch, e.g. club/2027-comunidad
pr: https://github.com/manoloah/clubemprendedoras/pull/18
---

# Landing: from "taller de 8 semanas" to "el club 2027"

## Problem

The landing sells one fixed product: an 8-week live taller where you build a mobile app
(hero "De cero a emprendedora en 8 semanas", a week-by-week syllabus in `#taller`, FAQ answers
about weeks 1–2 and 4–6 hours a week). For 2027 we haven't decided whether the club is that taller.
The direction we're leaning towards is broader: a **membership-style club** where we guide women
through the process with the workshops we already have. Every "8 semanas" promise on the page
would then be wrong, and changing it after people sign up costs trust.

## Goal

Keep the waitlist as the only conversion and keep the page as engaging as it is, but make it
describe **what being part of the club in 2027 could mean** instead of selling the taller. The
undecided format becomes an invitation: *lo estamos armando contigo*. The step-2 questionnaire
collects demand data that helps us decide.

## What the club includes (as of 2026-10-14)

1. **Grupo de WhatsApp:** community, Q&A, announcements.
2. **Sesiones grupales en vivo:** we guide members through the process, together.
3. **Talleres a tu ritmo (on demand, not relaunched):**
   - *Crea tu app con IA (sin saber programar)*: intro "Ser nativa de IA"; 5 modules
     (idea → posicionamiento, posicionamiento → diseño, diseño → app funcional, almacenamiento y
     pagos, lanzamiento y crecimiento); mini-modules "Dale inteligencia a tu app" and
     "Onboarding que convierte". About 2 h per module.
   - *Crece tu negocio de 0 a miles con contenido orgánico e IA*: 3 modules (encuentra tu hook,
     escala con un sistema de embajadoras, multiplica y automatiza con IA) plus a mini-module.
4. **Mentoría 1 a 1** with Pame or Manu.

Cadence, number of sessions and mentoring slots, and price are **not decided**. The page must not commit to them.

## Audience

Unchanged: Spanish-speaking women in Mexico/LATAM, 28–42, non-technical, on their phone from
Instagram. New sub-audience worth naming: the **500+ past students**, who need to see
what's new for them.

## Scope

### In
- Landing copy and structure (`site/index.html`), meta and OG tags, `og.jpg`.
- Step-2 profile modal: copy, plus one new question (needs `sheets/Code.gs`).
- Every other "taller / 8 semanas" mention: recetas CTAs, app.js success copy, voice bank, docs.

### Out (non-goals)
- No pricing, checkout or Hotmart links: the waitlist stays the only conversion.
- No new pages (e.g. a page per workshop) and no change to the Menú (it stays one option).
- No changes to the hero video, motion system or tokens beyond what new cards need.
- No newsletter issue about the change (a separate decision once this ships).

## Proposed changes

Copy below is a **draft** in the club's voice (`brand/voice.md`); polish it while implementing.

### 1. Head (`site/index.html` `<head>`)
- `<title>`: *El Club de las Emprendedoras · Waitlist 2027*
- `description` / `og:description`: *Un club para mujeres que quieren convertir su idea en negocio
  con IA, sin ser técnicas y sin hacerlo solas. Apártate un lugar en la waitlist 2027.*
- `og:title`: the new hero title.
- `site/assets/img/og.jpg`: re-export without "en 8 semanas" and "Taller 2027" (see Q5).

### 2. Hero (`.hero`)
- Kicker: *Waitlist abierta · Club 2027*
- Title: keep `cero a emprendedora` (nowrap, underlined, `data-jump`; the 9.2cqi sizing depends on it).
  → *De **cero a emprendedora**, acompañada.* (alt: *…, en comunidad.*) See Q1.
- Lead: *Un club para convertir tu idea en negocio con IA: sin ser técnica, sin miles de dólares
  y con mujeres que se apoyan entre ellas.*
- Form, stickers and proof line unchanged.

### 3. Band "Lo que viene" (`.band`)
- Title: *Este 2027 abrimos el club.*
- Body: *Un lugar para encontrar tu idea, construirla con IA y crecerla, a tu ritmo pero nunca sola.
  Lo estamos armando contigo: lo que nos cuentes al apartar tu lugar decide cómo se ve.*
- Note: *1 idea → 1 app → miles de usuarios* → *Tu idea → tu negocio → tu comunidad* (or keep, see Q3).

### 4. Replace `#taller` with "Lo que imaginamos para el club"
Keep the `.weeks` / `.week` / `.phone` / `.card-week` layout (the most engaging part of the page)
and change what each card says. The kicker changes from *Semanas 1 y 2* to the name of the part.
New phone screens use the existing `.screen-*` pieces.

| Card | Colour | Phone screen | Title / body | Note |
|---|---|---|---|---|
| Grupo de WhatsApp | pink | Group chat: *"¿Alguien ya conectó pagos?"* / *"Yo! Te paso el prompt ♡"* | *Nunca vas sola.* Un grupo para preguntar lo "básico", compartir avances y celebrar cada paso. | *Preguntar es lo normal aquí* |
| Sesiones en vivo | lilac | Calendar invite: *Sesión del club · en vivo* | *Te guiamos paso a paso, en grupo.* Sesiones con Pame y Manu para avanzar juntas, resolver dudas y destrabarte. | *Y grabadas, por si un día no llegas* |
| Talleres a tu ritmo | butter | Library: 2 workshop rows with progress | *Dos talleres completos, cuando tú quieras.* Crea tu app con IA y Crece tu negocio con contenido e IA. | *Empiezas el día que entras* |
| Mentoría 1 a 1 | pink | Booking: *Tu mentoría con Pame · elegir horario* | *Tu proyecto, con nosotras.* Espacios uno a uno para revisar tu idea, tu app o tu estrategia. | *Lo tuyo, a tu medida* |

Section head: kicker *Lo que imaginamos* · title *Así nos imaginamos el club en 2027.*
Add the anchor `id="club"` (keep `#taller` working as an alias, or update links to it).

### 5. New section: the two workshops (after the four cards, or folded into card 3; see Q4)
Two cards side by side (stacked on phone), reusing `.perk` or `.card-week`:
- **Crea tu app con IA (sin saber programar):** *De la idea al App Store: encuentras qué
  resolver, le das marca, la construyes con IA, cobras y lanzas.* Chips: Idea · Diseño · App ·
  Pagos · Lanzamiento.
- **Crece tu negocio con contenido orgánico e IA:** *Encuentra tu hook, arma un equipo de
  embajadoras y automatiza tu contenido para vender sin pagar anuncios.* Chips: Hook · Embajadoras
  · Escala con IA.
No price, no link out, no "inscríbete".

### 6. Ideas heap (`.chips`)
Keep. Footer: *Ideas que hoy pueden ser negocio y que puedes empezar con IA. ¿Cuál es la tuya?*

### 7. "Este club es para ti si…" (`.for-you`)
Keep the current items and add:
- *Ya vendes y quieres más clientas sin pagar anuncios.*
- *Quieres a alguien a quien preguntarle cuando te atoras.*
Not-for-you stays.

### 8. Quiénes (`#quienes`)
Keep. Optionally mention Renata for the content workshop (Q6).

### 9. "No es otro curso que compras y nunca terminas." (`.perks`)
Keep the title. Rework the perks so they don't repeat the four cards:
*En español y sin tecnicismos* · *Con herramientas gratis* · *A tu ritmo, con acompañamiento* ·
*Con resultado real* (body: *Avanzas con tu idea de verdad, no sólo con apuntes.*).

### 10. FAQ (`#faq`)
- Keep: *¿Necesito saber programar?*, *¿Cuándo empieza?*, *¿Cuánto cuesta?*, tools (broaden to
  include the content tools: Claude/ChatGPT, Higgsfield, Suno, Figma Weave).
- Replace *¿Y si todavía no tengo idea?*: answer points to the club (sessions + the app
  workshop's first module) instead of "semanas 1 y 2".
- Replace *¿Cuánto tiempo necesito a la semana?*: *Tú decides. Los talleres van a tu ritmo y
  las sesiones en vivo quedan grabadas.*
- New *¿Es un curso?*: *No. Es un club: comunidad, sesiones en vivo, talleres y mentoría.
  Los talleres son una parte, no todo.*
- New *Ya tomé un curso con ustedes, ¿qué cambia?*: *Ahora no vas sola después del curso: entras a
  la comunidad, a las sesiones y a la mentoría. Avísanos en el formulario que ya fuiste alumna.*

### 11. Final CTA (`.cta`)
Keep *Tu idea lleva mucho tiempo esperando.* Lead: *Apártate un lugar y ayúdanos a armar el club
que quieres en 2027.* Form title *Quiero entrar al club* (unchanged).

### 12. Step-2 profile modal (`site/index.html` `.profile`, `site/assets/app.js`, `sheets/Code.gs`)
- Intro: *…Con esto armamos el club a tu medida.*
- `traba_taller` legend → *¿Qué es lo que más te trabaría para avanzar?* (keep the field name so
  the Sheet column stays; only the label changes in `Code.gs`).
- `curso_previo` legend: *¿Ya tomaste un curso con nosotras?*
- **New question** `club_interes` (checkbox, multi): *¿Qué te emociona más del club?*: Grupo de
  WhatsApp · Sesiones en vivo · Talleres a mi ritmo · Mentoría 1 a 1. Add it to `COLUMNS` in
  `sheets/Code.gs` and redeploy the Apps Script (same `/exec`, new version).
- `app.js` success copy (line ~199): *…Con esto armamos el club pensando en ti…*

### 13. Recetas
`site/recetas/index.html`, `reel-con-claude-cowork/index.html`, `dashboard-finanzas-en-vivo/index.html`
share the CTA *Esto es un spoiler del taller. … 8 semanas…*. New: *Esto es un spoiler del club.* /
*En 2027 lo hacemos juntas: comunidad, sesiones en vivo, talleres y mentoría.* Because new
recetas are copied from `reel-con-claude-cowork/`, fixing it there fixes future ones.

### 14. Brand, docs and tooling
- `brand/voice.md`: copy bank (hero, band, the section kickers, the week cards → club cards,
  FAQ, step 2) and the vocabulary rule: **club** = what we offer; **talleres** = the two
  workshops inside it; *curso* is still avoided except for "No es otro curso…" and past
  students' "ya tomé un curso".
- `.claude/skills/nueva-receta/` (`SKILL.md` line ~68 and `receta.mjs` line ~216): the "curso →
  taller" rule becomes "curso → club / taller".
- `brand/index.html`, `brand/components.md`: rename the Week card to the Club card if the
  component is renamed. Run `scripts/sync-brand.sh` after CSS changes.
- `CLAUDE.md` *Project*, `README.md`, `newsletter/README.md`: describe the club, not the 8-week taller.
- Bump `?v=` on every changed asset (`styles.css`, `app.js`, plus `motion.js` if touched).

## Acceptance criteria
- [ ] No "8 semanas" or "taller de 8 semanas" left in `site/` (`grep -ri "8 semanas" site` is empty),
      except deliberate mentions of the two talleres.
- [ ] The page names all four parts of the club, and the two workshops by name, without price,
      cadence or a link out.
- [ ] The hero keeps `cero a emprendedora` on one line at 320, 393 and 1280.
- [ ] The step-2 modal shows *¿Qué te emociona más del club?*, and the value arrives in its own Sheet
      column (checked with a stubbed `fetch` locally, then one real test row the owner approves).
- [ ] `og.jpg` and the meta/OG tags no longer say "8 semanas" or "Taller 2027".
- [ ] Recetas hub and every receta CTA updated; `receta.mjs check` passes for each receta.
- [ ] `brand/voice.md` copy bank matches the page; `scripts/sync-brand.sh --check` is clean.
- [ ] Checked at 393×852 and 320 (plus 1280) in Chromium and WebKit; `scrollWidth === innerWidth`;
      motion and reduced-motion both fine.
- [ ] Production checked after merge (CLAUDE.md → Workflow).

## Open questions
| # | Question | Recommendation | Owner | Answer |
|---|---|---|---|---|
| 1 | Hero title: *…, acompañada.* or *…, en comunidad.*? | *acompañada* (warmer, says "not alone" without the jargon of "comunidad") | Manu + Pame | |
| 2 | Name the two workshops on the page? Link to Hotmart? | Name them, no link and no price: the waitlist stays the only conversion and they're part of the club, not separate products | Manu | |
| 3 | Keep the formula note *1 idea → 1 app → miles de usuarios*? | Change it to *Tu idea → tu negocio → tu comunidad*: the app is now one path | Pame | |
| 4 | Workshops as their own section or inside card 3? | Own short section: it's the most concrete proof of what you get | Manu | |
| 5 | `og.jpg`: Figma source to re-export, or recreate from page assets? | Re-export from Figma if the frame exists | Manu | |
| 6 | Mention Renata (co-lead of the content workshop)? | Only if she'll be in the 2027 club; otherwise just Pame and Manu | Manu | |
| 7 | Any concrete numbers (sessions per month, mentoring slots)? | None until decided; "en vivo" and "1 a 1" are enough | Manu + Pame | |
| 8 | Notify the current waitlist that the format changed? | Yes, briefly in the next newsletter, framed as "ayúdanos a armarlo" with a link to the step-2 question | Manu | |

## Risks & dependencies
- **Apps Script redeploy** is manual (Deploy → Manage deployments → New version). If the site ships
  first, `club_interes` is silently dropped until the script is updated: deploy the script first.
- **Past students** may read "talleres a tu ritmo" as "I already paid for this". FAQ #10 covers it.
- **Waitlist expectations:** people who signed up for "8 semanas" (see Q8).
- **This repo is public:** the PRD only holds what's fine to show publicly.

## Sources
- Notion: [Curso Crea tu app con IA (sin saber programar)](https://app.notion.com/p/Curso-Crea-tu-app-con-IA-sin-saber-programar-286f2126a3a281239a74d5e18a27e9ac)
  and its [module outline](https://app.notion.com/p/292f2126a3a28045b86bf60943eb9c63)
- Notion: [Curso Crecer tu negocio de 0 a Miles con Contenido orgánico y IA](https://app.notion.com/p/Curso-Crecer-tu-negocio-de-0-a-Miles-con-Contenido-org-nico-y-IA-305f2126a3a280199464df76eb13fbb2)
  and its [module outline](https://app.notion.com/p/305f2126a3a280308466d83a028e00e7)
- Current page: `site/index.html` at `main` (d91f813).
