# Wireframe & Layout Plan — "Yuva" Landing Page

Design pass: layout first, code second. The sketches below are the low-fidelity
wireframes I drew before writing any markup. Every box in the code traces back
to a box here.

---

## 1. Concept

**Yuva** — a learning & career accelerator for young people (the name means
"youth"). A single-page marketing site is the classic landing-page brief, so the
section inventory is the standard one: header/nav, hero, feature highlights,
how-it-works, social proof, call-to-action, footer.

---

## 2. Desktop wireframe (≥ 1024px)

```
┌────────────────────────────────────────────────────────────────────────┐
│ HEADER (sticky, translucent on scroll)                                │
│  [ logo ]          Features  How it works  Stories  FAQ     [Join free]│
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  HERO  (2-col grid: copy | visual)                                     │
│  ┌───────────────────────────────┬──────────────────────────────┐      │
│  │ eyebrow pill                  │                              │      │
│  │ H1 headline (3 lines max)     │      illustration /          │      │
│  │ supporting paragraph          │      product mock card       │      │
│  │ [ primary CTA ] [ ghost CTA ] │      + floating stat chips   │      │
│  │ trust row: avatars + rating   │                              │      │
│  └───────────────────────────────┴──────────────────────────────┘      │
│  (subtle gradient blobs behind, decorative only)                       │
├────────────────────────────────────────────────────────────────────────┤
│  LOGO / PARTNER STRIP  (marquee-ish row, wraps on small screens)       │
├────────────────────────────────────────────────────────────────────────┤
│  FEATURES                                                              │
│  section header (centered, narrow measure)                             │
│  ┌──────────┬──────────┬──────────┐   ← 3 columns, Grid                │
│  │  icon    │  icon    │  icon    │                                     │
│  │  title   │  title   │  title   │   (row 2 identical)                │
│  │  text    │  text    │  text    │                                     │
│  └──────────┴──────────┴──────────┘                                     │
├────────────────────────────────────────────────────────────────────────┤
│  HOW IT WORKS   (alternating 2-col steps / numbered rail)              │
│      01 ──────────────  02 ──────────────  03 ──────────────            │
├────────────────────────────────────────────────────────────────────────┤
│  STATS BAND  (dark full-bleed, 4 equal columns)                        │
├────────────────────────────────────────────────────────────────────────┤
│  TESTIMONIALS  (3 cards, Grid; horizontal snap-scroll on mobile)       │
├────────────────────────────────────────────────────────────────────────┤
│  CTA PANEL  (centred, single column, email capture form)               │
├────────────────────────────────────────────────────────────────────────┤
│  FOOTER                                                                  │
│  ┌────────────┬──────────┬──────────┬──────────┐                        │
│  │ brand +    │ Product  │ Company  │ Resources│                        │
│  │ blurb      │ links    │ links    │ links    │                        │
│  └────────────┴──────────┴──────────┴──────────┘                        │
│  ────────────────────────────────────────────────                       │
│  copyright · social icons · legal links                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Mobile wireframe (< 768px)

```
┌──────────────────────────────┐
│ [ logo ]            [ ☰ ]    │  ← hamburger toggles a dropdown panel
├──────────────────────────────┤
│  HERO — single column        │
│  eyebrow                     │
│  H1                          │
│  paragraph                   │
│  [ primary CTA ]             │
│  [ ghost CTA  ]              │
│  trust row                   │
│  visual below the copy       │
├──────────────────────────────┤
│  partner strip (wraps)       │
├──────────────────────────────┤
│  FEATURES — 1 column         │
│  ┌────────────────────────┐  │
│  │ card                   │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │  ← cards stack, full width
│  │ card                   │  │
│  └────────────────────────┘  │
├──────────────────────────────┤
│  HOW IT WORKS — stacked,     │
│  numbered rail on the left   │
├──────────────────────────────┤
│  STATS — 2 × 2 grid          │
├──────────────────────────────┤
│  TESTIMONIALS — swipeable    │
│  snap carousel (no JS)       │
├──────────────────────────────┤
│  CTA PANEL                   │
├──────────────────────────────┤
│  FOOTER — accordion-style    │
│  stacked columns             │
└──────────────────────────────┘
```

---

## 4. Breakpoint strategy (mobile-first)

| Token        | Width  | Purpose                                                    |
| ------------ | ------ | ---------------------------------------------------------- |
| (base)       | 0+     | Single column, stacked nav panel, 1-up cards               |
| `sm`         | 480px  | Larger type scale, 2-up where it helps                     |
| `md`         | 768px  | Nav links appear inline (hamburger hides), 2-col grids     |
| `lg`         | 1024px | Hero 2-col split, 3-col feature grid, full footer 4-col    |
| `xl`         | 1280px | Wider container + looser vertical rhythm                   |

Content max-width: `72rem` (1152px) container, `65ch` measure for prose.

---

## 5. Interaction inventory (vanilla JS)

1. **Hamburger toggle** — `aria-expanded` / `aria-controls`, closes on link click,
   on `Esc`, and on `resize` back to desktop.
2. **Sticky-header state** — adds `.is-scrolled` past 8px for shadow + blur.
3. **Active section highlighting** — `IntersectionObserver` marks the nav link of
   the section currently in view.
4. **Reveal-on-scroll** — `IntersectionObserver` adds `.is-visible` for subtle
   fade/rise; disabled under `prefers-reduced-motion`.
5. **Newsletter form** — client-side email validation + inline status message
   (`aria-live`), no page reload.
6. **Footer year** — auto-updated so the footer never goes stale.

Everything degrades: with JS off the nav is still visible (CSS-only fallback
shows the panel), content is fully readable, and the form simply posts nowhere.
