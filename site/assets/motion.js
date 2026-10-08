(() => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // ?debug in the URL shows an on-screen log of the hero video, so it can be
  // checked on a real phone without a cable (screenshot the panel).
  const dbg = /[?&#]debug\b/.test(location.search + location.hash) ? debugPanel() : () => {};
  dbg(`ua: ${navigator.userAgent}`);
  dbg(`reduceMotion=${reduce} saveData=${!!saveData} IO=${"IntersectionObserver" in window} rVFC=${"requestVideoFrameCallback" in HTMLVideoElement.prototype}`);

  // Reduced motion: leave the static page exactly as it is.
  if (reduce) return dbg("stopped: reduced motion is on, page stays static");

  // ---- Hero: ~0.2s of the static image, then the transparent loop takes over.
  // The loop is one H.264 file with the colour on the left half and the alpha
  // matte on the right; a tiny WebGL pass turns it into real transparency, so
  // it looks the same in every browser (no VP9/HEVC alpha support needed).
  const art = document.querySelector(".hero__art");
  if (art && !saveData) startHeroLoop(art, "assets/video/club-women.mp4?v=2");

  function startHeroLoop(art, src) {
    const canvas = document.createElement("canvas");
    canvas.className = "hero__video";
    canvas.width = canvas.height = 640;
    canvas.setAttribute("aria-hidden", "true");
    const gl = canvas.getContext("webgl", { premultipliedAlpha: true, alpha: true });
    if (!gl) return dbg("stopped: no WebGL"); // the static image stays

    const video = document.createElement("video");
    // Muted *before* the source is set, as an attribute too: Safari only
    // allows autoplay for videos that start out muted.
    video.defaultMuted = true;
    video.setAttribute("muted", "");
    video.muted = true;
    video.src = src; video.loop = true; video.playsInline = true; video.preload = "auto";
    video.setAttribute("playsinline", ""); video.setAttribute("aria-hidden", "true");
    video.style.cssText = "position:absolute;width:1px;height:1px;opacity:0;pointer-events:none";
    for (const ev of ["loadedmetadata", "canplay", "playing", "pause", "waiting", "stalled", "error"]) {
      video.addEventListener(ev, () => dbg(`video ${ev}${ev === "error" && video.error ? ` code=${video.error.code}` : ""} rs=${video.readyState} t=${video.currentTime.toFixed(2)}`));
    }

    const compile = (type, code) => { const s = gl.createShader(type); gl.shaderSource(s, code); gl.compileShader(s); return s; };
    const prog = gl.createProgram();
    gl.attachShader(prog, compile(gl.VERTEX_SHADER, "attribute vec2 p;varying vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}"));
    gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, `precision mediump float;varying vec2 uv;uniform sampler2D t;
      void main(){float a=texture2D(t,vec2(.5+uv.x*.5,uv.y)).r;vec3 c=texture2D(t,vec2(uv.x*.5,uv.y)).rgb;gl_FragColor=vec4(min(c,vec3(a)),a);}`));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return dbg("stopped: shader failed to link");
    gl.useProgram(prog);
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, "p");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    for (const [k, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]]) gl.texParameteri(gl.TEXTURE_2D, k, v);

    let live = false;
    let broken = false;
    let frames = 0;
    const draw = () => {
      try {
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, video);
      } catch (error) {
        // e.g. opened from file://, where the browser won't hand video pixels to WebGL.
        console.info("[hero] Animated hero needs the page served over http(s), e.g. `npx serve site`; showing the static image.", error.name);
        dbg(`stopped: texImage2D ${error.name}`);
        broken = true; video.pause(); canvas.remove(); video.remove();
        return;
      }
      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      frames++;
      if (frames === 1 || frames % 120 === 0) {
        const px = new Uint8Array(4);
        gl.readPixels(320, 400, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
        dbg(`drew frame ${frames}, sample rgba=${px.join(",")} (alpha 0 = nothing visible)`);
      }
      if (!live) { live = true; art.classList.add("is-live"); dbg("live: video replaced the static image"); }
    };

    // Plain animation-frame loop: draw whenever the video has moved on.
    // (requestVideoFrameCallback isn't used: browsers may not fire it for a
    // video that isn't itself on screen, which this one never is.)
    let raf = 0;
    let lastTime = -1;
    const loop = () => {
      raf = 0;
      if (broken || video.paused || video.ended) return;
      if (video.readyState >= 2 && video.currentTime !== lastTime) { lastTime = video.currentTime; draw(); }
      raf = requestAnimationFrame(loop);
    };
    const startLoop = () => { if (!raf) raf = requestAnimationFrame(loop); };
    video.addEventListener("playing", startLoop);

    // Safari won't autoplay a video that isn't on screen (on phones the hero
    // art starts below the fold), so playback follows visibility: it starts
    // once the art is in view and at least 0.2s have passed, and pauses when
    // it scrolls away. It also refuses while the art is still fading in, so a
    // refused play is retried a few times.
    let visible = !("IntersectionObserver" in window);
    let warmedUp = false;
    let attempts = 0;
    const play = () => {
      if (broken || !visible || !warmedUp || !video.paused) return;
      video.play().then(() => { attempts = 0; dbg("play() ok"); startLoop(); }).catch((error) => {
        dbg(`play() refused: ${error.name}`);
        if (++attempts < 8) setTimeout(play, 250 * attempts);
      });
    };

    // iPhones in Low Power Mode block every autoplay. A tap anywhere is a user
    // gesture that unlocks this video for the rest of the visit.
    const unlock = () => {
      if (broken || !video.paused) return;
      video.play().then(() => {
        dbg("play() ok after a tap");
        if (visible) startLoop(); else video.pause();
      }).catch((error) => dbg(`play() after a tap refused: ${error.name}`));
    };
    for (const ev of ["touchend", "click", "keydown"]) document.addEventListener(ev, unlock, { passive: true });
    video.addEventListener("playing", () => {
      for (const ev of ["touchend", "click", "keydown"]) document.removeEventListener(ev, unlock);
    }, { once: true });

    art.querySelector(".hero__illustration").after(canvas); // under the stickers
    art.append(video);
    setTimeout(() => { warmedUp = true; play(); }, 200);
    video.addEventListener("canplay", play);

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(([entry]) => {
        visible = entry.isIntersecting;
        dbg(`hero ${visible ? "on" : "off"} screen`);
        if (visible) play(); else video.pause();
      }).observe(art);
    }

    if (dbg.on) setInterval(() => dbg(`status rs=${video.readyState} t=${video.currentTime.toFixed(2)} paused=${video.paused} frames=${frames} live=${live} visible=${visible}`), 3000);
  }

  function debugPanel() {
    const box = document.createElement("pre");
    box.style.cssText = "position:fixed;left:8px;right:8px;bottom:8px;z-index:9999;max-height:45vh;overflow:auto;margin:0;padding:8px;" +
      "background:rgba(23,37,74,.92);color:#F6F0E6;font:11px/1.35 ui-monospace,Menlo,monospace;white-space:pre-wrap;border-radius:10px;user-select:text";
    const t0 = performance.now();
    const log = (msg) => {
      if (!box.isConnected) document.body.append(box);
      box.textContent += `${((performance.now() - t0) / 1000).toFixed(1)}s ${msg}\n`;
      box.scrollTop = box.scrollHeight;
    };
    log.on = true;
    return log;
  }

  if (!("IntersectionObserver" in window)) return;

  // ---- Highlighted words: split into letters so they can hop in a wave.
  // Screen readers get the phrase as plain text from a visually hidden copy;
  // only the animated letters are hidden from them.
  $$("[data-jump]").forEach((el) => {
    const text = el.textContent;
    const readable = document.createElement("span");
    readable.className = "visually-hidden";
    readable.textContent = text;
    const letters = document.createElement("span");
    letters.setAttribute("aria-hidden", "true");
    [...text].forEach((ch, i) => {
      if (ch === " ") return letters.append(" ");
      const span = document.createElement("span");
      span.className = "jump__ch";
      span.style.setProperty("--i", i);
      span.textContent = ch;
      letters.append(span);
    });
    el.replaceChildren(readable, letters);
  });

  // ---- Scroll reveals.
  const groups = [
    [".hero .kicker, .hero .display, .hero .lead, .hero .waitlist, .hero__proof", "up"],
    [".hero__art", "drop"],
    [".band__inner > *", "up"],
    [".section__head > *", "up"],
    [".phone", "drop"],
    [".card-week", "up"],
    [".for-you__item", "drop"],
    [".not-for-you", "up"],
    [".section__foot", "up"],
    [".about__photo", "drop"],
    [".about__copy > *", "up"],
    [".perk", "up"],
    [".faq__item", "up"],
    [".cta__inner > *", "up"],
    [".footer > *", "up"],
  ];
  const seen = new Set();
  const targets = [];
  for (const [selector, kind] of groups) {
    for (const el of $$(selector)) {
      if (seen.has(el)) continue;
      seen.add(el);
      el.dataset.reveal = kind;
      targets.push(el);
    }
  }
  // Stagger siblings that arrive together; a phone leads its card.
  // The step comes from the --stagger-reveal token (tokens.css), 90ms if it's missing.
  const staggerReveal = (() => {
    const v = getComputedStyle(document.documentElement).getPropertyValue("--stagger-reveal").trim();
    const n = parseFloat(v);
    if (!v || Number.isNaN(n)) return 90;
    return v.endsWith("ms") ? n : v.endsWith("s") ? n * 1000 : n;
  })();
  const perParent = new Map();
  for (const el of targets) {
    const n = perParent.get(el.parentElement) || 0;
    perParent.set(el.parentElement, n + 1);
    let delay = Math.min(n, 6) * staggerReveal;
    if (el.classList.contains("card-week")) delay = 160;
    el.style.setProperty("--d", `${delay}ms`);
  }

  const reveal = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting && entry.boundingClientRect.top > 0) continue;
      entry.target.classList.add("is-in");
      reveal.unobserve(entry.target);
    }
  }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
  targets.forEach((el) => reveal.observe(el));

  // ---- Ideas: a heap just under the heading -> sorted into place.
  const chipsWrap = document.querySelector(".chips");
  const chips = chipsWrap ? $$(".sticker", chipsWrap) : [];
  if (chips.length) {
    const rand = (i, salt) => { const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453; return x - Math.floor(x); };
    chipsWrap.style.position = "relative";
    chips.forEach((chip, i) => chip.style.setProperty("--i", i));

    const heap = document.createElement("span");
    heap.setAttribute("aria-hidden", "true");
    heap.style.cssText = "position:absolute;left:0;width:1px;height:1px;pointer-events:none";
    chipsWrap.append(heap);
    let heapY = 0;

    const buildPile = () => {
      const w = chipsWrap.clientWidth;
      // Heap sits just under the heading (where the eye already is), not in the
      // middle of a list that is ~12 rows tall on phones.
      heapY = Math.min(chipsWrap.clientHeight / 2, 150);
      heap.style.top = `${heapY}px`;
      chips.forEach((chip, i) => {
        // offsetLeft/Top ignore transforms, so this is the chip's real slot.
        const cx = chip.offsetLeft + chip.offsetWidth / 2;
        const cy = chip.offsetTop + chip.offsetHeight / 2;
        const spread = Math.min(w * 0.26, 170);
        const px = w / 2 + (rand(i, 1) - 0.5) * 2 * spread;
        const py = heapY + (rand(i, 2) - 0.5) * 60;
        chip.style.setProperty("--px", `${(px - cx).toFixed(1)}px`);
        chip.style.setProperty("--py", `${(py - cy).toFixed(1)}px`);
        chip.style.setProperty("--pr", `${((rand(i, 3) - 0.5) * 40).toFixed(1)}deg`);
        chip.style.zIndex = Math.floor(rand(i, 4) * chips.length);
      });
    };

    let sorted = false;
    const onResize = () => { if (!sorted) buildPile(); };
    buildPile();
    document.fonts && document.fonts.ready.then(onResize);
    window.addEventListener("resize", onResize);

    // Sort once the heap is well inside the screen.
    const sortObserver = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting && entry.boundingClientRect.top > 0) return;
      sortObserver.disconnect();
      sorted = true;
      setTimeout(() => chipsWrap.classList.add("is-sorted"), 300);
    }, { rootMargin: "0px 0px -15% 0px" });
    sortObserver.observe(heap);
  }

  // Turn the "before" states on only once everything above is wired up.
  document.documentElement.classList.add("motion");
})();
