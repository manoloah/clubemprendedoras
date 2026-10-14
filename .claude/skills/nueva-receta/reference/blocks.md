# Receta building blocks

Copy-paste HTML for every piece a receta uses. All of it is already styled and animated by
`site/assets/styles.css` and `motion.js`; reuse these before writing any CSS. The live example
of each is in `site/recetas/reel-con-claude-cowork/index.html`.

Colour variants that exist: `sticker--pink|lilac|butter|olive|tomato`, `note--butter|pink|lilac`,
`kicker--navy|tomato|cream`. Tilts: `tilt-l`, `tilt-r` (never animate `rotate` on them).

## Hero (`.receta-hero`)

```html
<p class="kicker kicker--tomato tilt-l">Receta #N · Gratis para el club</p>
<h1 id="receta-title" class="display">Lo que logras <span class="accent">la parte que engancha</span></h1>
<p class="lead">Dos o tres frases: qué haces tú, qué hace la IA y qué te llevas.</p>
<div class="receta-meta">
  <span class="sticker sticker--pink">N pasos</span>
  <span class="sticker sticker--olive">Sin saber X</span>
  <span class="sticker sticker--lilac">1 tarde</span>
</div>
<p class="receta-by">
  <img src="/assets/img/pame.webp" width="48" height="48" alt="">
  <span>Por Pame · <a href="https://www.instagram.com/PameVls/" target="_blank" rel="noopener">@PameVls</a></span>
</p>
```

- The `h1` is a full sentence in the club's voice; the `.accent` span (tomato) holds the hook.
  No final period (it's a title, not the landing hero).
- Stickers: first one is always the step count; then 1–2 of: the tool, "Sin saber editar/programar…",
  the time it takes, "Gratis". Short, no period.
- Author line: Pame (`pame.webp`, `instagram.com/PameVls`, shown as @PameVls) or Manu
  (`manu.webp`, `instagram.com/thebreathmanu`, @thebreathmanu). For both: "Por Pame y Manu ·
  @emprendeconpm" with the club's link.

## Lo que necesitas (public teaser)

```html
<div class="ingredientes">
  <p class="kicker kicker--navy">Antes de empezar</p>
  <h2 id="ingredientes-title" class="h2">Lo que necesitas</h2>
  <ul class="check-list">
    <li><strong>La herramienta</strong>, que bajas gratis en <a href="https://…" target="_blank" rel="noopener">dominio.com</a>. Qué plan hace falta.</li>
    <li><strong>Lo que ella ya tiene</strong> (fotos, videos, una idea…).</li>
    <li><strong>El tiempo</strong> y ganas de jugar.</li>
  </ul>
</div>
<div class="receta-why">
  <h3 class="h3">¿Por qué X y no Y?</h3>
  <p>Una o dos frases, en concreto.</p>
  <p class="note note--pink tilt-r">Una línea con guiño o el resultado real ♡</p>
</div>
```

The class stays `.ingredientes` (it's CSS), but the copy never says "ingredientes".
`.receta-why` is optional: use it when the draft explains why this tool, or for a "¿Qué es X?"
one-liner that the whole receta depends on. If neither applies, drop the `<div>` and the
`.receta-intro` grid still works with one child.

## A step

```html
<li class="paso" id="paso-N">
  <div class="paso__head"><span class="paso__num" aria-hidden="true">N</span><h2 class="h2">Verbo + qué haces</h2></div>
  <p>Una frase de contexto.</p>
  …blocks…
</li>
```

Step titles start with a verb in *tú*: "Prepara tu carpeta", "Abre Cowork y pega este prompt",
"Publica bien". Numbers in `id`, `.paso__num` and the order must match. First is `paso-1`.

For plain ordered instructions inside a step use a bare `<ol><li>…</li></ol>`.
Inline file or folder names go in `<code>`.

## Check list

```html
<ul class="check-list">
  <li><strong>Etiqueta:</strong> explicación corta.</li>
</ul>
```

## Example cards (2–4)

```html
<div class="frases">
  <div class="frase">
    <p class="kicker kicker--navy">Nombre</p>
    <p class="frase__what">Qué es, en 3–4 palabras</p>
    <p class="frase__eg">"El ejemplo real, entre comillas."</p>
  </div>
  <!-- the last or most important card can use kicker--tomato -->
</div>
```

## Prompt to copy

```html
<div class="prompt">
  <div class="prompt__bar">
    <span>Tu prompt</span>
    <button class="btn btn--sm" type="button" data-copy="prompt-SHORTNAME"><span class="btn__label">Copiar</span></button>
  </div>
<pre id="prompt-SHORTNAME">Texto del prompt, sin sangría inicial.
Lo que ella cambia va entre [corchetes].</pre>
</div>
```

- `<pre>` starts at column 0: any indentation becomes part of the copied text.
- Wrap lines at ~64 characters so it reads on a phone without much sideways scroll.
- Escape `<`, `>` and `&` inside the prompt (`&lt;` `&gt;` `&amp;`).
- Several prompts on one page need different ids (`prompt-1`, `prompt-ajustes`…).
- Keep the prompt's facts exactly as in the draft (tool names, URLs, sizes, colours). Translate or
  tidy the wording only if the draft's prompt is in another language or clearly a rough note.

## "Say it like this" bubbles

```html
<ul class="bubbles">
  <li class="bubble">Mensaje corto como se lo escribirías a la IA</li>
</ul>
```

## Notes and warnings

```html
<p class="note note--butter tilt-l">Tip en una línea, como escrito a mano.</p>

<div class="receta-ojo">
  <img src="/assets/brand/asterisk.svg" width="26" height="46" alt="">
  <p><strong>Ojo:</strong> la advertencia (límites, costos, privacidad…).</p>
</div>
```

At most one note per step, alternate `tilt-l`/`tilt-r` and colours down the page.

## Closing (`.receta-done`, inside `.receta__locked`, after the `</ol>`)

```html
<div class="receta-done">
  <p class="kicker kicker--tomato tilt-l">¿Lo hiciste?</p>
  <h2 class="h2">Mándanos tu [resultado], queremos verlo.</h2>
  <p>Etiquétanos en <a href="https://www.instagram.com/emprendeconpm/" target="_blank" rel="noopener">@emprendeconpm</a> o respóndenos el correo del miércoles. Los mejores los compartimos.</p>
</div>
```

The gate card (`.gate`) and the final `.cta` section stay as in the template: only `data-gate`
changes, and `receta.mjs new` already sets it.

## Hub card (`site/recetas/index.html`, first `<li>` of `.receta-list`)

```html
<li>
  <a class="receta-feature receta-feature--COLOR" href="/recetas/SLUG/">
    <div class="receta-cover" aria-hidden="true">
      <div class="phone phone--tilt-l receta-cover__phone">
        <div class="phone__screen receta-cover__screen">
          <img src="/assets/img/receta-SLUG.webp" width="600" height="1140" alt="" loading="lazy">
          <p class="receta-cover__sub">dos o tres <em>palabras</em></p>
          <span class="receta-cover__play"></span>
        </div>
      </div>
      <span class="sticker sticker--butter receta-cover__sticker">Dos palabras</span>
    </div>
    <div class="receta-feature__copy">
      <p class="kicker kicker--navy">Receta #N · X pasos</p>
      <h3 class="h2">El mismo título que el h1</h3>
      <p>El resumen en una o dos frases.</p>
      <div class="receta-meta">
        <span class="sticker sticker--olive">La herramienta</span>
        <span class="sticker sticker--lilac">El tiempo</span>
      </div>
      <span class="btn receta-feature__go"><span class="btn__label">Ver la receta</span> <span aria-hidden="true">→</span></span>
    </div>
  </a>
</li>
```

- `COLOR`: `receta.mjs next` prints it (pink → lilac → butter, so neighbours never match).
- Alternate `phone--tilt-l` / `phone--tilt-r` with the card below it.
- `.receta-cover__play` only makes sense if the result is a video; drop it otherwise.
- The cover sticker can't be the same colour as the card (`butter` on a butter card: use `pink`).
- `width`/`height` on the `<img>` must be the file's real size.
