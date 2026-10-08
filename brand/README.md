# Sistema de marca · El Club de las Emprendedoras

Todo lo que define cómo se ve, suena y se mueve el club, en un solo lugar. Sale de lo que ya existe:
la landing (`site/`), la hoja de Figma y los tokens.

| Documento | Qué responde |
|---|---|
| [`index.html`](index.html) | **Guía viva**: color, tipografía, componentes, imágenes y movimiento renderizados con el CSS real del sitio |
| [`voice.md`](voice.md) | Cómo hablamos y el banco de copy vigente |
| [`foundations.md`](foundations.md) | Color, tipografía, espacio, forma, inclinación, gráficos |
| [`components.md`](components.md) | Mapa Figma ↔ código y reglas de composición |
| [`motion.md`](motion.md) | `Club/Motion`: tokens, patrones y reglas de movimiento |

## Verlo

```bash
npx serve -l 4180 .
```

y abre http://localhost:4180/brand/. Se sirve desde la raíz del repo para que la guía cargue
`site/assets/tokens.css` y `styles.css`. No se despliega: Vercel solo publica `site/`.

## Assets

| Qué | Dónde |
|---|---|
| Logo / main hero (lettering a mano): tomato, navy, cream | `site/assets/brand/logo-{tomato,navy,cream}.webp` (640×400, transparente) |
| Asterisco, subrayado | `site/assets/brand/asterisk.svg`, `underline.svg` |
| Ilustración de la comunidad: cuadrada, vertical, horizontal | `brand/assets/img/community-{square,tall,wide}.webp` (originales 1080px PNG en `brand_assets_gptoutputs/club-women-illustrations/`) |
| Hero de la landing (imagen y video animado) | `site/assets/img/club-women.webp`, `site/assets/video/club-women.mp4` |
| Fotos de fondo, **sin texto**: palmera y edificio rosa, tote y botella, camiseta | `brand/assets/img/photo-{palm-pink,tote-bottle,shirt}.webp` (1400px; originales 3072px en `brand_assets_gptoutputs/club-photo-backgrounds/`) |
| Stickers ilustrados, Pame y Manu, og | `site/assets/img/` |

En Figma las fotos aparecen como "Missing photo" (02B palmera, 02D tote, 03B camiseta, 03C post-it rosa) con el logo
y las frases ya puestos. En los archivos del repo van limpias; el logo y el texto se agregan encima. El post-it
rosa (03C) no es una foto: es una tarjeta de color con texto.

## Fuentes de verdad (en este orden)

1. **Copy:** `site/index.html` (rama `feat/typeform-profile` en adelante).
2. **Tokens:** `site/assets/tokens.css`, espejo de las variables de Figma.
3. **Componentes:** `site/assets/styles.css` ↔ Figma "06 · Componentes reutilizables · v2".
4. **Movimiento:** `site/assets/motion.js` y el bloque Motion de `styles.css`.
5. Figma: [brand system](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=1-2&m=dev) y [06 · Componentes reutilizables · v2](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=47-115&m=dev)

## Qué está desactualizado

- `brand_assets_gptoutputs/club-brand-system/{tokens.json, tokens.css, typography.json}` son una
  primera exportación: usan **Baloo 2** y un rosa `#F3A0C2`. La marca vigente usa **Fraunces + DM Sans + Caveat**
  y rosa `#FBC0D7`. Sus `mark-*.svg` dibujan el logo con texto en Baloo 2: **no son** el logo vigente (el lettering a mano de `site/assets/brand/logo-*.webp`). Los demás SVG (estrellas, flor, corazón…) son formas sueltas de la primera exploración.
- Figma "05 · Voz" (CTAs de ejemplo y titulares EN) es anterior a la landing; ver la tabla de
  reconciliación en [voice.md](voice.md#reconciliación-con-figma).
- Figma no tiene aún el componente de movimiento ([motion.md](motion.md#en-figma)).
- La skill `emprendeconpm-brand-nuevo` describe **otra** marca ("Club de Fundadoras": rojo `#E01B22`,
  lavanda, Shantell Sans, "No naciste para pedir permiso"). No la uses para piezas de este club;
  `CLAUDE.md` la menciona y conviene quitar esa referencia o apuntarla a esta carpeta.

## Cómo mantenerlo

- Cambias un color, tamaño o curva: primero el token en `tokens.css` (y la variable en Figma), luego el uso.
- Cambias copy: se edita `site/index.html` y se refleja en [voice.md](voice.md) en el mismo PR.
- Nuevo componente: clase `.nombre` en `styles.css`, fila en [components.md](components.md), demo en `index.html`.
