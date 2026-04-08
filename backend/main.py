from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Optional, Dict
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore, auth
from supabase import create_client, Client
from dotenv import load_dotenv
import subprocess
import json
import time

load_dotenv()

app = FastAPI(title="OmniTrace AI API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database & Auth Setup (Hybrid Optimization) ---

# Firebase (Authentication or Caching)
try:
    if os.environ.get("FIREBASE_CREDENTIALS"):
        cred_dict = json.loads(os.environ.get("FIREBASE_CREDENTIALS"))
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    fb_db = firestore.client()
except Exception:
    fb_db = None

# Supabase (Primary Database - PostgreSQL for relational data)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role for backend
sb_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL else None

# --- Gemini Config helper ---
def get_gemini_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

# --- Scraper Module ---
class SocialScraper:
    async def get_posts(self, username: str, platforms: list):
        # Simulated data for prototype
        return [
            {"platform": "X", "content": "Learning AI every day!", "timestamp": time.time() - 86400},
            {"platform": "Instagram", "content": "OSINT is fun.", "timestamp": time.time() - 172800}
        ]

scraper = SocialScraper()

@app.get("/")
def read_root():
    return {"message": "OmniTrace AI API Hybrid DB (Firebase + Supabase) is running"}

@app.post("/search-identity")
async def search_identity(query: str = Body(..., embed=True), api_key: str = Body(None, embed=True)):
    """Module 1: Identity Discovery"""
    prompt = f"Given the identity '{query}', suggest 5 possible social handles. Return ONLY a JSON list of strings."
    try:
        model = get_gemini_model(api_key)
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        usernames = json.loads(text)
        return {"query": query, "suggested_usernames": usernames}
    except Exception:
        return {"query": query, "suggested_usernames": [query.lower().replace(" ", "")]}

@app.post("/scan-username")
async def scan_username(username: str = Body(..., embed=True)):
    """Module 2: Sherlock & Supabase Logic"""
    if sb_client:
        # Check cache in Supabase (Optimized query)
        res = sb_client.table("targets").select("*").eq("username", username).execute()
        if res.data:
            target = res.data[0]
            # Check 60-day cache
            if time.time() - target.get('last_scanned', 0) < 5184000:
                return {"username": username, "results": target.get('results'), "cached": True}

    # Sherlock simulation (Real call would use subprocess)
    results = [
        {"platform": "X", "url": f"https://x.com/{username}", "status": "active"},
        {"platform": "Instagram", "url": f"https://instagram.com/{username}", "status": "active"},
    ]
    
    if sb_client:
        # Save to Supabase
        sb_client.table("targets").upsert({
            "username": username,
            "results": results,
            "last_scanned": int(time.time())
        }).execute()

    return {"username": username, "results": results, "cached": False}

@app.post("/analyze-behavior")
async def analyze_behavior(username: str = Body(..., embed=True), api_key: str = Body(..., embed=True)):
    """Module 5: Analysis & Data Persistence"""
    posts = await scraper.get_posts(username, ["X", "Instagram"])
    
    prompt = f"Analyze behavior for user '{username}' based on these posts: {json.dumps(posts)}. Provide JSON with keys: sentiment_trend, topic_heatmap, anomalies_crisis, future_prediction."
    
    try:
        model = get_gemini_model(api_key)
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        analysis = json.loads(text)
        
        # Save analysis to Supabase
        if sb_client:
            sb_client.table("targets").update({"ai_analysis": analysis}).eq("username", username).execute()
            
        return {"username": username, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
