"use client";

import { useState, useEffect } from "react";
import { auth } from "@/lib/firebase";
import { signInWithEmailAndPassword, onAuthStateChanged, signOut } from "firebase/auth";
import axios from "axios";

const API_BASE = "http://localhost:8000";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [geminiKey, setGeminiKey] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestedUsernames, setSuggestedUsernames] = useState<string[]>([]);
  const [selectedUsername, setSelectedUsername] = useState("");
  const [scanResults, setScanResults] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
    });
    const savedKey = localStorage.getItem("gemini_api_key");
    if (savedKey) setGeminiKey(savedKey);
    return () => unsubscribe();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error: any) {
      alert("Login failed: " + error.message);
    }
  };

  const handleLogout = () => signOut(auth);

  const saveGeminiKey = () => {
    localStorage.setItem("gemini_api_key", geminiKey);
    alert("API Key saved locally");
  };

  const searchIdentity = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/search-identity`, { 
        query: searchQuery, 
        api_key: geminiKey 
      });
      setSuggestedUsernames(res.data.suggested_usernames);
    } catch (err) {
      alert("Search failed");
    } finally {
      setLoading(false);
    }
  };

  const scanUsername = async (username: string) => {
    setSelectedUsername(username);
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/scan-username`, { username });
      setScanResults(res.data.results);
      setAnalysis(null);
    } catch (err) {
      alert("Scan failed");
    } finally {
      setLoading(false);
    }
  };

  const analyzeBehavior = async () => {
    if (!geminiKey) return alert("Please provide Gemini API Key");
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/analyze-behavior`, { 
        username: selectedUsername, 
        api_key: geminiKey 
      });
      setAnalysis(res.data.analysis);
    } catch (err) {
      alert("Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div className="card" style={{ width: '400px' }}>
          <h1 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>OmniTrace AI</h1>
          <form onSubmit={handleLogin}>
            <input 
              className="input" 
              type="email" 
              placeholder="Email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
            />
            <input 
              className="input" 
              type="password" 
              placeholder="Password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
            />
            <button className="btn btn-primary" style={{ width: '100%' }} type="submit">Login</button>
          </form>
          <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            Use the credentials provided by your administrator.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <div>
          <h1>OmniTrace AI Dashboard</h1>
          <p style={{ color: 'var(--text-muted)' }}>OSINT & Behavioral Intelligence</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.9rem' }}>{user.email}</span>
          <button className="btn" style={{ background: '#e2e8f0' }} onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <div className="grid">
        {/* Configuration Card */}
        <div className="card">
          <h3>Configuration</h3>
          <p style={{ fontSize: '0.875rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>
            Enter your Google Gemini API Key to enable AI analysis.
          </p>
          <input 
            className="input" 
            type="password" 
            placeholder="Gemini API Key" 
            value={geminiKey} 
            onChange={(e) => setGeminiKey(e.target.value)} 
          />
          <button className="btn btn-primary" onClick={saveGeminiKey}>Save Key</button>
        </div>

        {/* Identity Discovery Card */}
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <h3>Identity Discovery</h3>
          <p style={{ fontSize: '0.875rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>
            Search by name or description to discover digital footprints.
          </p>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              className="input" 
              style={{ marginBottom: 0 }}
              placeholder="e.g. Son Tung M-TP or Tech CEO" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="btn btn-primary" onClick={searchIdentity} disabled={loading}>
              {loading ? "Searching..." : "Identify"}
            </button>
          </div>

          {suggestedUsernames.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <p style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Suggested Handles:</p>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {suggestedUsernames.map(u => (
                  <button 
                    key={u} 
                    className="btn" 
                    style={{ background: selectedUsername === u ? 'var(--primary)' : '#f1f5f9', color: selectedUsername === u ? 'white' : 'black', fontSize: '0.8rem' }}
                    onClick={() => scanUsername(u)}
                  >
                    @{u}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {scanResults.length > 0 && (
        <div className="grid" style={{ marginTop: '2rem' }}>
          <div className="card">
            <h3>Digital Footprint: @{selectedUsername}</h3>
            <div style={{ marginTop: '1rem' }}>
              {scanResults.map((res, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid var(--border)' }}>
                  <span>{res.platform}</span>
                  <a href={res.url} target="_blank" className="badge badge-active" style={{ textDecoration: 'none' }}>Visit Profile</a>
                </div>
              ))}
            </div>
            <button 
              className="btn btn-primary" 
              style={{ width: '100%', marginTop: '1.5rem' }} 
              onClick={analyzeBehavior}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Run AI Behavioral Analysis"}
            </button>
          </div>

          {analysis && (
            <div className="card" style={{ gridColumn: 'span 2' }}>
              <h3>AI Behavioral Intelligence</h3>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ color: 'var(--primary)' }}>Sentiment Trend</h4>
                  <p>{analysis.sentiment_trend || analysis["Sentiment Trend"]}</p>
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ color: 'var(--primary)' }}>Topic Heatmap</h4>
                  <p>{analysis.topic_heatmap || analysis["Topic Heatmap"]}</p>
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ color: 'var(--primary)' }}>Anomalies & Crisis</h4>
                  <p>{analysis.anomalies_crisis || analysis["Anomalies & Crisis"]}</p>
                </div>
                <div>
                  <h4 style={{ color: 'var(--primary)' }}>Future Prediction</h4>
                  <p>{analysis.future_prediction || analysis["Future Prediction"]}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
