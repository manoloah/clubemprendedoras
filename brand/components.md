# Componentes

Los nombres de las clases del CSS coinciden 1:1 con los componentes de Figma
(hoja **06 · Componentes reutilizables · v2**). La guía viva, con cada pieza renderizada con las
clases reales, es [`index.html`](index.html).

| Figma | Variantes | Código | Copy vigente (ejemplo) |
|---|---|---|---|
| `Club/Logo` | Color = Tomato · Navy · Cream | `assets/brand/logo-tomato.webp`, `logo-cream.webp` | — |
| `Club/Nav` | — | `.nav` + `.btn--sm` | logo + **Unirme** |
| `Club/Button` | Style = Primary · Secondary; State = Default · Pressed | `.btn`, `.btn--sm`, `.btn--block` | **Quiero mi lugar →** |
| `Club/Kicker` | Tone = Tomato · Navy · Cream | `.kicker--tomato / --navy / --cream` | Waitlist abierta · Taller 2027 |
| `Club/Input` | State = Default · Focus · Filled · Error | `.field` (`:focus`, `aria-invalid`) | Tu correo · tu@correo.com |
| `Club/Sticker` | Tone = Pink · Olive · Tomato · Lilac · Butter | `.sticker--*` | Sin ser técnica · Con IA · Tú puedes |
| `Club/Note` | Tone = Pink · Butter · Lilac | `.note--*` | Al final: tu app funcionando en tu teléfono |
| `Club/Card/ForYou` | Tone = Pink · Butter · Lilac · Cream | `.for-you__item--*` | Sientes que la IA va a mil y tú te estás quedando atrás. |
| `Club/Card/Week` | Tone = Pink · Lilac · Butter · Cream | `.card-week--*` | Semanas 1 y 2 · Encuentra tu idea… |
| `Club/FAQ Item` | State = Closed · Open | `.faq__item` (`<details>`) | ¿Necesito saber programar? |
| `Club/Waitlist Form` | — | `.waitlist` + `[data-waitlist]` | Aparta tu lugar |
| `Club/Phone` | — | `.phone`, `.phone__screen` | pantallas de ejemplo por semana |
| `Club/Footer` | — | `.footer` | Un proyecto de Pame y Manu · @emprendeconpm |
| `Club/Graphic/*`, `Club/Sticker Art/*`, `Club/Illustration/*` | — | `assets/brand/*`, `assets/img/*` | — |
| **`Club/Motion`** | Breathe · Bob · Hop · Ring · Reveal · Sort | tokens `--dur-*`, `--ease-*`, `--stagger-*` + bloque Motion de `styles.css` + `motion.js` | ver [motion.md](motion.md) |

## Composición

- **Rotación**: cada kicker, nota, sticker y teléfono lleva su inclinación (`.tilt-l`, `.tilt-r`, `rotate:` por elemento).
- **Tono por color**: las tarjetas alternan rosa → lila → mantequilla (→ crema) para dar ritmo; nunca dos del mismo tono seguidas.
- **Nota al pie de cada tarjeta de semana**: `Club/Note` con "Al final: …".
- **Stickers**: palabras sueltas en Caveat que acompañan una ilustración o una lista (hero, ideas, cierre); no llevan acción propia.
- **Formulario**: el nombre y el correo van primero; lo demás es el paso 2, opcional (un modal estilo Typeform, una pregunta por pantalla).
- **Secciones**: alternan fondo (hero rosa → banda navy → crema → lila → crema → rosa → crema → mantequilla → cierre tomato → footer) y cada una abre con un kicker inclinado.

## Pendiente en Figma

La hoja v2 conserva copy anterior a la landing en las notas de `Club/Card/Week` ("Al final: tu idea
validada y una waitlist propia ♡", hoy: "Al final: tu idea clara y tu waitlist arrancando ♡") y en la
tabla de voz. Cuando se sincronice, tomar el texto de [voice.md](voice.md). `Club/Card/ForYou`, `Club/FAQ Item`
y `Club/Waitlist Form` ya coinciden con la landing.
Falta además el componente `Club/Motion` (ver [motion.md](motion.md#en-figma)).
