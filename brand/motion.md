# Club/Motion

El movimiento es un componente de la marca, no un efecto suelto. Se construyó en la rama
`feat/landing-motion` (PR #2) y vive en `site/assets/motion.js` + el bloque "Motion" de
`site/assets/styles.css` (copias portátiles en `brand/assets/`, ver `scripts/sync-brand.sh`). Aquí queda definido como sistema: tokens, patrones y reglas.

**Personalidad:** juguetón y ligero, como pegatinas que flotan. Todo es *decoración*: nada
comunica información solo con movimiento, y todo se apaga con `prefers-reduced-motion: reduce`.

## Tokens (en `site/assets/tokens.css`)

| Token | Valor | Para qué |
|---|---|---|
| `--dur-fade` | 300ms | Cambio de ilustración estática → video |
| `--dur-reveal-fade` / `--dur-reveal` | 500ms / 900ms | Entrada: opacidad / desplazamiento |
| `--dur-sort` | 1000ms | Stickers saliendo del montón |
| `--dur-ring` | 2.6s | Luz del botón, una vuelta |
| `--dur-breathe` / `--dur-breathe-fast` | 3.2s / 2.4s | Íconos que respiran / asterisco del hero |
| `--dur-bob-sticker` / `--dur-bob-chip` / `--dur-bob-phone` | 3.6s / 4.2s / 5.5s | Flotar |
| `--dur-hop` | 3s | Ciclo del salto de letras |
| `--dur-float` | 4s | Fotos de Pame y Manu |
| `--stagger-reveal` / `--stagger-sort` / `--stagger-hop` | 90ms / 85ms / 65ms | Escalonado entre hermanos |
| `--ease-soft` | `ease-in-out` | Todos los loops |
| `--ease-pop` | `cubic-bezier(.34,1.56,.64,1)` | Entradas con rebote |
| `--ease-sort` | `cubic-bezier(.34,1.45,.64,1)` | Stickers acomodándose |
| `--ease-hop` | `cubic-bezier(.3,.7,.4,1)` | Salto de letras |
| `--bob-distance` / `--float-distance` | 9px / 8px | Altura de flotación |

Duraciones distintas por elemento (3.2, 3.6, 4.2, 5.5s) y `animation-delay` negativos
desfasan los loops a propósito: nada late al unísono.

## Patrones

| Patrón | Dónde | Cómo | Propiedad |
|---|---|---|---|
| **Breathe** | Asterisco, decoración de la banda, íconos de "distintas", corazón de éxito | `scale` .88 ↔ 1.16 | `scale` |
| **Bob** | Stickers del hero, teléfonos, stickers de ideas ya ordenados | sube 9px y baja | `translate` |
| **Float** | Fotos de Pame y Manu | sube 8px y baja | `transform` |
| **Hop** | La frase subrayada del hero (`[data-jump]`) | cada letra salta con 65ms de diferencia, como ola | `translate` |
| **Ring** | Todos los `.btn` | un haz de luz (butter → blanco) recorre el borde; se oculta en `disabled` | `@property --ring` |
| **Reveal · up** | Texto, tarjetas, FAQ, footer | entra desde 40px abajo, con rebote | `transform` + `opacity` |
| **Reveal · drop** | Hero art, teléfonos, tarjetas "para ti", foto | cae desde 70px arriba rotando ±4° | `transform` + `opacity` |
| **Heap → sort** | Ideas de apps (`.chips`) | empiezan amontonadas ~150px bajo el título; al entrar a pantalla se acomodan con escalón de 85ms | `transform` |
| **Hero loop** | Ilustración del hero | video de alfa apilado dibujado en WebGL sobre la imagen estática | canvas |
| **Step in** | Preguntas del paso 2 | entra desde ±32px según la dirección, 320ms | `transform` + `opacity` |
| **Press** | Botón | `translateY(4px)` y se quita la sombra dura | `transform` |

## Reglas

1. **Una propiedad por trabajo.** La inclinación es `rotate`; los loops son `translate`/`scale`;
   las entradas son `transform`. Nunca animes `rotate` en algo que ya tiene inclinación.
2. **Estados ocultos solo bajo `html.motion`**, clase que `motion.js` agrega al final. Sin JS, o con
   *reduce motion*, la página es estática y completa.
3. **Nada ensancha la página.** `main > section, .footer { overflow-x: clip }`. Verifica
   `document.documentElement.scrollWidth === innerWidth` a 320, 393 y 1280.
4. **`reduce` apaga todo**, incluido el video; también `saveData` desactiva el video.
5. **El movimiento no lleva información.** El texto de la frase que salta se duplica en un
   `visually-hidden` para lectores de pantalla; las letras animadas van `aria-hidden`.
6. **Máximo 6 hermanos escalonados** (`Math.min(n, 6) * 90ms`), si no la página se siente lenta.
7. **Los valores salen de tokens.** Una duración o curva nueva se crea primero en `tokens.css`.
8. **Al cambiar `motion.js`, `styles.css` o `tokens.css`, sube su `?v=N`** en `index.html`.

## Hero loop (video)

Resumen: MP4 H.264 *level 4.0* de 1280×640, color a la izquierda y máscara a la derecha, ping-pong de
238 cuadros a 24fps; `motion.js` lo pinta con WebGL bajo los stickers. Detalle, trucos de Safari/iPhone y
cómo regenerarlo: `CLAUDE.md` § Hero video y `brand/scripts/hero-video/build.sh`. El archivo es `assets/video/club-women.mp4` y es parte del sistema: sin él, el hero queda como imagen estática. Si el video cambia, sube el `?v=` de su URL en `motion.js`.

## Cómo probarlo

```bash
npx serve -l 4173 site     # la landing
npx serve -l 4180 brand    # esta carpeta: la guía viva
```

Abre con `?debug` para ver el log del video. Pruébalo a 393×852 (iPhone 15) y a 320; el escritorio
(1280) es solo la verificación final. La guía viva (`brand/index.html`) muestra cada patrón con las
clases reales y un botón "Repetir".

## En Figma

La hoja **06 · Componentes reutilizables · v2** no tiene aún un componente de movimiento. Propuesta
para `Club/Motion`: un frame por patrón (Breathe, Bob, Hop, Ring, Reveal, Sort) con la curva y duración
de esta tabla como *smart animate* y las variables de movimiento (`Club · Motion`) con los mismos nombres
que los tokens CSS (`dur-*`, `ease-*`, `stagger-*`).
