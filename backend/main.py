from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from core.config import sb_client
from core.security import verify_password
from services.identity import suggest_usernames, search_social_identity
from services.scanner import get_cached_scan, save_scan_results, perform_scan
from services.analyzer import analyze_user_behavior
from chat.processor import get_initial_greeting, process_chat_message
from services.insight_engine import process_full_insight

app = FastAPI(title="OmniTrace AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "OmniTrace AI API is running"}


@app.post("/login")
async def login(
    username: str = Body(..., embed=True), password: str = Body(..., embed=True)
):
    if not sb_client:
        raise HTTPException(status_code=500, detail="Database not configured")
    res = sb_client.table("users").select("*").eq("username", username).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    user = res.data[0]
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "user": {"username": username}}


@app.post("/search-identity")
async def search_identity(
    query: str = Body(..., embed=True), api_key: str = Body(None, embed=True)
):
    if api_key == "test":
        result = suggest_usernames(query, api_key)
    else:
        result = search_social_identity(query, api_key)
    return {"query": query, "suggested_usernames": result}


@app.post("/infer-insight")
async def infer_insight(profiles: list = Body(..., embed=True)):
    # profiles: list of {"platform": ..., "url": ...}
    results = await process_full_insight(profiles)
    return {"results": results}


@app.post("/chat-message")
async def chat_message(
    message: str = Body(..., embed=True), api_key: str = Body(..., embed=True)
):
    response = process_chat_message(message, api_key)
    return {"response": response}


@app.post("/scan-username")
async def scan_username(username: str = Body(..., embed=True)):
    cached = get_cached_scan(username)
    if cached:
        return {"username": username, "results": cached, "cached": True}
    results = perform_scan(username)
    save_scan_results(username, results)
    return {"username": username, "results": results, "cached": False}


@app.post("/analyze-behavior")
async def analyze_behavior(
    username: str = Body(..., embed=True), api_key: str = Body(..., embed=True)
):
    try:
        analysis = analyze_user_behavior(username, api_key)
        return {"username": username, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat-init")
async def chat_init(
    model_id: str = Body(..., embed=True), api_key: str = Body(..., embed=True)
):
    try:
        message = get_initial_greeting(model_id, api_key)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
