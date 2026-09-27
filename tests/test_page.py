"""Responsive / interaction smoke test for the Yuva landing page.

Run:  pip install playwright && playwright install chromium
      python tests/test_page.py

Runs the real page in headless Chromium at several viewport widths and
reports: horizontal overflow, JS console errors, failed requests, the
mobile menu behaviour, and the newsletter form validation.
Also writes screenshots for visual review into shots/.
"""
import os, sys, json
from playwright.sync_api import sync_playwright

# tests/ lives one level below the site root, so index.html is in the parent.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file:///' + os.path.join(ROOT, 'index.html').replace('\\', '/')
SHOTS = os.path.join(ROOT, 'shots')
os.makedirs(SHOTS, exist_ok=True)

WIDTHS = [360, 390, 414, 480, 640, 768, 834, 1024, 1280, 1440, 1920]

results, errors = [], []

with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---------- 1. layout / overflow sweep ----------
    for w in WIDTHS:
        page = browser.new_page(viewport={'width': w, 'height': 900})
        console, failed = [], []
        page.on('console', lambda m: console.append(m.type + ': ' + m.text)
                if m.type in ('error', 'warning') else None)
        page.on('requestfailed', lambda r: failed.append(r.url))
        page.goto(URL, wait_until='networkidle')
        page.wait_for_timeout(400)

        info = page.evaluate("""() => {
            const de = document.documentElement;
            const over = [];     // bugs: content escaping the viewport
            const planned = [];  // by design: clipped blobs, peeking carousel
            document.querySelectorAll('body *').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width === 0 || r.height === 0) return;
                if (r.right <= de.clientWidth + 1.5 && r.left >= -1.5) return;
                if (getComputedStyle(el).position === 'fixed') return;
                const cls = el.className.toString().split(' ')[0] || '';
                const label = el.tagName.toLowerCase() + '.' + cls +
                    ' [' + Math.round(r.left) + '..' + Math.round(r.right) + ']';
                // decorative hero blobs are clipped by .hero{overflow:hidden};
                // testimonial cards live in an intentional horizontal scroller
                if (el.classList.contains('hero__blob') || el.closest('.quote-track')) {
                    planned.push(label);
                } else {
                    over.push(label);
                }
            });
            return {
                innerWidth: window.innerWidth,
                scrollWidth: de.scrollWidth,
                overflow: [...new Set(over)].slice(0, 8),
                planned: [...new Set(planned)].length,
                navToggleShown: getComputedStyle(document.querySelector('.nav-toggle')).display !== 'none'
            };
        }""")

        ok = info['scrollWidth'] <= info['innerWidth'] + 1 and not info['overflow']
        results.append({
            'width': w, 'innerWidth': info['innerWidth'],
            'scrollWidth': info['scrollWidth'], 'noOverflow': ok,
            'unexpectedOverflow': info['overflow'],
            'intentionalOverflowIgnored': info['planned'],
            'hamburgerShown': info['navToggleShown'],
        })
        if console: errors.append((w, 'console', console))
        if failed:  errors.append((w, 'requestfailed', failed))

        if w in (390, 768, 1440):
            page.screenshot(path=os.path.join(SHOTS, 'w%s-full.png' % w), full_page=True)
        page.close()

    # ---------- 2. mobile menu behaviour at 390 ----------
    page = browser.new_page(viewport={'width': 390, 'height': 844})
    page.goto(URL, wait_until='networkidle')
    toggle = page.locator('#nav-toggle')
    nav = page.locator('#primary-nav')

    menu = {}
    menu['initial aria-expanded'] = toggle.get_attribute('aria-expanded')
    menu['initial panel visible'] = nav.is_visible()

    toggle.click(); page.wait_for_timeout(350)
    menu['after click aria-expanded'] = toggle.get_attribute('aria-expanded')
    menu['after click panel visible'] = nav.is_visible()
    page.screenshot(path=os.path.join(SHOTS, 'menu-open.png'))

    page.keyboard.press('Escape'); page.wait_for_timeout(350)
    menu['after Escape aria-expanded'] = toggle.get_attribute('aria-expanded')
    menu['after Escape panel visible'] = nav.is_visible()

    toggle.click(); page.wait_for_timeout(300)
    nav.locator('a[href="#features"]').click(); page.wait_for_timeout(600)
    menu['after link click aria-expanded'] = toggle.get_attribute('aria-expanded')
    menu['scrolled to features'] = abs(
        page.evaluate("document.getElementById('features').getBoundingClientRect().top")) < 900
    menu['active nav link'] = page.evaluate(
        "(document.querySelector('.nav__link.is-active')||{}).textContent || none")

    # horizontal overflow after opening the menu
    menu['noOverflow with menu open'] = page.evaluate(
        "document.documentElement.scrollWidth <= window.innerWidth + 1")
    results.append({'menu': menu})
    page.close()

    # ---------- 3. newsletter form ----------
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto(URL, wait_until='networkidle')
    status = page.locator('#signup-status')
    form = {}
    page.locator('#signup-form button').click(); page.wait_for_timeout(150)
    form['empty submit'] = status.text_content()

    page.fill('#signup-email', 'not-an-email')
    page.locator('#signup-form button').click(); page.wait_for_timeout(150)
    form['invalid submit'] = status.text_content()

    page.fill('#signup-email', 'sam@example.com')
    page.locator('#signup-form button').click(); page.wait_for_timeout(150)
    form['valid submit'] = status.text_content()
    form['input cleared'] = page.input_value('#signup-email') == ''
    results.append({'form': form})

    # ---------- 4. FAQ + sticky header + active nav on desktop ----------
    misc = {}
    page.locator('.faq__q').first.click(); page.wait_for_timeout(200)
    misc['faq opens'] = page.locator('.faq__item').first.get_attribute('open') is not None
    page.evaluate("window.scrollTo(0, 600)"); page.wait_for_timeout(400)
    misc['header gets is-scrolled'] = page.evaluate(
        "document.getElementById('site-header').classList.contains('is-scrolled')")
    misc['active link after scroll'] = page.evaluate(
        "(document.querySelector('.nav__link.is-active')||{}).textContent || none")
    misc['footer year'] = page.locator('#year').text_content()
    results.append({'misc': misc})
    page.close()
    browser.close()

print(json.dumps(results, indent=2))
if errors:
    print('\n--- page errors ---')
    for e in errors: print(e)
else:
    print('\nno console errors / failed requests')

# ---------------------------------------------------------------- assertions
layout = [r for r in results if 'width' in r]
menu = next(r['menu'] for r in results if 'menu' in r)
form = next(r['form'] for r in results if 'form' in r)
misc = next(r['misc'] for r in results if 'misc' in r)

checks = []
for r in layout:
    checks.append(('no horizontal overflow @%d' % r['width'], r['noOverflow']))
    checks.append(('hamburger visible @%d' % r['width'],
                   r['hamburgerShown'] == (r['width'] < 768)))
checks += [
    ('menu closed initially', menu['initial aria-expanded'] == 'false'),
    ('menu opens', menu['after click aria-expanded'] == 'true'),
    ('menu closes on Escape', menu['after Escape aria-expanded'] == 'false'),
    ('menu closes on link click', menu['after link click aria-expanded'] == 'false'),
    ('menu scrolls to section', menu['scrolled to features']),
    ('active link highlighted', menu['active nav link'] != 'none'),
    ('form rejects empty', 'enter your email' in form['empty submit']),
    ('form rejects invalid email', 'valid email' in form['invalid submit']),
    ('form accepts valid email', 'on its way' in form['valid submit']),
    ('form clears input', form['input cleared']),
    ('FAQ opens', misc['faq opens']),
    ('sticky header shadow', misc['header gets is-scrolled']),
    ('footer year set', misc['footer year'].isdigit()),
    ('no console/network errors', not errors),
]

print('\n--- results ---')
failed = 0
for name, passed in checks:
    print(('PASS  ' if passed else 'FAIL  ') + name)
    failed += 0 if passed else 1
print('\n%d/%d checks passed' % (len(checks) - failed, len(checks)))
sys.exit(1 if failed else 0)
