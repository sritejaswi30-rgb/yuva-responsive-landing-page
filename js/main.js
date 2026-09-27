/* ============================================================================
   YUVA — FRONT-END INTERACTION LAYER (vanilla JS, no dependencies)
   ----------------------------------------------------------------------------
   Everything here is progressive enhancement: the page is fully readable
   and navigable with this file removed. The script only ADDS behaviour.

   Modules:
     1. Mobile navigation toggle (a11y-first)
     2. Sticky header shadow on scroll
     3. Active section highlighting in the nav
     4. Reveal-on-scroll animations
     5. Newsletter form validation + inline status
     6. Footer year
   ========================================================================== */

/* The script is loaded with `defer`, so the DOM is already parsed when it
   runs. The wrapper below is kept anyway so the file also works if it is
   ever included without defer. */
(function () {
  "use strict";

  /* ------------------------------------------------------------------------
     1. MOBILE NAVIGATION TOGGLE
     Contract: the button owns aria-expanded, the panel owns .is-open.
     Keeping state in BOTH places means the CSS animation, the a11y tree
     and the JS source of truth never drift apart.
     ---------------------------------------------------------------------- */
  const navToggle = document.getElementById("nav-toggle");
  const navPanel = document.getElementById("primary-nav");

  /** isOpen() reads the DOM rather than a closure variable, so a state
      change made outside this module (e.g. by CSS media queries) is
      always reflected correctly. */
  function isOpen() {
    return navToggle.getAttribute("aria-expanded") === "true";
  }

  function setNav(open) {
    navToggle.setAttribute("aria-expanded", String(open));
    navPanel.classList.toggle("is-open", open);
  }

  if (navToggle && navPanel) {
    navToggle.addEventListener("click", function () {
      setNav(!isOpen());
    });

    /* Clicking a nav link should close the panel AND leave the page
       scrolled to the section — otherwise the open panel covers the
       content you just jumped to. */
    navPanel.addEventListener("click", function (event) {
      const link = event.target.closest("a");
      if (link) setNav(false);
    });

    /* Click/tap outside the header dismisses the menu (common mobile
       pattern — cheaper than a focus-trap for a simple link panel). */
    document.addEventListener("click", function (event) {
      if (!isOpen()) return;
      const header = document.getElementById("site-header");
      if (header && !header.contains(event.target)) setNav(false);
    });

    /* Escape closes the menu and returns focus to the toggle, so
       keyboard users are never trapped behind an open panel. */
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && isOpen()) {
        setNav(false);
        navToggle.focus();
      }
    });

    /* If the viewport grows past the breakpoint the nav becomes an
       inline row (CSS). Clear the mobile state so that when the user
       shrinks the window again the menu starts closed. */
    const desktopQuery = window.matchMedia("(min-width: 768px)");
    const handleBreakpoint = function (event) {
      if (event.matches) setNav(false);
    };
    /* addEventListener on matchMedia is the modern API; the fallback
       keeps older Safari working. */
    if (desktopQuery.addEventListener) {
      desktopQuery.addEventListener("change", handleBreakpoint);
    } else if (desktopQuery.addListener) {
      desktopQuery.addListener(handleBreakpoint);
    }
  }

  /* ------------------------------------------------------------------------
     2. STICKY HEADER — add .is-scrolled once the page leaves the top.
     Passive listener so it never blocks scrolling.
     ---------------------------------------------------------------------- */
  const header = document.getElementById("site-header");
  let ticking = false;

  function updateHeader() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 8);
    ticking = false;
  }

  window.addEventListener(
    "scroll",
    function () {
      if (!ticking) {
        window.requestAnimationFrame(updateHeader);
        ticking = true;
      }
    },
    { passive: true }
  );
  updateHeader();

  /* ------------------------------------------------------------------------
     3. ACTIVE SECTION HIGHLIGHTING
     IntersectionObserver watches the sections and marks the matching nav
     link. rootMargin pulls the observation line up by the header height so
     a link activates when its heading is actually under the bar, not when
     the section first appears at the bottom of the viewport.
     ---------------------------------------------------------------------- */
  const navLinks = Array.prototype.slice.call(
    document.querySelectorAll('.nav__link[href^="#"]')
  );

  if ("IntersectionObserver" in window && navLinks.length) {
    // Map "#features" -> <a>, for instant lookup when a section is seen.
    const linkById = {};
    navLinks.forEach(function (link) {
      linkById[link.getAttribute("href").slice(1)] = link;
    });

    const sectionObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          navLinks.forEach(function (l) { l.classList.remove("is-active"); });
          const active = linkById[entry.target.id];
          if (active) active.classList.add("is-active");
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );

    Object.keys(linkById).forEach(function (id) {
      const section = document.getElementById(id);
      if (section) sectionObserver.observe(section);
    });
  }

  /* ------------------------------------------------------------------------
     4. REVEAL ON SCROLL
     One observer for every .reveal element. If the browser lacks
     IntersectionObserver (or the user asked for reduced motion) we just
     show everything immediately — never leave content invisible.

     The testimonial cards live inside a horizontal scroll track: a card
     parked off-screen to the right never intersects the viewport, so
     observing them individually would leave a blank card until the user
     swiped to it. Those cards are revealed as a group as soon as their
     track is on screen instead.
     ---------------------------------------------------------------------- */
  const revealItems = document.querySelectorAll(".reveal");
  const prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  if (!("IntersectionObserver" in window) || prefersReducedMotion) {
    revealItems.forEach(function (el) { el.classList.add("is-visible"); });
  } else {
    const revealObserver = new IntersectionObserver(
      function (entries, observer) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);   // animate once, then stop
          }
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.1 }
    );

    // Cards inside a horizontal track are grouped under their track.
    const grouped = new Set();
    document.querySelectorAll(".quote-track").forEach(function (track) {
      grouped.add(track);
      Array.prototype.forEach.call(
        track.querySelectorAll(".reveal"),
        function (card) { grouped.add(card); }
      );
      // Reveal the whole group together when the track scrolls into view.
      new IntersectionObserver(
        function (entries, observer) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            entry.target.querySelectorAll(".reveal").forEach(function (card) {
              card.classList.add("is-visible");
            });
            observer.unobserve(entry.target);
          });
        },
        { rootMargin: "0px 0px -12% 0px", threshold: 0.1 }
      ).observe(track);
    });

    revealItems.forEach(function (el) {
      if (!grouped.has(el)) revealObserver.observe(el);
    });
  }

  /* ------------------------------------------------------------------------
     5. NEWSLETTER FORM
     novalidate on the <form> lets us own the messaging (the browser bubble
     disappears on blur, which is useless for a11y). We validate ourselves,
     announce the result through an aria-live region, and never actually
     navigate — this is a static demo with no backend.
     ---------------------------------------------------------------------- */
  const form = document.getElementById("signup-form");
  const emailInput = document.getElementById("signup-email");
  const status = document.getElementById("signup-status");

  if (form && emailInput && status) {
    // Deliberately simple and permissive: real deliverability checks need
    // a server. Anything with a local part, an @ and a dotted domain passes.
    const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    function setStatus(message, type) {
      status.textContent = message;
      status.classList.toggle("is-error", type === "error");
      status.classList.toggle("is-success", type === "success");
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();                    // no reload
      const value = emailInput.value.trim();

      if (!value) {
        setStatus("Please enter your email address.", "error");
        emailInput.classList.add("is-invalid");
        emailInput.focus();
        return;
      }

      if (!EMAIL_RE.test(value)) {
        setStatus("That doesn't look like a valid email — check for typos.", "error");
        emailInput.classList.add("is-invalid");
        emailInput.focus();
        return;
      }

      emailInput.classList.remove("is-invalid");
      setStatus("Thanks! The syllabus is on its way to " + value + ".", "success");
      form.reset();
    });

    // Clear the error as soon as the user starts fixing it.
    emailInput.addEventListener("input", function () {
      emailInput.classList.remove("is-invalid");
      if (status.classList.contains("is-error")) setStatus("", null);
    });
  }

  /* ------------------------------------------------------------------------
     6. FOOTER YEAR
     Keeps the copyright line correct without a yearly edit.
     ---------------------------------------------------------------------- */
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  /* ------------------------------------------------------------------------
     7. HANDSHAKE WITH THE INLINE HEAD SCRIPT
     The head script hides .reveal elements optimistically and starts a
     2.5s timer. Confirming here cancels it; if this file failed to load
     the timer runs out and the content is revealed un-animated instead
     of staying invisible.
     ---------------------------------------------------------------------- */
  document.documentElement.classList.add("js-ready");
  if (window.__revealFallback) window.clearTimeout(window.__revealFallback);
})();
