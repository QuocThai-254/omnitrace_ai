from google import genai
import json
from google.genai import types
import re
from google import genai
import json


def get_gemini_client(api_key: str):
    return genai.Client(api_key=api_key)


def suggest_usernames(query: str, api_key: str):
    if api_key == "test":
        return {
            "status": "success",
            "data": [
                {
                    "platform": "Facebook",
                    "username": "Sơn Tùng M-TP",
                    "url": "https://www.facebook.com/MTP.Fan",
                },
                {
                    "platform": "Instagram",
                    "username": "sontungmtp",
                    "url": "https://www.instagram.com/sontungmtp",
                },
                {
                    "platform": "X (Twitter)",
                    "username": "sontungmtp",
                    "url": "https://twitter.com/sontungmtp777",
                },
                {
                    "platform": "Threads",
                    "username": "sontungmtp",
                    "url": "https://www.threads.net/@sontungmtp",
                },
                {
                    "platform": "Youtube",
                    "username": "sontungmtp",
                    "url": "https://www.youtube.com/c/sontungmtp",
                },
            ],
            "references": [
                {
                    "title": "Search Query: Sơn Tùng M-TP Facebook chính thức",
                    "url": "https://www.google.com/search?q=Sơn+Tùng+M-TP+Facebook+chính+thức",
                },
                {
                    "title": "Search Query: Sơn Tùng M-TP Instagram chính thức",
                    "url": "https://www.google.com/search?q=Sơn+Tùng+M-TP+Instagram+chính+thức",
                },
                {
                    "title": "Search Query: Sơn Tùng M-TP X (Twitter) chính thức",
                    "url": "https://www.google.com/search?q=Sơn+Tùng+M-TP+X+(Twitter)+chính+thức",
                },
                {
                    "title": "Search Query: Sơn Tùng M-TP LinkedIn chính thức",
                    "url": "https://www.google.com/search?q=Sơn+Tùng+M-TP+LinkedIn+chính+thức",
                },
            ],
        }

    prompt = f"Given the identity '{query}', suggest 5 possible social handles. Return ONLY a JSON list of strings."
    try:
        client = get_gemini_client(api_key)
        response = client.models.generate_content(
            model="gemini-1.5-pro", contents=prompt
        )
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception:
        return [query.lower().replace(" ", "")]


def clean_json_text(text: str):
    """Bóc tách JSON từ Markdown của AI"""
    match = re.search(r"```json\s+(.*?)\s+```", text, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r"```\s+(.*?)\s+```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def search_social_identity(query: str, api_key: str):
    client = genai.Client(api_key=api_key)

    # 1. Cấu hình công cụ Search
    grounding_tool = types.Tool(google_search=types.GoogleSearch())

    # 2. Cấu hình: Rất quan trọng để lấy Metadata
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        temperature=0.0,
        system_instruction=(
            "Bạn là một thám tử số. Hãy sử dụng công cụ tìm kiếm Google để tìm link mạng xã hội. "
            "Sau khi tìm xong, hãy tổng hợp kết quả thành file JSON. "
            "Bắt buộc phải dựa trên kết quả tìm kiếm thực tế."
        ),
    )

    # Prompt thay đổi: Yêu cầu AI "sử dụng kết quả tìm kiếm"
    prompt = f"""
    Sử dụng Google Search để tìm URL chính thức của '{query}' trên mạng xã hội Facebook, Instagram, X (Twitter), LinkedIn, Threads.
    Viết câu query đầy đủ chi tiết
    Dựa trên các kết quả tìm thấy, hãy trả về danh sách JSON:
    [
      {{"platform": "tên nền tảng", "username": "username", "url": "link trực tiếp"}}
    ]
    Nếu không thấy link nào, hãy bỏ qua nền tảng đó.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=config,
        )

        # 3. Lấy dữ liệu từ candidate đầu tiên
        candidate = response.candidates[0]
        raw_text = response.text
        social_links = []

        try:
            social_links = json.loads(clean_json_text(raw_text))
        except:
            social_links = []

        # 4. Bóc tách Metadata (Sử dụng đúng snake_case của Python SDK)
        sources = []
        if candidate.grounding_metadata:
            metadata = candidate.grounding_metadata

            # Cách 1: Lấy từ grounding_chunks (Link trực tiếp Google trích dẫn)
            if metadata.grounding_chunks:
                for chunk in metadata.grounding_chunks:
                    if chunk.web:
                        sources.append(
                            {
                                "title": chunk.web.title,
                                "url": chunk.web.uri,  # SDK dùng .uri chứ không phải .url
                            }
                        )

            # Cách 2: Nếu chunks trống, lấy từ web_search_queries (Các từ khóa AI đã search)
            # Điều này giúp bạn biết AI đã tìm cái gì nếu nó không trả về link dẫn chứng
            elif metadata.web_search_queries:
                for q in metadata.web_search_queries:
                    sources.append(
                        {
                            "title": f"Search Query: {q}",
                            "url": f"https://www.google.com/search?q={q.replace(' ', '+')}",
                        }
                    )

        # Loại bỏ các nguồn trùng lặp
        unique_sources = {s["url"]: s for s in sources}.values()

        return {
            "status": "success",
            "data": social_links,
            "references": list(unique_sources),
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "data": [], "references": []}
