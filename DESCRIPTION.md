# SOFTWARE SPECIFICATION: OMNITRACE AI (OSINT & BEHAVIORAL ANALYTICS)

## 1. Project Overview
OmniTrace AI is a next-generation Open Source Intelligence (OSINT) platform. Instead of just searching for usernames, the system allows identity discovery from real names or descriptions, followed by a comprehensive scan of digital footprints across social media, historical data collection, and the use of AI (Gemini) for psychological, behavioral analysis, and trend forecasting.

## 2. Tech Stack Recommendation
*   **Backend:** Python (FastAPI) - Optimized for running OSINT scripts and data processing.
*   **Frontend:** React.js or Next.js (Intuitive Dashboard).
*   **Database:** Supabase (Primary relational DB for targets/logs) & Firebase (Authentication & JSON caching).
*   **Search Engine:** SerpApi (Google Search) or DuckDuckGo API for identity discovery.
*   **Core Tools:** Sherlock (Username discovery), Playwright/Scrapy (Social Scraping).
*   **AI Engine:** Google Gemini Pro 1.5 (Long context window for 12-month data analysis).

## 3. Core Modules & Workflow

### Module 1: Identity Discovery (Chatbot & Search)
*   **Input:** Celebrity name, job title, or description (e.g., "Son Tung M-TP" or "CEO of Company X").
*   **Process:**
    1.  AI Agent receives the request via chat.
    2.  Uses Search APIs to find common handles/usernames (Twitter, Instagram, LinkedIn).
    3.  Presents a list of results for user confirmation.
*   **Output:** A confirmed `primary_username`.

### Module 2: Cross-Platform Scouting (Sherlock Engine)
*   **Input:** `primary_username` from Module 1.
*   **Process:** Runs Sherlock script to scan 400+ platforms.
*   **Output:** List of valid profile URLs.

### Module 3: Smart Caching & Persistence
*   **Logic:** 
    1.  Check database before scanning.
    2.  If exists and `last_scanned` < 60 days: Return cached results.
    3.  Otherwise: Trigger Module 2 and Module 4, then update the database.

### Module 4: Data Scraping & Time-Travel
*   **Target Platforms:** X (Twitter), Reddit, Instagram, Facebook, TikTok.
*   **Data Points:** Post content, timestamps, engagement metrics (Likes/Shares/Comments).

### Module 5: Gemini AI Behavioral Analysis
*   **Analysis Pillars:**
    *   *Sentiment Trend:* Emotional trend over time.
    *   *Topic Heatmap:* Primary interests and recurring themes.
    *   *Anomalies & Crisis:* Detection of engagement spikes or sudden attitude shifts.
    *   *Future Prediction:* Forecast of interaction trends based on past data.

---

## 4. Agent Instructions (Prompt to Start Coding)

> "Build a Python FastAPI application integrated with Supabase and Firebase.
> 1. Create a `/search-identity` endpoint that suggests social media handles based on a name.
> 2. Implement caching logic: if a username was scanned within 60 days, fetch from DB. Otherwise, run Sherlock.
> 3. Integrate a scraping module to fetch posts from the last few months.
> 4. Send this data to Gemini AI for behavioral analysis: 'Analyze behavior, emotional shifts, and crisis risks for this subject'.
> 5. Save all results to the database and return JSON to the frontend."
