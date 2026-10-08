# Sistema de marca · El Club de las Emprendedoras

Todo lo que define cómo se ve, suena y se **mueve** el club, en una carpeta que se puede copiar a otro
proyecto y funciona sola: tokens, componentes CSS, movimiento (JS y video), logos, ilustración, fotos y voz.

Figma: [brand system](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=1-2&m=dev) y [06 · Componentes reutilizables · v2](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=47-115&m=dev)

## Qué hay dentro

```
brand/
  index.html            guía viva: color, tipografía, componentes, imágenes y movimiento (con el CSS/JS reales)
  voice.md              cómo hablamos + banco de copy vigente
  foundations.md        color, tipografía, espacio, forma, inclinación, gráficos
  components.md         mapa Figma ↔ clases CSS y reglas de composición
  motion.md             Club/Motion: tokens, patrones, reglas, video
  assets/
    tokens.css          variables: color, tipografía, espacio, forma, movimiento
    styles.css          componentes (.btn, .kicker, .sticker, .note, .card-week, .faq__item, .phone…) y bloque Motion
    motion.js           animación: reveals, montón de ideas, salto de letras, hero en video (WebGL)
    brand/              logo tomato / navy / cream (lettering a mano), asterisco, subrayado
    img/                ilustración (hero, comunidad), stickers, fotos de fondo, Pame y Manu, og
    video/club-women.mp4   hero animado, alfa apilado (clave para el movimiento de la marca)
    old_brand_assets_gptout/   primera exploración (ver "Qué está desactualizado")
  scripts/hero-video/   build.sh + matte.py: regenerar el video desde un render
```

## Verlo

```bash
npx serve -l 4180 brand
```

y abre http://localhost:4180. Siempre por http(s): desde `file://` el video no se dibuja, y Safari necesita un
servidor con Range requests (no `python3 -m http.server`). Agrega `?debug` para ver el log del video.
Se puede abrir también desde la entrada `brand` de `.claude/launch.json`.

## Usarlo en otro proyecto

1. Copia la carpeta `brand/` (puedes borrar `old_brand_assets_gptout/` y las `.md` si no las necesitas).
2. En tu HTML, en este orden:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&family=Fraunces:opsz,wght@9..144,700;9..144,900&display=swap">
<link rel="stylesheet" href="brand/assets/tokens.css">
<link rel="stylesheet" href="brand/assets/styles.css">
<script src="brand/assets/motion.js" defer></script>
```

3. Copia el marcado de cada componente desde `brand/index.html` (la tabla de [components.md](components.md) dice cuál es cuál).
   `styles.css` busca `brand/underline.svg` relativo a sí mismo, y `motion.js` busca `assets/video/club-women.mp4`
   relativo a la **página**: si tu HTML no está junto a `assets/`, ajusta la ruta del video en `motion.js` (una línea).
4. Para el movimiento: `motion.js` busca las clases del sistema (`.hero__art`, `[data-jump]`, `.chips`, `.card-week`, `.phone`…).
   Lo que no encuentre, lo ignora. Con "reducir movimiento" no hace nada y la página queda estática.

Los tokens (`--brand-primary`, `--surface-*`, `--dur-*`…) son lo único que los componentes leen: cambia ahí y
cambia todo.

## Mantenerlo en sintonía con la landing

La landing (`site/`) y esta carpeta comparten `tokens.css`, `styles.css`, `motion.js`, `assets/brand/`, `assets/img/`
y `assets/video/`. La landing es la fuente (Vercel solo publica `site/`); esta carpeta es la copia portátil.

```bash
scripts/sync-brand.sh           # copia site → brand
scripts/sync-brand.sh --check   # falla si brand/ quedó atrás (úsalo antes de un PR)
```

Lo que solo vive aquí (ilustraciones de la comunidad, fotos de fondo, guía, docs) no se toca. El video se
regenera con `brand/scripts/hero-video/build.sh render.mp4`, que también lo copia a `site/assets/video/`.

## Assets

| Qué | Dónde |
|---|---|
| Logo / main hero (lettering a mano): tomato, navy, cream | `assets/brand/logo-{tomato,navy,cream}.webp` (640×400, transparente) |
| Asterisco, subrayado | `assets/brand/asterisk.svg`, `underline.svg` |
| Hero animado | `assets/video/club-women.mp4` + `assets/img/club-women.webp` (imagen estática mientras carga) |
| Ilustración de la comunidad: cuadrada, vertical, horizontal | `assets/img/community-{square,tall,wide}.webp` (originales 1080px en `assets/old_brand_assets_gptout/club-women-illustrations/`) |
| Fotos de fondo, **sin texto**: palmera y edificio rosa, tote y botella, camiseta | `assets/img/photo-{palm-pink,tote-bottle,shirt}.webp` (1400px; originales 3072px en `assets/old_brand_assets_gptout/club-photo-backgrounds/`) |
| Stickers ilustrados, Pame y Manu, imagen para compartir | `assets/img/` |

En Figma las fotos aparecen como "Missing photo" (02B palmera, 02D tote, 03B camiseta, 03C post-it rosa) con el logo
y las frases ya puestos. Aquí van limpias; el logo y el texto se agregan encima. El post-it rosa (03C) no es una foto:
es una tarjeta de color con texto.

## Fuentes de verdad (en este orden)

1. **Copy:** `site/index.html` (rama `feat/typeform-profile` en adelante).
2. **Tokens:** `site/assets/tokens.css`, espejo de las variables de Figma.
3. **Componentes:** `site/assets/styles.css` ↔ Figma "06 · Componentes reutilizables · v2".
4. **Movimiento:** `site/assets/motion.js`, el bloque Motion de `styles.css` y `club-women.mp4`.

## Qué está desactualizado

- `assets/old_brand_assets_gptout/club-brand-system/{tokens.json, tokens.css, typography.json}` son una primera
  exportación: usan **Baloo 2** y un rosa `#F3A0C2`. La marca vigente usa **Fraunces + DM Sans + Caveat** y rosa `#FBC0D7`.
  Sus `mark-*.svg` dibujan el logo con texto en Baloo 2: **no son** el logo vigente (el lettering a mano de `assets/brand/logo-*.webp`).
  Los demás SVG (estrellas, flor, corazón…) son formas sueltas de esa exploración. Son 48 MB: bórralos al copiar la carpeta.
- Figma "05 · Voz" (CTAs de ejemplo y titulares EN) es anterior a la landing; ver la tabla de
  reconciliación en [voice.md](voice.md#reconciliación-con-figma).
- Figma no tiene aún el componente de movimiento ([motion.md](motion.md#en-figma)).
- La skill `emprendeconpm-brand-nuevo` describe **otra** marca ("Club de Fundadoras": rojo `#E01B22`,
  lavanda, Shantell Sans, "No naciste para pedir permiso"). No la uses para piezas de este club.

## Cómo mantenerlo

- Cambias un color, tamaño o curva: primero el token en `site/assets/tokens.css` (y la variable en Figma), luego `scripts/sync-brand.sh`.
- Cambias copy: se edita `site/index.html` y se refleja en [voice.md](voice.md) en el mismo PR.
- Nuevo componente: clase en `styles.css`, fila en [components.md](components.md), demo en `index.html`, y sync.
