// Hotmart checkout inside the page.
//
// Markup: <a class="btn" href="https://pay.hotmart.com/CODE?checkoutMode=10" data-checkout="CODE" data-sck="landing">
// Without JS the link opens Hotmart's own checkout page. With JS a tap opens the
// embedded checkout (checkoutMode=2) in a <dialog>: full screen on phones, a
// window on desktop.
//
// We don't use Hotmart's widget.min.js: on phones it skips the lightbox and
// sends people to Hotmart anyway, it pulls in jQuery and fancybox, and if its
// health check fails it deletes every hotmart.com link on the page.
(() => {
  const links = document.querySelectorAll("a[data-checkout]");
  if (!links.length) return;

  const params = new URLSearchParams(location.search);
  let dialog, frame, fallback, current;

  function checkoutUrl(code, mode, sck) {
    const url = new URL(`https://pay.hotmart.com/${encodeURIComponent(code)}`);
    url.searchParams.set("checkoutMode", mode);
    // src and sck show up in Hotmart's sales report, so we know what sold.
    url.searchParams.set("src", (params.get("utm_source") || "web").slice(0, 60));
    url.searchParams.set("sck", (sck || "club").slice(0, 60));
    return url.toString();
  }

  function build() {
    dialog = document.createElement("dialog");
    dialog.className = "checkout";
    dialog.setAttribute("aria-label", "Pago seguro con Hotmart");
    dialog.innerHTML = `
      <div class="checkout__bar">
        <p class="checkout__title">Pago seguro con Hotmart</p>
        <button class="checkout__close" type="button" aria-label="Cerrar">×</button>
      </div>
      <div class="checkout__body">
        <p class="checkout__loading">Cargando el pago…</p>
        <iframe class="checkout__frame" title="Pago con Hotmart" allow="payment *" referrerpolicy="strict-origin-when-cross-origin"></iframe>
      </div>
      <p class="checkout__foot">¿No carga? <a target="_blank" rel="noopener">Abre el pago en Hotmart</a></p>`;
    document.body.appendChild(dialog);
    frame = dialog.querySelector("iframe");
    fallback = dialog.querySelector(".checkout__foot a");
    dialog.querySelector(".checkout__close").addEventListener("click", () => dialog.close());
    // A tap on the backdrop (the dialog box itself, outside its content) closes it.
    dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener("close", () => {
      document.documentElement.classList.remove("is-checkout");
      if (current) current.focus();
    });
  }

  function open(link) {
    if (!dialog) build();
    const code = link.dataset.checkout;
    // Reopening the same course keeps what she already typed, so the first
    // button she tapped for it is the one Hotmart credits, on both paths.
    if (frame.dataset.code !== code) {
      frame.dataset.code = code;
      frame.dataset.sck = link.dataset.sck || "";
      frame.src = checkoutUrl(code, "2", frame.dataset.sck);
    }
    fallback.href = checkoutUrl(code, "10", frame.dataset.sck);
    current = link;
    document.documentElement.classList.add("is-checkout");
    dialog.showModal();
  }

  links.forEach((link) => {
    link.addEventListener("click", (e) => {
      if (typeof HTMLDialogElement !== "function" || e.metaKey || e.ctrlKey) return;
      e.preventDefault();
      open(link);
    });
  });
})();
