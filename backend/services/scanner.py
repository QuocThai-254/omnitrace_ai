import time
from core.config import sb_client

def get_cached_scan(username: str):
    if not sb_client:
        return None
    res = sb_client.table("targets").select("*").eq("username", username).execute()
    if res.data:
        target = res.data[0]
        if time.time() - target.get("last_scanned", 0) < 5184000:
            return target.get("results")
    return None

def save_scan_results(username: str, results: list):
    if sb_client:
        sb_client.table("targets").upsert(
            {"username": username, "results": results, "last_scanned": int(time.time())}
        ).execute()

def perform_scan(username: str):
    # Simulated scan logic
    return [
        {"platform": "X", "url": f"https://x.com/{username}", "status": "active"},
        {
            "platform": "Instagram",
            "url": f"https://instagram.com/{username}",
            "status": "active",
        },
    ]
