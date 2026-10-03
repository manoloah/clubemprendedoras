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

  async function submitLead(lead) {
    if (config.supabaseUrl && config.supabaseAnonKey) {
      // join_waitlist() returns the same empty 204 for new and existing emails.
      const res = await fetch(
        `${config.supabaseUrl.replace(/\/$/, "")}/rest/v1/rpc/join_waitlist`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            apikey: config.supabaseAnonKey,
            Authorization: `Bearer ${config.supabaseAnonKey}`,
          },
          body: JSON.stringify({
            p_name: lead.name,
            p_email: lead.email,
            p_source: lead.source,
            p_utm_source: lead.utm_source ?? null,
            p_utm_medium: lead.utm_medium ?? null,
            p_utm_campaign: lead.utm_campaign ?? null,
            p_utm_content: lead.utm_content ?? null,
            p_referrer: lead.referrer ?? null,
          }),
        }
      );
      if (res.ok) return;
      throw new Error(`Supabase ${res.status}`);
    }
    if (config.endpoint) {
      const res = await fetch(config.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(lead),
      });
      if (res.ok) return;
      throw new Error(`Endpoint ${res.status}`);
    }
    if (isLocal) {
      console.info("[waitlist] No backend configured; local preview only.", lead);
      return;
    }
    throw new Error("Waitlist backend not configured (assets/config.js)");
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
    node.focus();
  }

  document.querySelectorAll("[data-waitlist]").forEach((form) => {
    const nameInput = form.elements.name;
    const emailInput = form.elements.email;
    const emailError = form.querySelector(".field__error");
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
        await submitLead({
          name: name.slice(0, 120),
          email: email.slice(0, 254),
          source: config.source || "landing-2027",
          ...attribution,
        });
        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({ event: "waitlist_signup", source: config.source });
        if (typeof window.fbq === "function") window.fbq("track", "Lead");
        showSuccess(form, name.split(" ")[0]);
      } catch (error) {
        console.error("[waitlist]", error);
        status.textContent = "Ups, no pudimos guardar tu lugar. Intenta de nuevo en un momento.";
        button.disabled = false;
        buttonLabel.textContent = original;
      }
    });
  });
})();
