from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup, FeatureNotFound

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
    "login",
    "log in",
    "sign in",
    "đăng nhập",
    "accounts/login",
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
    if "twitter.com" in host or "x.com" in host:
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
    # Print input ngay khi nhận
    print(f"Input:  '{token}'")

    if not token:
        print("Output: None")
        return None

    t = token.strip().replace(",", "").replace(" ", "")
    result = None  # Biến tạm để lưu kết quả

    try:
        if re.fullmatch(r"\d+(\.\d+)?[K]", t):
            result = int(float(t[:-1]) * 1_000)
        elif re.fullmatch(r"\d+(\.\d+)?[M]", t):
            result = int(float(t[:-1]) * 1_000_000)
        elif re.fullmatch(r"\d+(\.\d+)?[B]", t):
            result = int(float(t[:-1]) * 1_000_000_000)
        elif re.fullmatch(r"\d+(\.\d+)?", t):
            result = int(float(t))
    except Exception as e:
        print(f"Error: {e}")
        result = None

    # Print output trước khi trả về
    print(f"Output: {result}")
    return result


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
        if not text or len(text) > 160:
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


def normalize_followers(raw_text: str):
    val = parse_compact_number(raw_text)
    return val if val is not None else 0
