(function () {
  const mqMobile = window.matchMedia("(max-width: 960px)");
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  const backdrop = document.querySelector(".nav-backdrop");
  const dropdowns = Array.from(document.querySelectorAll(".nav-item-dropdown"));

  if (backdrop) backdrop.removeAttribute("hidden");

  let lockedScrollY = 0;

  function lockScroll() {
    // Capture scroll, then lock both html and body. Compensate for the
    // disappearing scrollbar so desktop layout doesn't shift.
    lockedScrollY = window.scrollY || document.documentElement.scrollTop || 0;
    const scrollbar = window.innerWidth - document.documentElement.clientWidth;
    document.documentElement.style.overflow = "hidden";
    document.body.style.overflow = "hidden";
    if (scrollbar > 0) {
      document.documentElement.style.paddingRight = scrollbar + "px";
    }
  }
  function unlockScroll() {
    document.documentElement.style.overflow = "";
    document.body.style.overflow = "";
    document.documentElement.style.paddingRight = "";
    // Some browsers reset scroll when toggling overflow:hidden — restore it.
    window.scrollTo(0, lockedScrollY);
  }

  function closeMobileNav() {
    if (!nav) return;
    const wasOpen = nav.classList.contains("is-open");
    nav.classList.remove("is-open");
    document.body.classList.remove("nav-open");
    if (wasOpen) unlockScroll();
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Odpri meni");
    }
    dropdowns.forEach((d) => d.setAttribute("aria-expanded", "false"));
  }

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = !nav.classList.contains("is-open");
      if (open) lockScroll();
      else unlockScroll();
      nav.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Zapri meni" : "Odpri meni");
    });
  }

  if (backdrop) backdrop.addEventListener("click", closeMobileNav);

  dropdowns.forEach((dd) => {
    const trigger = dd.querySelector(".nav-link");
    if (!trigger) return;

    trigger.addEventListener("click", (e) => {
      if (mqMobile.matches) {
        e.preventDefault();
        const expanded = dd.getAttribute("aria-expanded") === "true";
        dropdowns.forEach((other) => {
          if (other !== dd) other.setAttribute("aria-expanded", "false");
        });
        dd.setAttribute("aria-expanded", expanded ? "false" : "true");
      }
    });

    // Desktop keyboard: expand on Enter when focused
    trigger.addEventListener("keydown", (e) => {
      if (!mqMobile.matches && (e.key === "ArrowDown" || e.key === "Enter")) {
        const first = dd.querySelector(".dropdown-link");
        if (first) {
          e.preventDefault();
          dd.setAttribute("aria-expanded", "true");
          first.focus();
        }
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      dropdowns.forEach((d) => d.setAttribute("aria-expanded", "false"));
      if (nav && nav.classList.contains("is-open")) closeMobileNav();
    }
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".nav-item-dropdown") && !mqMobile.matches) {
      dropdowns.forEach((d) => d.setAttribute("aria-expanded", "false"));
    }
    if (
      nav &&
      nav.classList.contains("is-open") &&
      !e.target.closest(".site-nav") &&
      !e.target.closest(".nav-toggle")
    ) {
      closeMobileNav();
    }
  });

  mqMobile.addEventListener("change", () => {
    closeMobileNav();
  });

  // Close mobile nav when clicking a non-dropdown link
  if (nav) {
    nav.querySelectorAll("a:not(.nav-item-dropdown > .nav-link)").forEach((link) => {
      link.addEventListener("click", () => {
        if (mqMobile.matches) closeMobileNav();
      });
    });
  }

  // Contact form — web3forms (AJAX submit, inline status)
  const form = document.querySelector("form[data-web3forms]");
  if (form) {
    const status = form.querySelector(".form-status");
    const submit = form.querySelector("button[type='submit']");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (status) {
        status.textContent = "";
        status.className = "form-status";
      }
      // hCaptcha: block submit until widget is solved
      const captchaField = form.querySelector("textarea[name='h-captcha-response']");
      if (form.querySelector(".h-captcha") && (!captchaField || !captchaField.value)) {
        if (status) {
          status.textContent = "Prosim, potrdi, da nisi robot.";
          status.classList.add("is-error");
        }
        return;
      }
      if (submit) {
        submit.disabled = true;
        submit.dataset.originalLabel = submit.dataset.originalLabel || submit.innerHTML;
        submit.innerHTML = "Pošiljam…";
      }
      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: new FormData(form),
        });
        const data = await res.json().catch(() => ({}));
        if (res.ok && data.success) {
          form.reset();
          if (status) {
            status.textContent = "Hvala — sporočilo je oddano. Odgovorim ti v najkrajšem možnem času.";
            status.classList.add("is-success");
          }
        } else {
          throw new Error((data && data.message) || "Napaka pri pošiljanju.");
        }
      } catch (err) {
        if (status) {
          status.textContent =
            "Sporočila ni bilo mogoče oddati. Poskusi znova ali piši neposredno na tea@teaknez.com.";
          status.classList.add("is-error");
        }
      } finally {
        if (submit) {
          submit.disabled = false;
          if (submit.dataset.originalLabel) submit.innerHTML = submit.dataset.originalLabel;
        }
      }
    });
  }

  // Modal — open via [data-open-modal="id"], close via [data-modal-close] or Escape
  const modalTriggers = document.querySelectorAll("[data-open-modal]");
  if (modalTriggers.length) {
    let lastFocused = null;
    function openModal(modal) {
      lastFocused = document.activeElement;
      modal.hidden = false;
      document.body.classList.add("modal-open");
      lockScroll();
      const focusable = modal.querySelector("input, textarea, button, [href]");
      if (focusable) focusable.focus({ preventScroll: true });
    }
    function closeModal(modal) {
      modal.hidden = true;
      document.body.classList.remove("modal-open");
      unlockScroll();
      if (lastFocused && typeof lastFocused.focus === "function") lastFocused.focus();
    }
    modalTriggers.forEach((trigger) => {
      trigger.addEventListener("click", (e) => {
        e.preventDefault();
        const id = trigger.getAttribute("data-open-modal");
        const modal = document.getElementById(id);
        if (modal) openModal(modal);
      });
    });
    document.querySelectorAll(".modal [data-modal-close]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const modal = btn.closest(".modal");
        if (modal) closeModal(modal);
      });
    });
    document.addEventListener("keydown", (e) => {
      if (e.key !== "Escape") return;
      const openOne = document.querySelector(".modal:not([hidden])");
      if (openOne) closeModal(openOne);
    });
  }
})();
