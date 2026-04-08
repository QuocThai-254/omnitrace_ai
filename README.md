# 🕵️ OmniTrace AI - Comprehensive Setup Guide (A-Z)

**OmniTrace AI** is an Open Source Intelligence (OSINT) platform. It enables you to discover a person's digital footprint from their real name, then uses Gemini AI to analyze their personality and behavior.

---

## 📑 Table of Contents
1. [Resource Preparation (Free Tier)](#1-resource-preparation-free-tier)
2. [Local Setup (Running on your PC)](#2-local-setup-running-on-your-pc)
3. [App Usage Guide](#3-app-usage-guide)
4. [Deployment Guide (Vercel/Railway)](#4-deployment-guide-vercelrailway)

---

## 1. Resource Preparation (Free Tier)

You will need to prepare 3 "keys" below. All of them have a free tier.

### A. Google Gemini AI (For Analysis)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click **Create API Key**.
3. Save this code (to be entered into the App later).

### B. Supabase (For Data Storage)
1. Sign up at [Supabase.com](https://supabase.com/).
2. Create a new Project (e.g., `OmniTrace-DB`).
3. Go to **SQL Editor** (the `>_` icon on the left).
4. Paste the following code and click **Run**:
   ```sql
   CREATE TABLE targets (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     username TEXT UNIQUE NOT NULL,
     results JSONB,
     ai_analysis JSONB,
     last_scanned BIGINT,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```
5. Go to **Project Settings** -> **API**:
   - Copy `Project URL`.
   - Copy `API Key` (`service_role` for backend and `anon` for frontend).

### C. Firebase (For Authentication)
1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Create a new Project.
3. Go to **Build** -> **Authentication** -> **Get Started** -> Enable **Email/Password**.
4. Create a user account for yourself to login later.
5. Go to **Project Settings** (gear icon) -> Scroll down -> Select Web icon (`</>`) to get the configuration (apiKey, authDomain, etc.).
6. Go to **Service Accounts** -> Click **Generate new private key** -> Download the `.json` file, rename it to `serviceAccountKey.json`, and place it in the `backend/` folder.

---

## 2. Local Setup (Running on your PC)

The easiest way for non-technical users is to use **Docker**.

### Step 1: Install Required Software
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/). (Just download, click Next until finished, and open it).

### Step 2: Set Environment Variables
1. Open the project folder.
2. Create `frontend/.env.local` and paste the Firebase/Supabase info:
   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=...
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
   NEXT_PUBLIC_FIREBASE_APP_ID=...
   
   NEXT_PUBLIC_SUPABASE_URL=...
   NEXT_PUBLIC_SUPABASE_ANON_KEY=...
   ```
3. Create `backend/.env` and paste:
   ```env
   SUPABASE_URL=...
   SUPABASE_SERVICE_ROLE_KEY=...
   ```

### Step 3: Start the Application
1. Open **Terminal** (Mac) or **Command Prompt/PowerShell** (Windows).
2. Navigate to the project folder (use `cd path_to_folder`).
3. Run the following command:
   ```bash
   docker-compose up --build
   ```
4. Wait for 2-3 minutes. Once the screen indicates completion, open your browser and go to: `http://localhost:3000`.

---

## 3. App Usage Guide

1. **Login:** Use the email/password you created in the Firebase step.
2. **AI Config:** Enter your **Gemini API Key** into the configuration box on the left and click **Save**.
3. **Search:** Enter a person's name (e.g., "Son Tung M-TP") in the search box.
4. **Confirm:** The App will suggest usernames. Click on a username (e.g., `@sontungmtp`).
5. **Scan:** Click the scan button. The App will find social media links (Facebook, Instagram, X, etc.) for that person.
6. **Analyze:** Click **Run AI Behavioral Analysis**. Wait a few seconds for Gemini to process the data and provide a behavioral report.

---

## 4. Deployment Guide (Vercel/Railway)

If you want to share the link with others:

1. Push this code to **GitHub**.
2. Log in to [Vercel](https://vercel.com/).
3. Click **Add New** -> **Project** -> Select the Repo from GitHub.
4. **Configure:**
   - Framework preset: `Next.js`.
   - Root directory: `frontend`.
   - Enter all environment variables from Step 2 in the **Environment Variables** section.
5. Click **Deploy**.
6. **Note on Backend:** Since the Backend includes the heavy Sherlock tool, the free version of Vercel might not be able to run it. It is recommended to use **Railway.app** or **Render.com** to host the `backend/` folder (which supports Dockerfile execution).

---
*Happy exploring with OmniTrace AI!*
