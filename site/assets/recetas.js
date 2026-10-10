// Recetas: the signup gate and the "Copiar" buttons.
// The gate itself is decided before paint by the inline script in each
// receta's <head>, which adds html.is-gated unless she came from the
// newsletter (utm_source=newsletter) or already signed up on this browser.
(() => {
  const config = window.CLUB_WAITLIST || {};
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const KEY = "club_receta_ok";
  const root = document.documentElement;

  // Sticky nav gets a hairline once the page scrolls (same as app.js).
  const nav = document.querySelector("[data-nav]");
  if (nav) {
    const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // ---- Copy buttons: <button data-copy="id-of-pre">.
  document.querySelectorAll("[data-copy]").forEach((button) => {
    const label = button.querySelector(".btn__label") || button;
    const original = label.textContent;
    button.addEventListener("click", async () => {
      const text = document.getElementById(button.dataset.copy).innerText;
      try {
        await navigator.clipboard.writeText(text);
      } catch (_) {
        // Older in-app browsers: select the text so a long-press copies it.
        const range = document.createRange();
        range.selectNodeContents(document.getElementById(button.dataset.copy));
        getSelection().removeAllRanges();
        getSelection().addRange(range);
        label.textContent = "Selecciónalo y copia";
        return;
      }
      label.textContent = "¡Copiado! ✓";
      setTimeout(() => { label.textContent = original; }, 2200);
    });
  });

  const gate = document.querySelector("[data-gate]");
  const locked = document.querySelector("[data-locked]");
  if (!gate || !locked) return;

  const unlock = () => {
    try { localStorage.setItem(KEY, "1"); } catch (_) { /* private mode: unlocked for this visit */ }
    root.classList.remove("is-gated");
    locked.classList.add("is-unlocked");
  };
  if (!root.classList.contains("is-gated")) return;

  // Same backend and payload as the landing's waitlist form (app.js). The
  // Sheet keeps one row per email and never overwrites, so a member who
  // types her email again just unlocks; nothing tells the page who's on the list.
  async function send(payload) {
    if (!config.endpoint) return console.info("[receta] No endpoint configured; local preview only.", payload);
    const request = { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(payload) };
    try {
      const res = await fetch(config.endpoint, request);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const out = await res.json();
      if (!out.ok) throw new Error(out.error || "not ok");
    } catch (error) {
      // Instagram's in-app browser can fail Apps Script's redirect after the
      // row is saved (see app.js). Retry without CORS; the save is idempotent.
      if (!(error instanceof TypeError)) throw error;
      await fetch(config.endpoint, { ...request, mode: "no-cors" });
    }
  }

  const form = gate.querySelector("form");
  const status = form.querySelector(".waitlist__status");
  const button = form.querySelector("button[type=submit]");
  const label = button.querySelector(".btn__label");
  const params = new URLSearchParams(location.search);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    status.textContent = "";
    if (form.elements.company.value) return; // honeypot

    const name = form.elements.name.value.trim().replace(/\s+/g, " ");
    const email = form.elements.email.value.trim().toLowerCase();
    if (!name) { status.textContent = "Dinos cómo te llamas."; return form.elements.name.focus(); }
    if (!EMAIL_RE.test(email)) { status.textContent = "Revisa tu correo, parece que le falta algo."; return form.elements.email.focus(); }

    button.disabled = true;
    const original = label.textContent;
    label.textContent = "Abriendo tu receta…";
    const payload = { nombre: name.slice(0, 120), email: email.slice(0, 254), company: "", source: gate.dataset.gate };
    for (const key of ["utm_source", "utm_medium", "utm_campaign", "utm_content"]) {
      if (params.get(key)) payload[key] = params.get(key).slice(0, 200);
    }
    if (document.referrer) payload.referrer = document.referrer.slice(0, 500);

    try {
      await send(payload);
      unlock();
      const first = document.getElementById("paso-1");
      if (first) first.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      console.error("[receta]", error);
      status.textContent = "Ups, no pudimos abrirla. Intenta de nuevo en un momento.";
      button.disabled = false;
      label.textContent = original;
    }
  });
})();
