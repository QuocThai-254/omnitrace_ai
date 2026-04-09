"use client";

import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [geminiKey, setGeminiKey] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestedUsernames, setSuggestedUsernames] = useState<string[]>([]);
  const [selectedUsername, setSelectedUsername] = useState("");
  const [scanResults, setScanResults] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem("omnitrace_user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    const savedKey = localStorage.getItem("gemini_api_key");
    if (savedKey) setGeminiKey(savedKey);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/login`, { username, password });
      setUser(res.data.user);
      localStorage.setItem("omnitrace_user", JSON.stringify(res.data.user));
    } catch (error: any) {
      alert("Login failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("omnitrace_user");
  };

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

  const scanUsername = async (u: string) => {
    setSelectedUsername(u);
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/scan-username`, { username: u });
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
              type="text" 
              placeholder="Username" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
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
            <button className="btn btn-primary" style={{ width: '100%' }} type="submit" disabled={loading}>
              {loading ? "Logging in..." : "Login"}
            </button>
          </form>
          <p style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            Admin Login Only
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
          <p style={{ color: 'var(--text-muted)' }}>Logged in as: <strong>{user.username}</strong></p>
        </div>
        <button className="btn" style={{ background: '#e2e8f0' }} onClick={handleLogout}>Logout</button>
      </header>

      <div className="grid">
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

        <div className="card" style={{ gridColumn: 'span 2' }}>
          <h3>Identity Discovery</h3>
          <p style={{ fontSize: '0.875rem', marginBottom: '1rem', color: 'var(--text-muted)' }}>
            Search by name or description to discover digital footprints.
          </p>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              className="input" 
              style={{ marginBottom: 0 }}
              placeholder="e.g. Son Tung M-TP" 
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
                  <a href={res.url} target="_blank" rel="noreferrer" className="badge badge-active" style={{ textDecoration: 'none' }}>Visit Profile</a>
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
                  <p>{analysis.sentiment_trend || analysis["sentiment_trend"]}</p>
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ color: 'var(--primary)' }}>Topic Heatmap</h4>
                  <p>{analysis.topic_heatmap || analysis["topic_heatmap"]}</p>
                </div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ color: 'var(--primary)' }}>Anomalies & Crisis</h4>
                  <p>{analysis.anomalies_crisis || analysis["anomalies_crisis"]}</p>
                </div>
                <div>
                  <h4 style={{ color: 'var(--primary)' }}>Future Prediction</h4>
                  <p>{analysis.future_prediction || analysis["future_prediction"]}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
