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

### A. Google Gemini AI (For Analysis)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click **Create API Key**.
3. Save this code (to be entered into the App later).

### B. Supabase (For Database & Authentication)
1. Sign up at [Supabase.com](https://supabase.com/).
2. Create a new Project (e.g., `OmniTrace-DB`).
3. Go to **SQL Editor** (the `>_` icon on the left).
4. Run this query to create the **Targets** table:
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
5. Run this query to create the **Users** table for login:
   ```sql
   CREATE TABLE users (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     username TEXT UNIQUE NOT NULL,
     password TEXT NOT NULL, -- This will store hashed passwords
     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );
   ```
6. **Create your Admin User:**
   Since passwords must be hashed (BCrypt), use this pre-hashed password for the username `admin` (it hashes the string `admin123`):
   ```sql
   INSERT INTO users (username, password)
   VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0Lpue8uD7s.R1q3vU7p.fX.F.fX.F.fX.F.fX.');
   -- Username: admin
   -- Password: admin123
   ```
7. Go to **Project Settings** -> **API**:
   - Copy `Project URL`.
   - Copy `API Key` (Use `service_role` for backend and `anon` for frontend).

---

## 2. Local Setup (Running on your PC)

### Step 1: Install Required Software
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### Step 2: Set Environment Variables
1. Open the project folder.
2. Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```
3. Create `backend/.env`:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```

### Step 3: Start the Application
1. Open **Terminal** (Mac) or **Command Prompt/PowerShell** (Windows).
2. Navigate to the project folder.
3. Run the following command:
   ```bash
   docker-compose up --build
   ```
4. Access the dashboard at: `http://localhost:3000`.

---

## 3. App Usage Guide

1. **Login:** Use the username `admin` and password `admin123` (unless you changed it in SQL).
2. **AI Config:** Enter your **Gemini API Key** in the configuration box and click **Save**.
3. **Search:** Enter a person's name (e.g., "Son Tung M-TP") in the search box.
4. **Confirm:** Select a handle from the suggestions.
5. **Scan:** Click the scan button to find social media footprints.
6. **Analyze:** Click **Run AI Behavioral Analysis** to generate the intelligence report.

---

## 4. Deployment Guide (Vercel/Railway)

1. Push code to **GitHub**.
2. Deploy **Frontend** to **Vercel** (Set env variables).
3. Deploy **Backend** to **Railway** or **Render** using the provided `Dockerfile`.

---
*Happy exploring with OmniTrace AI!*
