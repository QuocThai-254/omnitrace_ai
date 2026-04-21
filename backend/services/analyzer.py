import json
import time
from core.config import sb_client
from services.identity import get_gemini_client

def analyze_user_behavior(username: str, api_key: str):
    # Simulated posts
    posts = [{"platform": "X", "content": "Learning AI!", "timestamp": time.time()}]

    prompt = f"Analyze behavior for user '{username}' based on posts: {json.dumps(posts)}. Provide JSON with keys: sentiment_trend, topic_heatmap, anomalies_crisis, future_prediction."

    client = get_gemini_client(api_key)
    response = client.models.generate_content(
        model="gemini-1.5-pro", contents=prompt
    )
    text = response.text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    analysis = json.loads(text)

    if sb_client:
        sb_client.table("targets").update({"ai_analysis": analysis}).eq(
            "username", username
        ).execute()

    return analysis
