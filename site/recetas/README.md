# Recetas de Emprendimiento y IA

Our tutorials, called **recetas**. Each one is a short, hands-on recipe: ingredients (what you
need), steps, and a prompt to copy. The newsletter features one every Wednesday.

```
site/recetas/index.html                 the hub (a card per receta)
site/recetas/<slug>/index.html          one receta
site/recetas/recetas.json               the list the newsletter reads
site/assets/recetas.js                  signup gate + "Copiar" buttons
```

## Adding a receta

1. Copy `reel-con-claude-cowork/` to `site/recetas/<slug>/` and rewrite it (voice: `brand/voice.md`).
   Keep the parts: hero, `.ingredientes`, then everything behind the gate inside
   `<div class="receta__locked" data-locked>`, then the closing CTA.
2. Add its card at the top of the grid in `site/recetas/index.html`.
3. Add an entry to `recetas.json` (newest last). `url` can be relative or a full link.
4. Merge to `main`. The Tuesday routine picks the newest entry not yet in `newsletter/sent.json`.

```json
{ "numero": 2, "slug": "…", "titulo": "…", "resumen": "One or two sentences for the email.",
  "fecha": "2026-10-21", "url": "/recetas/…/" }
```

## The signup gate

- Anyone can read the hero and the ingredients. The steps are blurred behind a signup card
  (name + email) that posts to the waitlist Apps Script with `source: receta-<slug>`, so every
  new reader joins the waitlist and, from the next daily sync, the newsletter.
- Already on the list? She types her email again. The Sheet never duplicates or overwrites a row,
  so it just unlocks. The Apps Script still never tells the page who's on the list.
- Links in the newsletter carry `utm_source=newsletter` (added by `newsletter.py`), which skips
  the gate. Signing up on the landing page also unlocks every receta on that browser
  (`localStorage` key `club_receta_ok`).
- It's a soft gate: the content is in the page. Without JavaScript everything is visible.
