import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from services.insight_processor import (
    detect_platform, normalize_space, extract_number_tokens, 
    PLATFORM_KEYWORDS, VISIBLE_TAGS, INVALID_SIGNALS,
    generic_html_signals, dedupe_signals, build_best_guess
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}

async def validate_rendered_page(url: str, page):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2.5)
        await page.mouse.wheel(0, 1000)
        await asyncio.sleep(1.2)

        final_url = page.url
        html = await page.content()
        html_l = html.lower()

        valid = not any(sig in html_l for sig in INVALID_SIGNALS)

        return {
            "valid": valid,
            "reason": "ok" if valid else "invalid_signal_in_rendered_html",
            "final_url": final_url,
            "html": html,
        }
    except PlaywrightTimeoutError:
        return {"valid": False, "reason": "timeout", "final_url": None, "html": None}
    except Exception as e:
        return {
            "valid": False,
            "reason": f"exception: {type(e).__name__}: {e}",
            "final_url": None,
            "html": None,
        }

async def platform_specific_signals(page, platform: str):
    signals = []
    selector_map = {
        "instagram": ["header span", "main header section span", "main span", "header a span"],
        "threads": ["main span", "main a span", "header span"],
        "tiktok": ["main strong", "main h3", "main span", "[data-e2e] span"],
        "youtube": ["#subscriber-count", "yt-formatted-string#subscriber-count", "yt-formatted-string"],
        "x": ["main a[href*='verified_followers'] span", "main section span", "main div span"],
        "twitter": ["main a[href*='verified_followers'] span", "main section span", "main div span"],
        "facebook": ["main span", "main a span", "div[role='main'] span"],
        "generic": ["span", "a", "div"],
    }

    selectors = selector_map.get(platform, selector_map["generic"])
    keywords = PLATFORM_KEYWORDS["generic"] + PLATFORM_KEYWORDS.get(platform, [])
    seen = set()

    for selector in selectors:
        try:
            loc = page.locator(selector)
            count = min(await loc.count(), 200)
            for i in range(count):
                el = loc.nth(i)
                try:
                    text = normalize_space(await el.inner_text(timeout=1000))
                    if not text: continue
                    matched = [kw for kw in keywords if kw.lower() in text.lower()]
                    if not matched: continue

                    outer_html = await el.evaluate("node => node.outerHTML")
                    number_tokens = extract_number_tokens(text + " " + outer_html)
                    if not number_tokens: continue

                    key = (text, outer_html[:200])
                    if key in seen: continue
                    seen.add(key)

                    signals.append({
                        "source": "platform_selector",
                        "selector": selector,
                        "text": text,
                        "matched_keywords": sorted(set(matched)),
                        "number_tokens": number_tokens,
                        "outer_html": outer_html,
                    })
                except Exception:
                    continue
        except Exception:
            continue
    return signals

async def process_profile(profile, browser):
    url = profile["url"]
    platform = detect_platform(url)

    context = await browser.new_context(
        user_agent=HEADERS["User-Agent"],
        locale="en-US",
        extra_http_headers={"Accept-Language": HEADERS["Accept-Language"]},
    )
    page = await context.new_page()

    try:
        validate_meta = await validate_rendered_page(url, page)
        result = {
            **profile,
            "platform_detected": platform,
            "valid": validate_meta["valid"],
            "validate_meta": {
                "reason": validate_meta["reason"],
                "final_url": validate_meta["final_url"],
            },
            "best_guess": {},
        }

        if not validate_meta["valid"] or not validate_meta["html"]:
            return result

        selector_signals = await platform_specific_signals(page, platform)
        generic_sigs, _ = generic_html_signals(validate_meta["html"], platform)
        
        all_signals = dedupe_signals(selector_signals + generic_sigs)
        result["best_guess"] = build_best_guess(all_signals)
        
        # Flatten for frontend compatibility if needed
        if "followers" in result["best_guess"]:
            result["followers"] = result["best_guess"]["followers"]["value"]
        else:
            result["followers"] = 0

        return result
    finally:
        await page.close()
        await context.close()

async def process_full_insight(profiles: list):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            tasks = []
            for profile in profiles:
                if not profile or not isinstance(profile, dict):
                    continue
                tasks.append(process_profile(profile, browser))
            results = await asyncio.gather(*tasks)
            return results
        finally:
            await browser.close()
