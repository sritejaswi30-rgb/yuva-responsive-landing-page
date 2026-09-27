# Yuva — Responsive Landing Page

A single-page, fully responsive marketing landing page built for the
"design & develop a responsive landing page from a wireframe" task.
No frameworks, no build step, no dependencies — open it and it works.

**Stack:** semantic HTML5 · modern CSS3 (Grid, Flexbox, `clamp()`, custom
properties, media queries) · vanilla JavaScript.

---

## Run it

Serving over HTTP (recommended — avoids any `file://` edge cases):

```bash
python -m http.server 5500 --bind 127.0.0.1
# alternative: npx serve -l 5500 .
```

Then open <http://localhost:5500/>.

> Port **5500** is used on purpose: **8000 is already taken** by another local
> service on this machine. If 5500 is busy, pick any free port
> (`python -m http.server 5501`) — the page has no port-specific code.
> Double-clicking `index.html` also works, without a server.

---

## File map

```
index.html              Semantic markup for every section + <head> failsafe
css/styles.css          10 numbered blocks: tokens → base → components → sections
                        → motion → breakpoints → print
js/main.js              6 documented modules (nav, header, observers, form, year)
wireframe.md            Desktop + mobile wireframes, breakpoint plan,
                        interaction inventory
report/
  Yuva_Responsive_Landing_Page_Report.docx   Full report (10 sections, tables)
  report-description.txt                    300-word submission description
screenshots/          Visual proof: desktop + mobile captures of the live page
tests/
  test_page.py        Playwright smoke test (36 assertions, see below)
  make_screenshots.py Regenerates everything in screenshots/
```

---

## Page sections

Header (sticky) → hero → partner strip → feature highlights (6 cards) →
how-it-works (3 steps) → stats band → testimonials → FAQ → newsletter CTA →
footer.

---

## Breakpoints (mobile-first, `min-width` only)

| Width | What changes |
|-------|--------------|
| base  | Single column, hamburger + dropdown nav panel, 1-up cards, scroll-snap testimonial track |
| 480px | Wider gutters, newsletter form becomes one inline row |
| 768px | Nav renders inline (hamburger hidden), stats 4-up, footer 3 columns |
| 1024px | Hero splits into 2 columns, steps become a horizontal rail, testimonials 3-up |
| 1280px | Wider gutter, footer reaches its 4-column layout |

Content caps at a `72rem` (1152px) container; heading sizes are fluid via
`clamp()`, so there are no font-size media queries.

---

## Interactivity (vanilla JS)

1. **Menu toggle** — `aria-expanded` drives both the a11y state and the CSS;
   closes on link click, outside click, `Escape` (focus returns to the
   button), and when the viewport grows past 768px.
2. **Sticky header state** — `.is-scrolled` past 8px adds shadow + hairline
   (rAF-throttled, passive listener).
3. **Active section highlighting** — `IntersectionObserver` with a
   header-adjusted `rootMargin`.
4. **Reveal on scroll** — one observer per element, unobserved after firing;
   testimonial cards inside the horizontal scroller reveal as a group.
5. **Newsletter validation** — inline `aria-live` status, invalid-state
   border cleared on input, no page reload.
6. **Footer year** — auto-updated.

### Progressive enhancement

* The reveal animation is scoped to `html.js`, added by a tiny inline head
  script, so **no JavaScript = fully visible content** (never a blank page).
* That script also starts a 2.5s failsafe timer which `main.js` cancels —
  if the main script ever fails to load, the class drops and the content
  appears un-animated instead of staying hidden.
* The FAQ is native `<details>/<summary>` and the mobile testimonial
  carousel is CSS `scroll-snap`, so both work with JS off.
* `prefers-reduced-motion: reduce` disables smooth scrolling, the float
  animation and every transition.

---

## Accessibility

Skip link, landmark structure (`header/nav/main/section/footer`), one `h1`
with a correct heading outline, visible `:focus-visible` rings, labelled
form controls, `aria-hidden` on decorative artwork, accessible names on
icon-only links, ≥44px touch targets, and text/background contrast above
WCAG AA.

---

## Tests

```bash
pip install playwright
playwright install chromium
python tests/test_page.py
```

Checks 11 viewport widths (360 → 1920) for horizontal overflow and clipped
text, asserts the menu / form / FAQ / scroll behaviours, and exits non-zero on
any failure or console error. Latest run: **36/36 checks passed, 0 console
errors, 0 failed requests.**

---

## Browser support

Anything current: Chromium, Firefox, Safari. Every cutting-edge feature is
guarded — `backdrop-filter` and `background-clip: text` have `@supports`
fallbacks, `IntersectionObserver` and `matchMedia` listeners are feature-
detected, and the layout only uses Flexbox/Grid/`clamp()`/custom properties.
