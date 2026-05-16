(function () {
  const mqMobile = window.matchMedia("(max-width: 960px)");
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  const dropdowns = Array.from(document.querySelectorAll(".nav-item-dropdown"));

  function closeMobileNav() {
    if (!nav) return;
    nav.classList.remove("is-open");
    document.body.classList.remove("nav-open");
    if (toggle) {
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Odpri meni");
    }
    dropdowns.forEach((d) => d.setAttribute("aria-expanded", "false"));
  }

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = !nav.classList.contains("is-open");
      nav.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Zapri meni" : "Odpri meni");
    });
  }

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
})();
