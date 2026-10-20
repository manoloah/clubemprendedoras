# Prompts que crearon la marca

Los prompts con los que armamos la marca del club con Claude Code (Figma → sistema de marca → landing →
carpeta `brand/`), para poder repetir el proceso en otro proyecto. Arriba está la plantilla reutilizable;
abajo, los prompts originales tal cual se escribieron, en orden, con los follow-ups que cambiaron el resultado.

Antes de esto, la primera exploración visual se hizo en ChatGPT (`assets/old_brand_assets_gptout/`, commit
"assets created by chatgpt"). Esos prompts viven en el historial de ChatGPT, no aquí.

## Plantilla reutilizable

Cambia lo que está entre `[corchetes]`. Cada paso es una sesión de Claude Code con el conector de Figma.

1. **Hero en Figma, desde una referencia.** Adjunta la imagen de referencia.
   > Estoy creando la marca [nombre]. Ayúdame a diseñar el hero en mi Figma lo más parecido posible a la
   > imagen adjunta, usando solo las fuentes de mi marca: [link al frame de tipografía]. Lo importante es
   > cómo se acomodan las letras: forma, tamaño y detalle. Créalo aquí: [link al frame destino].

   Si no queda: *"Compara los dos y esfuérzate más. Fíjate en los detalles de la forma, eso es lo que importa."*

2. **Más layouts con la misma precisión.** Adjunta las imágenes.
   > Muy sólido. Ahora imita exactamente el layout adjunto y ponlo aquí: [link]. La primera imagen va sobre
   > fondo [color], la segunda sobre merch. Hazlo igual que antes para que quede súper preciso.

3. **Sistema de marca y landing.**
   > Con el board de Figma y los assets de marca, construye la landing de [nombre], optimizada para móvil,
   > con un solo CTA: [acción]. La copy sigue esta historia: [1, 2, 3…]. Usa como inspiración y estructura
   > [link a la landing de referencia]. Escanea completo [curso/producto] y [ICP] y habla como nosotros, sin
   > AI slop. **Antes de crear la landing, crea primero el sistema de marca reutilizable**, y luego la landing.
   > Todos los assets están en Figma: [link].

4. **Ajustes de marca sobre la landing** (los que más pesaron aquí): pantallas provocativas y ligadas a la
   marca en vez de genéricas, fotos reales de los fundadores con movimiento, hero elegido con TypeSafe Jev
   para el ICP, y *"con movimiento y animación"* como parte de la marca.

5. **Extraer la carpeta de marca.**
   > Crea un sistema de marca con lo que llevamos en la landing y este proyecto, en un branch nuevo. Los
   > assets y el Figma están en [link brand system] y [link componentes]. Usa la versión más reciente de la
   > copy y haz del movimiento un componente. Referencia las URLs de Figma en el README. Copia a `brand/`
   > todos los assets que usa la landing (fondos, hero, logo, video) y úsalos desde ahí: piensa en esta
   > carpeta como algo que pego en un proyecto nuevo y replica todos los componentes y características
   > de mi marca.

## Prompts originales

### 1. Hero design para Club de Emprendedoras (2 oct 2026)

Sesión en la carpeta `emprendeconPM` (por eso no aparece bajo este proyecto en Claude desktop). Los
prompts 1 y 3 llevaban imágenes de referencia adjuntas.

> I am recreating my brand for EmprendeConPM now will be called el club de las emprendedoras, I need your
> help to create the hero design into my figm as close as possible using the fonts I have available in my
> brand: https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=3-74&m=dev But I
> need your help to become a design so that the fonts are arranged in a way that emulates what is shown in
> the image attached.
>
> Create the design at my figma here: https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=3-72&m=dev

> Mmmm getting there but still not there compare the two and try harder. I know you can do it, look at the
> detaisl of the shape and form, that is what matter.

> That was extremely solid. Next I want you to perfectly imititate the attached layout. And place it here:
> https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=34-265&m=dev the first
> image is on a pink background, the second is on merch do it as you did before so that it is super precise

### 2. ElClubDeLasEmprendedoras landing page (2–6 oct 2026, PR #1)

Primer prompt:

> Using the Figma board here and the brand assets, I need you to build our landing page for
> "ElClubDeLasEmprendedoras" It should be optimized for mobile and the only CTA we need is that they sign up
> to the waitlist by providing their email address and name.
>
> The copy in the landing page should follow the next story telling.
>
> 1. De 0 a emprendedora con una producto que vende: Preparate para ser parte de un grupo exclusivo de
>    emprnededoras que pierden el mierdo a emprender y usan la inteligencia artificial como expertas.
> 2. Este 2027 daremos un taller de 1 mes donde te llevaremos a encontrar una idea, crear una app móvil y
>    crecerla a miles de usuarios.
> 3. Es para ti si, piensas que no te estas quedando atras con el uso de inteligencia artificial, si sientes
>    que por no ser técnica no puedes emprender, .... (and find other based on the ICP).
>
> Use the Landing page from MUSA as inspo and follow the same structure:
> https://www.figma.com/design/Rayj3Upv4uARiXKufVy94t/Inspiration?node-id=1-1162&m=dev
>
> Our goal with this landing page is to repurpose our course, scan it completely. And focus on helping women
> find their business idea and convert it into a mobile app they can sell:
> https://app.notion.com/p/Curso-Crea-tu-app-con-IA-sin-saber-programar-286f2126a3a281239a74d5e18a27e9ac?source=copy_link
>
> Our target persona is her so adapt the copies to speak to her in a powerful way but without AI slop and
> similar to how we speak (Pame and I):
> https://app.notion.com/p/ICP-Ideal-User-Persona-3bbf2126a3a280f68558dd162d34acd2?source=copy_link
>
> Before creating the landing page first create the reusable brand system, and then create the landing
> page. All assets should be in Figma at:
> https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=1-2&m=dev

Follow-ups que definieron la marca (se omiten los del formulario y el Google Sheet):

> Lets improve a few things:
>
> 1. I hated the idea of yoga in the screens of the landing page. Instead, think of something more
>    provocative and tied to the brand for example for the first screen lets do: "Mi idea: Cambiar al mundo"
> 2. Add Pame and I in the last section where you speak about us. And to our names add hyperlinks to our
>    instagram profiles: https://www.instagram.com/thebreathmanu/ https://www.instagram.com/pamevls/ also add
>    our pictures instead in a aesthetic way in front of the image.
>    https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=91-423&m=dev
>    https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=92-426&m=dev
> 3. On our section, lets make the verse more inspirational. Example: "Somos Pame y Manu de emprendeconpm.
>    Este año después de apoyar muchos emprendimientos, nos dimos cuentas que la mayoría de las mujeres
>    tienen ideas increíbles, pero las tienen guardada por años por miedo. Por eso armamos este club: un
>    espacio donde preguntar lo "básico" es lo normal y donde ser mujer es una ventaja para emprender.

> More improvmeents:
>
> - The placement is not great, instead can you place us side to side and add a simple movement animation?
> - The hero on the web version layout is not ideal, it has a ton of pink empty section. Can you move the
>   drawing more or make the CTA in a better layout. On the mobile version it looks ok.

> Great can you test everything works please! I have a few more changes to the website to make:
>
> 1. I will increase the duration of everything to 8 weeks instead of 1 month. Each module will last two
>    weeks to simplify everything.
> 2. Make sure everywhere it says "más de 500 personas han tomado nuestros cursos" keep it general to
>    "cursos" not about the apps when referencing this.
> 3. improve the idas of apps (section attached) the ideas are not as provocative and they should be
>    exciting and even be good ideas for women to start.
> 4. Remove "Todo lo anterior" as an option. I hate this does not tell us anything.
> 5. Remove the whatsapp from the first registration modal, only show it in the second one.
>
> WHEN THEY REGISTER ALSO show a message that they will start receiving content every week about AI that
> will help them loose the fear to start their entrepreneurship journey.

> I made a change to the hero and description but still not convinced. Propose a few more catchy but
> concise alternatives as the one I landed one. Using Typesafe Jev model help me select the top one based
> on probably of being engaging to our ICP.

> I do want the de: "De cero a emprendedora en 8 semanas" but what description does complement it more.
> Maybe: "Se parte del club de emprendedoras que lanzan su app y se quitan el miedo a emprender" I do not
> like F thoughts?

> Lets do the this one: Convierte tu idea a una aplicación tu aplicación móvil, sin ser técnica, sin miles
> de dolares y con IA. En un grupo de mujeres que se apoyan juntas.

> I prefer the highlight on "cero a emprendedora" En Semanas 3 y 4 marca. Lets also say: "con movimiento y
> animación" which is very important in nowadays brands with AI.
>
> Also "construye tu app sin escribir código" is not correct becauwe we do writ ecode but we use AI to do
> it. Correct this.

### 3. Brand system from landing page (8 oct 2026, PR #8)

> Help me create a brand system with have we have creeated so far with the landign page and this project.
> Make this into a new branch. I forgot the first initial conversation where we created all of the landing
> page but all of the project assets and figma is at:
> https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=1-2&m=dev
> https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=47-115&m=dev
>
> Now make sure the brand voice and everythhing uses the latest version of copies, make sure a componnent
> is movement which we created in a branch.

> Make sure to in the README and reference the Figma components url.

> A few assets are missing including the background images used in here:
> https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=47-386&m=dev Also the
> main hero and logo: [imágenes adjuntas] and there in the index.html

> Great! Also in the index.html you are using a ton of the assets inside the folder of the site... lets
> make sure to add them under the /brand folder too. Think as this brand folder as if I copy past it into
> a new project it will easily replicate all the components and characteristics as my brand.
>
> Finally, make sure to add the video assets too inside the brand that we use for the landing located at:
> site/assets/video which is critical to the motion characteristic of the brand.

## Dónde están las conversaciones completas

En Claude desktop (pestaña Code):

- *Hero design para Club de Emprendedoras*: bajo el proyecto `emprendeconPM`.
- *ElClubDeLasEmprendedoras landing page* y *Brand system from landing page*: bajo este proyecto.

En disco, cada sesión es un `.jsonl` en `~/.claude/projects/<carpeta>/`:

- `-Users-manuangel-Github-emprendeconpm/bdcc7494-ac10-4601-9650-3880730049fd.jsonl` (hero en Figma)
- `-Users-manuangel-Github-clubemprendedoras--claude-worktrees-gifted-mestorf-c54fcc/b465e65b-5986-47c2-9ab7-fc06f09a5cb5.jsonl` (landing)
- `-Users-manuangel-Github-clubemprendedoras/4daa46ee-d14e-4b73-a1b9-2616a1dba01c.jsonl` (sistema de marca)
