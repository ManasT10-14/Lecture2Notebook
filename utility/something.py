import os, re
from http.cookiejar import MozillaCookieJar
from playwright.sync_api import sync_playwright
import requests

COURSE_SLUG = "neural-networks-deep-learning"
COURSE_ID = "W_mOXCrdEeeNPQ68_4aPpA"
OUTPUT = "transcripts"
os.makedirs(OUTPUT, exist_ok=True)

# ------------ Load cookies ------------
cj = MozillaCookieJar("cookies.txt")
cj.load()
cookies_dict = {c.name: c.value for c in cj}
print("✔ Cookies loaded")

# ------------ Fetch lectures ------------
s = requests.Session()
s.cookies.update(cookies_dict)

materials_api = (
    f"https://www.coursera.org/api/onDemandCourseMaterials.v2/"
    f"{COURSE_ID}?includes=modules,items"
)
materials = s.get(materials_api).json()
items = materials["linked"]["onDemandCourseMaterialItems.v2"]

lectures = [(it["id"], it["slug"]) for it in items if "slug" in it]
print(f"✔ Found {len(lectures)} lectures")

# ------------ Playwright automation ------------
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,             # 👈 FULL BACKGROUND MODE
        args=[
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ]
    )

    ctx = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        java_script_enabled=True
    )

    # SPEED BOOST
    ctx.route("**/*", lambda route: (
        route.abort() if (
            route.request.resource_type in ["media", "font", "image"]
            or route.request.url.endswith(".mp4")
            or route.request.url.endswith(".m3u8")
        ) else route.continue_()
    ))

    ctx.add_cookies([
        {"name": c.name, "value": c.value, "domain": ".coursera.org", "path": "/"}
        for c in cj
    ])

    page = ctx.new_page()
    saved = 0

    for idx, (lec_id, slug) in enumerate(lectures, start=1):
        url = f"https://www.coursera.org/learn/{COURSE_SLUG}/lecture/{lec_id}/{slug}"
        print(f"\n🎥 ({idx}/{len(lectures)}) Opening: {slug}")
        page.goto(url, wait_until="domcontentloaded")

        if "login" in page.url.lower():
            print("❌ Cookies expired — refresh cookies.txt")
            break

        # ---- Transcript Tab ----
        try:
            page.get_by_role("tab", name=re.compile("Transcript", re.I)).click(timeout=6000)
        except:
            print("⚠️ No Transcript tab → skip fast")
            continue

        page.wait_for_timeout(300)

        try:
            page.wait_for_selector(
                "div[role='tabpanel'][id*='panel-transcript']",
                timeout=6000
            )
        except:
            print("⚠️ No transcript panel → skip fast")
            continue

        timestamps = page.eval_on_selector_all(
            "div[role='tabpanel'][id*='panel-transcript'] button.timestamp",
            "els => els.map(e => e.innerText)"
        )

        phrases = page.eval_on_selector_all(
            "div[role='tabpanel'][id*='panel-transcript'] .rc-Phrase span.css-4s48ix",
            "els => els.map(e => e.innerText)"
        )

        if not phrases:
            print("⚠️ Empty transcript → skip")
            continue

        lines = []
        if len(timestamps) == len(phrases):
            for t, p in zip(timestamps, phrases):
                if p.strip():
                    lines.append(f"{t}  {p.strip()}")
        else:
            for p in phrases:
                if p.strip():
                    lines.append(p.strip())

        text = "\n".join(lines).strip()
        if not text:
            print("⚠️ No text → skip")
            continue

        safe = slug.replace("/", "-")
        path = os.path.join(OUTPUT, f"{idx:02d}-{safe}.txt")

        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

        print("✔ Saved →", path)
        saved += 1

    browser.close()

print(f"\n🎉 Done! Saved {saved} transcripts.")
