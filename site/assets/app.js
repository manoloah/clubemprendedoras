(() => {
  const config = window.CLUB_WAITLIST || {};
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  const isLocal = ["localhost", "127.0.0.1", ""].includes(location.hostname);

  // Sticky nav gets a hairline once the page scrolls.
  const nav = document.querySelector("[data-nav]");
  if (nav) {
    const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Keep campaign data so we know which post or ad brought each signup.
  const params = new URLSearchParams(location.search);
  const attribution = {};
  for (const key of ["utm_source", "utm_medium", "utm_campaign", "utm_content"]) {
    const value = params.get(key);
    if (value) attribution[key] = value.slice(0, 200);
  }
  if (document.referrer) attribution.referrer = document.referrer.slice(0, 500);

  // Posts to the Apps Script web app. JSON goes as text/plain so the
  // browser skips the CORS preflight Apps Script can't answer.
  async function send(payload) {
    if (!config.endpoint) {
      if (isLocal) {
        console.info("[waitlist] No endpoint configured; local preview only.", payload);
        return;
      }
      throw new Error("Waitlist endpoint not configured (assets/config.js)");
    }
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 15000);
    const request = {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(payload),
      signal: ctrl.signal,
    };
    let out;
    try {
      const res = await fetch(config.endpoint, request);
      out = await res.json();
    } catch (error) {
      if (ctrl.signal.aborted) throw error;
      // Apps Script saves the row, then 302-redirects to googleusercontent
      // for the reply. Some in-app browsers (Instagram's) fail that second
      // hop, so the save worked but we can't read the answer. Re-send without
      // CORS: the save is idempotent per email, and an opaque reply that
      // arrives at all means Apps Script got it.
      console.warn("[waitlist] reply unreadable, retrying no-cors", error);
      await fetch(config.endpoint, { ...request, mode: "no-cors" });
      return;
    } finally {
      clearTimeout(timer);
    }
    if (!out.ok) throw new Error(out.error || "not ok");
  }

  function setError(input, errorEl, message) {
    input.setAttribute("aria-invalid", "true");
    if (errorEl) {
      errorEl.textContent = message;
      errorEl.hidden = false;
      input.setAttribute("aria-describedby", errorEl.id);
    }
  }

  function clearError(input, errorEl) {
    input.removeAttribute("aria-invalid");
    if (errorEl) {
      errorEl.hidden = true;
      errorEl.textContent = "";
    }
  }

  function showSuccess(form, name) {
    const tpl = document.getElementById("waitlist-success");
    const node = tpl.content.firstElementChild.cloneNode(true);
    node.querySelector("[data-success-title]").textContent = `¡Ya estás dentro, ${name}!`;
    form.replaceWith(node);
    return node;
  }

  // Step 2: optional profile questions in a modal, saved to the same row.
  const dialog = document.getElementById("profile");
  const profileForm = dialog.querySelector("form");
  const profileStatus = profileForm.querySelector(".waitlist__status");
  const profileButton = profileForm.querySelector("button[type=submit]");
  let profileEmail = "";
  let profileReturn = null;

  function openProfile(email, firstName, returnFocus) {
    profileEmail = email;
    profileReturn = returnFocus;
    dialog.querySelector("[data-profile-name]").textContent = `¡Listo, ${firstName}!`;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else returnFocus.focus();
  }

  function closeProfile() {
    dialog.close();
    if (profileReturn) profileReturn.focus();
  }

  dialog.addEventListener("close", () => profileReturn && profileReturn.focus());
  dialog.querySelectorAll("[data-profile-skip]").forEach((b) => b.addEventListener("click", closeProfile));
  dialog.addEventListener("click", (e) => { if (e.target === dialog) closeProfile(); });

  profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    profileStatus.textContent = "";
    const answers = { email: profileEmail };
    for (const [key, value] of new FormData(profileForm)) {
      const v = String(value).trim();
      if (!v) continue;
      answers[key] = answers[key] ? `${answers[key]}, ${v}` : v;
    }
    if (Object.keys(answers).length === 1) return closeProfile();

    profileButton.disabled = true;
    const label = profileButton.querySelector(".btn__label");
    label.textContent = "Guardando…";
    try {
      await send(answers);
      if (profileReturn) {
        profileReturn.querySelector("p:not(.h3)").textContent =
          "Gracias por contarnos de ti. Con esto armamos el taller pensando en ti. Desde esta semana te llega contenido sobre IA para que le pierdas el miedo a emprender, y te avisamos antes que a nadie cuando abramos.";
      }
      closeProfile();
    } catch (error) {
      console.error("[waitlist profile]", error);
      profileStatus.textContent = "No pudimos guardar tus respuestas. Intenta otra vez en un momento.";
    } finally {
      profileButton.disabled = false;
      label.textContent = "Enviar mis respuestas";
    }
  });

  document.querySelectorAll("[data-waitlist]").forEach((form) => {
    const nameInput = form.elements.name;
    const emailInput = form.elements.email;
    const emailError = emailInput.parentElement.querySelector(".field__error");
    const status = form.querySelector(".waitlist__status");
    const button = form.querySelector("button[type=submit]");
    const buttonLabel = button.querySelector(".btn__label");

    nameInput.addEventListener("input", () => clearError(nameInput));
    emailInput.addEventListener("input", () => clearError(emailInput, emailError));

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      status.textContent = "";

      // Bots fill the hidden field; people never see it.
      if (form.elements.company.value) return;

      const name = nameInput.value.trim().replace(/\s+/g, " ");
      const email = emailInput.value.trim().toLowerCase();
      let firstInvalid = null;

      if (!name) {
        setError(nameInput);
        status.textContent = "Dinos cómo te llamas para guardarte el lugar.";
        firstInvalid = nameInput;
      }
      if (!EMAIL_RE.test(email)) {
        setError(emailInput, emailError, "Revisa tu correo, parece que le falta algo.");
        firstInvalid = firstInvalid || emailInput;
      }
      if (firstInvalid) {
        firstInvalid.focus();
        return;
      }

      button.disabled = true;
      const original = buttonLabel.textContent;
      buttonLabel.textContent = "Guardando tu lugar…";

      try {
        await send({
          nombre: name.slice(0, 120),
          email: email.slice(0, 254),
          company: form.elements.company.value,
          source: config.source || "landing-2027",
          ...attribution,
        });
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({ event: "waitlist_signup", source: config.source });
        if (typeof window.fbq === "function") window.fbq("track", "Lead");
        const firstName = name.split(" ")[0];
        const success = showSuccess(form, firstName);
        openProfile(email, firstName, success);
      } catch (error) {
        console.error("[waitlist]", error);
        status.textContent = "Ups, no pudimos guardar tu lugar. Intenta de nuevo en un momento.";
        button.disabled = false;
        buttonLabel.textContent = original;
      }
    });
  });
})();
