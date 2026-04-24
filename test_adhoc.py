import re
import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup, FeatureNotFound
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}

PLATFORM_KEYWORDS = {
    "generic": [
        "followers",
        "follower",
        "following",
        "subscribers",
        "subscriber",
        "likes",
        "fans",
        "posts",
        "post",
        "videos",
        "video",
        "replies",
        "người theo dõi",
        "đang theo dõi",
        "người đăng ký",
        "lượt thích",
        "bài viết",
        "フォロワー",
        "팔로워",
        "粉丝",
    ],
    "instagram": [
        "followers",
        "following",
        "posts",
        "người theo dõi",
        "đang theo dõi",
        "bài viết",
    ],
    "facebook": ["followers", "likes", "fans", "người theo dõi", "lượt thích"],
    "tiktok": [
        "followers",
        "following",
        "likes",
        "fans",
        "người theo dõi",
        "đang theo dõi",
        "lượt thích",
    ],
    "threads": ["followers", "following", "replies", "người theo dõi", "đang theo dõi"],
    "x": ["followers", "following", "người theo dõi", "đang theo dõi"],
    "twitter": ["followers", "following", "người theo dõi", "đang theo dõi"],
    "youtube": ["subscribers", "subscriber", "videos", "video", "người đăng ký"],
}

VISIBLE_TAGS = {
    "span",
    "a",
    "div",
    "li",
    "button",
    "section",
    "h1",
    "h2",
    "h3",
    "h4",
    "p",
    "strong",
    "small",
    "yt-formatted-string",
}

SKIP_TAGS = {"script", "style", "noscript", "svg", "path", "meta", "link", "iframe"}

INVALID_SIGNALS = [
    "page isn't available",
    "sorry, this page",
    "the link you followed may be broken",
    "this page isn’t available",
    "not found",
    "page not found",
]

NUMBER_TOKEN_PATTERN = re.compile(
    r"(?:\d{1,3}(?:[,\.\s]\d{3})+|\d+(?:\.\d+)?[kKmMbB]|\d+(?:\.\d+)?)"
)


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "instagram.com" in host:
        return "instagram"
    if "facebook.com" in host or "fb.com" in host:
        return "facebook"
    if "tiktok.com" in host:
        return "tiktok"
    if "threads.net" in host:
        return "threads"
    if "twitter.com" in host:
        return "twitter"
    if "x.com" in host:
        return "x"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    return "generic"


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_number_tokens(text: str):
    return NUMBER_TOKEN_PATTERN.findall(text or "")


def make_soup(html: str):
    for parser in ("lxml", "html5lib", "html.parser"):
        try:
            return BeautifulSoup(html, parser), parser
        except FeatureNotFound:
            continue
    raise RuntimeError("No HTML parser available")


def text_has_keywords(text: str, keywords):
    text_l = text.lower()
    return [kw for kw in keywords if kw.lower() in text_l]


def parse_compact_number(token: str):
    if not token:
        return None
    t = token.strip().replace(",", "").replace(" ", "")
    try:
        if re.fullmatch(r"\d+(\.\d+)?[kK]", t):
            return int(float(t[:-1]) * 1_000)
        if re.fullmatch(r"\d+(\.\d+)?[mM]", t):
            return int(float(t[:-1]) * 1_000_000)
        if re.fullmatch(r"\d+(\.\d+)?[bB]", t):
            return int(float(t[:-1]) * 1_000_000_000)
        if re.fullmatch(r"\d+(\.\d+)?", t):
            return int(float(t))
        return None
    except Exception:
        return None


def validate_rendered_page(url: str, page):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(1200)

        final_url = page.url
        html = page.content()
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


def platform_specific_signals(page, platform: str):
    signals = []

    selector_map = {
        "instagram": [
            "header span",
            "main header section span",
            "main span",
            "header a span",
        ],
        "threads": [
            "main span",
            "main a span",
            "header span",
        ],
        "tiktok": [
            "main strong",
            "main h3",
            "main span",
            "[data-e2e] span",
        ],
        "youtube": [
            "#subscriber-count",
            "yt-formatted-string#subscriber-count",
            "yt-formatted-string",
        ],
        "x": [
            "main a[href*='verified_followers'] span",
            "main section span",
            "main div span",
        ],
        "twitter": [
            "main a[href*='verified_followers'] span",
            "main section span",
            "main div span",
        ],
        "facebook": [
            "main span",
            "main a span",
            "div[role='main'] span",
        ],
        "generic": ["span", "a", "div"],
    }

    selectors = selector_map.get(platform, selector_map["generic"])
    keywords = PLATFORM_KEYWORDS["generic"] + PLATFORM_KEYWORDS.get(platform, [])
    seen = set()

    for selector in selectors:
        try:
            loc = page.locator(selector)
            count = min(loc.count(), 200)
            for i in range(count):
                el = loc.nth(i)
                try:
                    text = normalize_space(el.inner_text(timeout=1000))
                    if not text:
                        continue
                    matched = text_has_keywords(text, keywords)
                    if not matched:
                        continue

                    outer_html = el.evaluate("node => node.outerHTML")
                    number_tokens = extract_number_tokens(text + " " + outer_html)
                    if not number_tokens:
                        continue

                    key = (text, outer_html[:200])
                    if key in seen:
                        continue
                    seen.add(key)

                    signals.append(
                        {
                            "source": "platform_selector",
                            "selector": selector,
                            "text": text,
                            "matched_keywords": sorted(set(matched)),
                            "number_tokens": number_tokens,
                            "outer_html": outer_html,
                        }
                    )
                except Exception:
                    continue
        except Exception:
            continue

    return signals


def generic_html_signals(rendered_html: str, platform: str):
    soup, parser_used = make_soup(rendered_html)

    for t in soup.find_all(SKIP_TAGS):
        t.decompose()

    keywords = PLATFORM_KEYWORDS["generic"] + PLATFORM_KEYWORDS.get(platform, [])
    candidates = []
    seen = set()

    for tag in soup.find_all(True):
        if tag.name not in VISIBLE_TAGS:
            continue

        text = normalize_space(tag.get_text(" ", strip=True))
        if not text:
            continue
        if len(text) > 160:
            continue

        matched = text_has_keywords(text, keywords)
        if not matched:
            continue

        attrs_join = " ".join(
            [
                str(tag.get("title") or ""),
                str(tag.get("aria-label") or ""),
                str(tag.get("href") or ""),
            ]
        )
        number_tokens = extract_number_tokens(text + " " + attrs_join)
        if not number_tokens:
            continue

        outer_html = str(tag)
        key = (tag.name, text, outer_html[:250])
        if key in seen:
            continue
        seen.add(key)

        candidates.append(
            {
                "source": "generic_html",
                "tag": tag.name,
                "text": text,
                "matched_keywords": sorted(set(matched)),
                "number_tokens": number_tokens,
                "attrs": {
                    "class": tag.get("class"),
                    "id": tag.get("id"),
                    "title": tag.get("title"),
                    "aria-label": tag.get("aria-label"),
                    "href": tag.get("href"),
                },
                "outer_html": outer_html,
            }
        )

    return candidates, parser_used


def classify_signal(signal):
    text_l = signal["text"].lower()

    if (
        "followers" in text_l
        or "người theo dõi" in text_l
        or "粉丝" in text_l
        or "フォロワー" in text_l
    ):
        return "followers"
    if "following" in text_l or "đang theo dõi" in text_l:
        return "following"
    if "subscribers" in text_l or "subscriber" in text_l or "người đăng ký" in text_l:
        return "subscribers"
    if "posts" in text_l or "post" in text_l or "bài viết" in text_l:
        return "posts"
    if "likes" in text_l or "fans" in text_l or "lượt thích" in text_l:
        return "likes"
    if "videos" in text_l or "video" in text_l:
        return "videos"
    if "replies" in text_l:
        return "replies"
    return "unknown"


def build_best_guess(signals):
    result = {}
    for sig in signals:
        label = classify_signal(sig)
        if label == "unknown":
            continue

        parsed_values = [parse_compact_number(x) for x in sig.get("number_tokens", [])]
        parsed_values = [x for x in parsed_values if x is not None]
        if not parsed_values:
            continue

        # ưu tiên số lớn nhất vì outer_html có thể chứa cả 8.3M lẫn 8,336,905
        value = max(parsed_values)
        if label not in result:
            result[label] = {
                "value": value,
                "from_text": sig["text"],
                "source": sig["source"],
            }
    return result


def dedupe_signals(signals):
    out = []
    seen = set()
    for sig in signals:
        key = (
            sig.get("text"),
            sig.get("outer_html", "")[:220],
            tuple(sig.get("matched_keywords", [])),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(sig)
    return out


def process_profile(profile, browser):
    url = profile["url"]
    platform = detect_platform(url)

    context = browser.new_context(
        user_agent=HEADERS["User-Agent"],
        locale="en-US",
        extra_http_headers={"Accept-Language": HEADERS["Accept-Language"]},
    )
    page = context.new_page()

    try:
        validate_meta = validate_rendered_page(url, page)

        result = {
            **profile,
            "platform_detected": platform,
            "valid": validate_meta["valid"],
            "validate_meta": {
                "reason": validate_meta["reason"],
                "final_url": validate_meta["final_url"],
            },
            "parser_used": None,
            "signals": [],
            "signal_count": 0,
            "best_guess": {},
        }

        if not validate_meta["valid"] or not validate_meta["html"]:
            return result

        selector_signals = platform_specific_signals(page, platform)
        generic_signals, parser_used = generic_html_signals(
            validate_meta["html"], platform
        )
        result["parser_used"] = parser_used

        all_signals = dedupe_signals(selector_signals + generic_signals)

        # rank: selector-specific đứng trước
        all_signals.sort(
            key=lambda s: (
                0 if s["source"] == "platform_selector" else 1,
                len(s.get("text", "")),
            )
        )

        result["signals"] = all_signals
        result["signal_count"] = len(all_signals)
        result["best_guess"] = build_best_guess(all_signals)
        return result

    finally:
        page.close()
        context.close()


def run_pipeline(data: dict):
    profiles = data.get("suggested_usernames", {}).get("data", [])
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            for profile in profiles:
                results.append(process_profile(profile, browser))
        finally:
            browser.close()

    return {
        "query": data.get("query"),
        "results": results,
    }


if __name__ == "__main__":
    input_data = {
        "query": "son tung",
        "suggested_usernames": {
            "data": [
                {
                    "platform": "Instagram",
                    "username": "sontungmtp",
                    "url": "https://www.instagram.com/sontungmtp",
                },
                {
                    "platform": "Threads",
                    "username": "sontungmtp",
                    "url": "https://www.threads.net/@sontungmtp",
                },
                {
                    "platform": "X (Twitter)",
                    "username": "sontungmtp",
                    "url": "https://twitter.com/sontungmtp777",
                },
                {
                    "platform": "Youtube",
                    "username": "sontungmtp",
                    "url": "https://www.youtube.com/c/sontungmtp",
                },
                {
                    "platform": "TikTok",
                    "username": "sontungmtp",
                    "url": "https://www.tiktok.com/@sontungmtp",
                },
                {
                    "platform": "Facebook",
                    "username": "Sơn Tùng M-TP",
                    "url": "https://www.facebook.com/MTP.Fan",
                },
            ]
        },
    }

    output = run_pipeline(input_data)
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    # print(json.dumps(output, indent=2, ensure_ascii=False))
