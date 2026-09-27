import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
    if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == 'tests' \
    else os.path.dirname(os.path.abspath(__file__))
URL = 'file:///' + os.path.join(ROOT, 'index.html').replace(os.sep, '/')
OUT = os.path.join(ROOT, 'screenshots')
os.makedirs(OUT, exist_ok=True)

SET_AUTO = 'document.documentElement.style.scrollBehavior = "auto"'


def shoot(pg, name, selector=None, wait=900):
    if selector:
        pg.evaluate(SET_AUTO)
        pg.eval_on_selector(selector, 'e => e.scrollIntoView({block: "start"})')
        pg.wait_for_timeout(wait)
    pg.screenshot(path=os.path.join(OUT, name))


with sync_playwright() as p:
    b = p.chromium.launch()

    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.goto(URL, wait_until='networkidle'); pg.wait_for_timeout(700)
    shoot(pg, 'desktop-1-hero.png')
    shoot(pg, 'desktop-2-features.png', '#features')
    shoot(pg, 'desktop-3-steps.png', '#how-it-works')
    shoot(pg, 'desktop-4-cta.png', '#cta')
    pg.close()

    pg = b.new_page(viewport={'width': 390, 'height': 780})
    pg.goto(URL, wait_until='networkidle'); pg.wait_for_timeout(700)
    shoot(pg, 'mobile-1-hero.png')
    pg.click('#nav-toggle'); pg.wait_for_timeout(450)
    shoot(pg, 'mobile-2-menu-open.png')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(350)
    shoot(pg, 'mobile-3-features.png', '#features')
    pg.close()
    b.close()

print('screenshots written to', OUT)
