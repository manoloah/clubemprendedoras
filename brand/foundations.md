# Fundamentos

Todo sale de `site/assets/tokens.css`, que refleja las variables de Figma
(colecciones **Club · Primitives**, **Club · Color roles**, **Club · Foundations**).
Los componentes usan los **roles**, nunca las primitivas ni hex sueltos.

## Color

### Primitivas

| Token | Hex | Uso |
|---|---|---|
| `--club-tomato` | `#F02717` | Acción principal, logo, subrayado, asterisco |
| `--club-pink` | `#FBC0D7` | Fondo expresivo (hero, nav), tarjetas y stickers rosas |
| `--club-lilac` | `#B99CE5` | Fondo frío, tarjetas y notas lila |
| `--club-butter` | `#F2C75C` | Fondo optimista, notas, stickers mantequilla |
| `--club-olive` | `#63774C` | Crecimiento: stickers y hojas |
| `--club-cream` | `#F6F0E6` | Fondo por defecto, texto sobre navy |
| `--club-navy` | `#17254A` | Texto, bordes, sombra dura, fondo inverso |
| `--club-white` | `#FFFFFF` | Campos de formulario |
| `--club-red-ink` | `#B72E21` | Texto de acento (contraste sobre rosa/crema) y botón presionado |

### Roles (lo que usan los componentes)

| Rol | Valor | Cuándo |
|---|---|---|
| `--surface-default` | cream | Fondo de página y secciones neutras |
| `--surface-expressive` | pink | Hero, nav, bloques cálidos |
| `--surface-cool` | lilac | Sección de ideas, pantallas de ejemplo |
| `--surface-optimistic` | butter | FAQ, notas, tarjetas de apoyo |
| `--surface-inverse` | navy | Cierre, footer, kickers oscuros |
| `--brand-primary` | tomato | CTA, acento |
| `--brand-secondary` / `--brand-tertiary` / `--brand-growth` | pink / lilac / olive | Tonos de tarjetas y stickers |
| `--text-default` / `--text-inverse` / `--text-accent` | navy / cream / red-ink | Texto |
| `--border-default` | navy | Bordes y sombra dura |
| `--action-default` / `--action-pressed` | tomato / red-ink | Botón normal / hover y presionado |
| `--field-surface` | white | Inputs |

Reglas de contraste: texto navy sobre rosa, lila, mantequilla y crema; cream sobre tomato, olive y navy;
`--text-accent` (red-ink, no tomato) para texto rojo pequeño sobre claro.

> **Nombres en Figma vs. código.** Figma expone las variables con el prefijo `--club-color-…`
> (p. ej. `--club-color-brand-primary`, `--club-color-action-hover`); el CSS del sitio usa los
> nombres cortos (`--brand-primary`, `--action-pressed`). Son los mismos valores. Si algún día se
> sincronizan por Code Connect, el mapa es: quitar `club-color-` y renombrar `action-hover` → `action-pressed`.

## Tipografía

| Rol | Fuente | Token | Specs |
|---|---|---|---|
| Titular | **Fraunces** 900 | `--type-display` | 44/46 móvil, crece en desktop |
| H2 | Fraunces 700 | `--type-h2` | 32/36 |
| H3 | Fraunces 700 | `--type-h3` | 22/26 |
| Cuerpo | **DM Sans** 400 | `--type-body` | 16/24 |
| Cuerpo fuerte | DM Sans 700 | `--type-body-strong` | 16/24 |
| Caption | DM Sans 500 | `--type-caption` | 13/18 |
| Kicker | DM Sans 700, MAYÚS, tracking .12em | `--type-kicker` | 12/16 |
| Label | DM Sans 700 | `--type-label` | 14/20 |
| Botón | DM Sans 700 | `--type-button` | 18/24 |
| Nota / sticker | **Caveat** 700 | `--type-note` | 26/28 (stickers en MAYÚS) |

Google Fonts: `Fraunces` (opsz 9..144, 700/900), `DM Sans` (opsz 9..40, 400/500/700), `Caveat` (400/700).
El logo "EL CLUB DE LAS EMPRENDEDORAS" es lettering a mano: se usa como imagen
(`site/assets/brand/logo-*.webp`), nunca se reescribe en una fuente.

## Espacio, forma y trazo

- **Espacio** (base 4): 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 80 · 96. Gutter móvil 24, ancho máximo 1120.
- **Radio**: 8 (notas) · 16 (tarjetas de lista) · 24 (tarjetas de semana, formulario) · pill (botones, kickers, stickers).
- **Trazo**: 1 fino · **2 UI** (bordes de botón, tarjeta, campo) · 4 doodle (borde crema de los stickers).
- **Elevación**: `--shadow-hard` (`0 4px 0 navy`, sin blur) para botones; `--shadow-sticker` (suave) para stickers y notas.

## Inclinación (identidad, no adorno)

**Nada queda perfectamente recto.** Las rotaciones usan la propiedad `rotate` de CSS:

| Clase / patrón | Valor |
|---|---|
| `.tilt-l` / `.tilt-r` (kickers, notas) | −2° / +2° |
| `.phone--tilt-l` / `--tilt-r` | −3° / +3° |
| `.waitlist--tilt` | +1° |
| Stickers del hero | −8° y +9° |
| Stickers de ideas (`.chips`) | −3, +2, −1, +3, −2° en ciclo |

`rotate` pertenece a la inclinación. Los loops (`translate`/`scale`) y las entradas (`transform`)
nunca lo tocan; así se componen sin pelearse (ver [motion.md](motion.md)).

## Gráficos e imágenes

- **Logo / main hero**: lettering a mano "EL CLUB DE LAS EMPRENDEDORAS" con subrayado y asterisco. Tres colores: tomato (sobre rosa, crema, mantequilla), navy (sobre claros) y cream (sobre navy, tomato, lila). Imagen, nunca texto.
- **Asterisco** tomato (`asterisk.svg`): chispa de marca; favicon.
- **Subrayado** tomato (`underline.svg`): trazo a mano bajo "cero a emprendedora"; el `::after` de `.underline`.
- **Stickers ilustrados** (WebP): corazón lila, palma rosa, flor mantequilla, blob olive, óvalo rosa, etiqueta crema.
- **Ilustración de la comunidad**: tres mujeres con lentes y gorra "Big dreams", transparente, en cuadrada, vertical y horizontal; en la landing, también animada (`club-women.mp4`).
- **Fotos de fondo**: palmera con edificio rosa, tote con botella coral, mujer de espaldas con camiseta crema. Luz de mediodía, cielo azul, rosa y coral; van sin texto y el logo o una frase de Caveat (p. ej. "Apoyo entre hermanas") se pone encima.
- **Post-it**: tarjeta rosa con kicker "Post it" y una frase en Caveat ("Tú también puedes").
- Inventario completo y ubicación de cada archivo: [README](README.md#assets).
