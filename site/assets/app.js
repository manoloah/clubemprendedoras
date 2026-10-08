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
    let res;
    try {
      try {
        res = await fetch(config.endpoint, request);
      } catch (error) {
        // A TypeError here (not a timeout) is a network/CORS failure. Apps
        // Script saves the row, then 302-redirects to googleusercontent for
        // the reply, and some in-app browsers (Instagram's) fail that hop.
        // Re-send without CORS: the save is idempotent per email. We can't
        // read an opaque reply, so this is best effort. Any reply we *can*
        // read (an HTTP error, HTML, ok:false) still counts as a failure.
        if (ctrl.signal.aborted || !(error instanceof TypeError)) throw error;
        console.warn("[waitlist] reply unreadable, retrying no-cors", error);
        await fetch(config.endpoint, { ...request, mode: "no-cors" });
        return;
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const out = await res.json();
      if (!out.ok) throw new Error(out.error || "not ok");
    } finally {
      clearTimeout(timer);
    }
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

  // Step 2: optional profile questions, one at a time (Typeform style).
  // Answers are saved in the background as she goes, so nobody waits on
  // Apps Script and an abandoned survey still keeps what was answered.
  const dialog = document.getElementById("profile");
  const profileForm = dialog.querySelector("form");
  const steps = [...dialog.querySelectorAll("[data-step]")];
  const progress = dialog.querySelector("[data-progress]");
  const prevBtn = dialog.querySelector(".profile__nav [data-prev]");
  const nextBtn = dialog.querySelector(".profile__nav [data-next]");
  const KEYS = "ABCDEFGHIJ";
  let profileEmail = "";
  let profileReturn = null;
  let current = 0;
  let lastSent = "";
  let answered = false;

  steps.forEach((step) => {
    step.querySelectorAll(".chip span").forEach((span, i) => { span.dataset.key = KEYS[i]; });
  });

  function collect() {
    const answers = {};
    for (const [key, value] of new FormData(profileForm)) {
      const v = String(value).trim();
      if (!v) continue;
      answers[key] = answers[key] ? `${answers[key]}, ${v}` : v;
    }
    return answers;
  }

  // Sends the answers so far if anything changed since the last save. The
  // backend only fills empty cells, so repeats are harmless. When the page is
  // going away, a beacon survives the unload where a plain fetch may not.
  function flush(exiting) {
    const answers = collect();
    if (!profileEmail || !Object.keys(answers).length) return;
    const payload = { email: profileEmail, ...answers };
    const body = JSON.stringify(payload);
    if (body === lastSent) return;
    lastSent = body;
    answered = true;
    if (exiting && config.endpoint && navigator.sendBeacon &&
        navigator.sendBeacon(config.endpoint, new Blob([body], { type: "text/plain;charset=utf-8" }))) return;
    send(payload).catch((error) => {
      console.error("[waitlist profile]", error);
      lastSent = "";
    });
  }

  function show(index) {
    const from = current;
    current = Math.max(0, Math.min(steps.length - 1, index));
    steps.forEach((step, i) => {
      step.hidden = i !== current;
      step.classList.remove("is-in", "from-top");
    });
    const step = steps[current];
    void step.offsetWidth;
    step.classList.add("is-in");
    if (current < from) step.classList.add("from-top");
    progress.style.width = `${(current / (steps.length - 1)) * 100}%`;
    prevBtn.disabled = current === 0;
    nextBtn.disabled = current >= steps.length - 2;
    dialog.classList.toggle("is-done", current === steps.length - 1);
    dialog.querySelector(".profile__body").scrollTop = 0;
    // Focus text fields; on choice questions focus the first option so
    // keyboard users can arrow through, without popping the phone keyboard.
    const field = step.querySelector("input[type=text], input[type=tel], textarea");
    if (field && matchMedia("(hover: hover)").matches) field.focus({ preventScroll: true });
    else (step.querySelector("[data-next], button") || step).focus({ preventScroll: true });
  }

  // Saves in batches (every 4th question and at the end) rather than per
  // answer: Apps Script allows MAX_PER_MINUTE saves across the whole site.
  function next() {
    const to = current + 1;
    if (to % 4 === 0 || to >= steps.length - 1) flush();
    show(to);
  }

  function openProfile(email, firstName, returnFocus) {
    if (email !== profileEmail) {
      // A second signup on the same page starts from a blank survey.
      profileForm.reset();
      lastSent = "";
      answered = false;
    }
    profileEmail = email;
    profileReturn = returnFocus;
    dialog.querySelector("[data-profile-name]").textContent = `¡Listo, ${firstName}!`;
    if (typeof dialog.showModal !== "function") return returnFocus.focus();
    dialog.showModal();
    show(0);
  }

  function closeProfile() {
    flush();
    if (answered && profileReturn) {
      profileReturn.querySelector("p:not(.h3)").textContent =
        "Gracias por contarnos de ti. Con esto armamos el taller pensando en ti. Desde esta semana te llega contenido sobre IA para que le pierdas el miedo a emprender, y te avisamos antes que a nadie cuando abramos.";
    }
    if (dialog.open) dialog.close();
  }

  dialog.addEventListener("close", () => profileReturn && profileReturn.focus());
  dialog.addEventListener("cancel", () => flush());
  dialog.querySelectorAll("[data-profile-skip]").forEach((b) => b.addEventListener("click", closeProfile));
  dialog.querySelectorAll("[data-next]").forEach((b) => b.addEventListener("click", next));
  prevBtn.addEventListener("click", () => show(current - 1));
  profileForm.addEventListener("submit", (e) => { e.preventDefault(); next(); });
  document.addEventListener("visibilitychange", () => { if (document.hidden && dialog.open) flush(true); });

  // Single-choice questions move on by themselves, like Typeform.
  profileForm.addEventListener("change", (e) => {
    const step = e.target.closest("[data-step]");
    if (e.target.type === "radio" && step && step.hasAttribute("data-auto")) {
      setTimeout(() => { if (steps[current] === step) next(); }, 350);
    }
  });

  dialog.addEventListener("keydown", (e) => {
    const step = steps[current];
    const inText = e.target.matches("input[type=text], input[type=tel], textarea");
    if (e.key === "Enter" && !e.shiftKey && !(e.target.tagName === "TEXTAREA" && !e.metaKey && !e.ctrlKey)) {
      if (e.target.tagName === "BUTTON") return;
      e.preventDefault();
      next();
      return;
    }
    // A, B, C… pick an option on choice questions.
    if (!inText && !e.metaKey && !e.ctrlKey && !e.altKey && /^[a-j]$/i.test(e.key)) {
      const input = step.querySelectorAll(".chip input")[KEYS.indexOf(e.key.toUpperCase())];
      if (input) {
        e.preventDefault();
        input.checked = input.type === "checkbox" ? !input.checked : true;
        input.dispatchEvent(new Event("change", { bubbles: true }));
      }
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
