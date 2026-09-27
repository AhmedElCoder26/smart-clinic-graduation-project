/*!
 * Smart Clinic — main.js
 * Site-wide UI enhancements: safe to include on every page via base.html.
 * Every feature checks for its own elements before running, so this file
 * never throws on a page that doesn't have a particular component.
 */
(function () {
  "use strict";

  const prefersReducedMotion =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.addEventListener("DOMContentLoaded", () => {
    initNavbarScrollEffect();
    initActiveNavLink();
    initAutoDismissAlerts();
    initCardRevealAnimation();
    initFormLoadingState();
    initBackToTop();
    initDoctorSearch();
  });

  /* 1. Navbar gets a stronger shadow / blur once the page is scrolled ------ */
  function initNavbarScrollEffect() {
    const navbar = document.querySelector(".navbar");
    if (!navbar) return;

    const toggle = () => {
      navbar.classList.toggle("navbar-scrolled", window.scrollY > 12);
    };
    toggle();
    window.addEventListener("scroll", toggle, { passive: true });
  }

  /* 2. Highlight the nav link matching the current page --------------------*/
  function initActiveNavLink() {
    const links = document.querySelectorAll(".navbar .nav-link");
    if (!links.length) return;

    const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";
    links.forEach((link) => {
      const linkPath = (link.getAttribute("href") || "").replace(/\/+$/, "") || "/";
      if (linkPath && linkPath !== "/" && currentPath.startsWith(linkPath)) {
        link.classList.add("active");
      }
    });
  }

  /* 3. Auto-dismiss success/info alerts after a few seconds ----------------*/
  function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll(".alert.alert-dismissible");
    if (!alerts.length) return;

    alerts.forEach((alert) => {
      let timer = setTimeout(() => dismiss(alert), 5000);
      alert.addEventListener("mouseenter", () => clearTimeout(timer));
      alert.addEventListener("mouseleave", () => {
        timer = setTimeout(() => dismiss(alert), 2500);
      });
    });

    function dismiss(alert) {
      if (!alert.isConnected) return;
      // Prefer Bootstrap's own Alert API if it loaded; otherwise fade manually.
      if (window.bootstrap && window.bootstrap.Alert) {
        window.bootstrap.Alert.getOrCreateInstance(alert).close();
      } else {
        alert.style.transition = "opacity .4s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 400);
      }
    }
  }

  /* 4. Gentle reveal animation for cards as they scroll into view ----------*/
  function initCardRevealAnimation() {
    const cards = document.querySelectorAll(".card");
    if (!cards.length || prefersReducedMotion || !("IntersectionObserver" in window)) return;

    cards.forEach((card) => card.classList.add("reveal-on-scroll"));

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );

    cards.forEach((card) => observer.observe(card));
  }

  /* 5. Show a spinner + disable the submit button on plain forms -----------*/
  function initFormLoadingState() {
    // Forms that already ask for a confirm() (e.g. Cancel Appointment) manage
    // their own submit flow, so we deliberately leave them alone.
    const forms = document.querySelectorAll("form:not([onsubmit]):not(#chat-form)");
    if (!forms.length) return;

    forms.forEach((form) => {
      form.addEventListener("submit", () => {
        const btn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (!btn || btn.disabled) return;
        btn.dataset.originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Please wait…';
      });
    });
  }

  /* 6. Floating "back to top" button ---------------------------------------*/
  function initBackToTop() {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "back-to-top";
    btn.setAttribute("aria-label", "Back to top");
    btn.innerHTML = "↑";
    document.body.appendChild(btn);

    const toggle = () => btn.classList.toggle("visible", window.scrollY > 400);
    toggle();
    window.addEventListener("scroll", toggle, { passive: true });

    btn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" });
    });
  }

  /* 7. Live client-side search box for the doctor list page ----------------*/
  function initDoctorSearch() {
    const heading = Array.from(document.querySelectorAll("h2")).find((h) =>
      /our doctors/i.test(h.textContent)
    );
    const grid = document.querySelector(".row.g-4");
    if (!heading || !grid) return;

    const cards = Array.from(grid.querySelectorAll(":scope > [class*='col-']"));
    if (!cards.length) return;

    const wrap = document.createElement("div");
    wrap.className = "doctor-search-wrap mb-4";
    wrap.innerHTML =
      '<input type="search" class="form-control doctor-search-input" ' +
      'placeholder="🔍 Search by doctor name or specialization…" aria-label="Search doctors">' +
      '<div class="doctor-search-empty d-none alert alert-info text-center mt-3">' +
      "No doctors match your search.</div>";
    heading.insertAdjacentElement("afterend", wrap);

    const input = wrap.querySelector(".doctor-search-input");
    const emptyState = wrap.querySelector(".doctor-search-empty");

    input.addEventListener("input", () => {
      const term = input.value.trim().toLowerCase();
      let visibleCount = 0;

      cards.forEach((card) => {
        const text = card.textContent.toLowerCase();
        const match = term === "" || text.includes(term);
        card.style.display = match ? "" : "none";
        if (match) visibleCount += 1;
      });

      emptyState.classList.toggle("d-none", visibleCount !== 0);
    });
  }
})();