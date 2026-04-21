"use client";

import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const AVAILABLE_MODELS = [
  "gemini-3.1-pro-preview",
  "gemini-3-flash-preview",
  "gemini-3.1-flash-lite-preview",
  "gemini-2.5-flash",
  "gemini-2.5-flash-lite",
  "gemini-2.5-pro",
];

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [geminiKey, setGeminiKey] = useState("");
  const [selectedModel, setSelectedModel] = useState("gemini-2.5-flash-lite");
  const [messages, setMessages] = useState<string[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [identityData, setIdentityData] = useState<{ platform: string, username: string, url: string }[]>([
    { platform: "Facebook", username: "", url: "" },
    { platform: "Instagram", username: "", url: "" },
    { platform: "TikTok", username: "", url: "" },
    { platform: "Threads", username: "", url: "" },
    { platform: "X (Twitter)", username: "", url: "" },
    { platform: "Youtube", username: "", url: "" },
  ]);

  useEffect(() => {
    const savedUser = localStorage.getItem("omnitrace_user");
    if (savedUser) setUser(JSON.parse(savedUser));
    const savedKey = localStorage.getItem("gemini_api_key");
    if (savedKey) setGeminiKey(savedKey);
    const savedModel = localStorage.getItem("gemini_model");
    if (savedModel) setSelectedModel(savedModel);
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

  const saveConfig = async () => {
    localStorage.setItem("gemini_api_key", geminiKey);
    localStorage.setItem("gemini_model", selectedModel);

    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/chat-init`, {
        api_key: geminiKey,
        model_id: selectedModel
      });
      setMessages([`🤖 AI: ${res.data.message}`]);
    } catch (err: any) {
      alert("Configuration saved, but greeting failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setMessages(prev => [...prev, `🧑 User: ${userMsg}`]);
    setChatInput("");

    try {
      const res = await axios.post(`${API_BASE}/chat-message`, {
        message: userMsg,
        api_key: geminiKey
      });
      setMessages(prev => [...prev, `🤖 AI: ${res.data.response}`]);
    } catch (err: any) {
      setMessages(prev => [...prev, `🤖 AI: Error - ${err.message}`]);
    }
  };

  const updateEntry = (index: number, field: string, value: string) => {
    const newData = [...identityData];
    newData[index] = { ...newData[index], [field]: value };
    setIdentityData(newData);
  };

  const addIdentityEntry = () => {
    setIdentityData([...identityData, { platform: "Other", username: "", url: "" }]);
  };

  const searchIdentity = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/search-identity`, {
        query: searchQuery,
        api_key: geminiKey
      });
      if (res.data.suggested_usernames?.data) {
        setIdentityData(res.data.suggested_usernames.data);
      }
    } catch (err) {
      alert("Search failed");
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div className="card" style={{ width: '400px' }}>
          <h1 style={{ marginBottom: '1.5rem', textAlign: 'center', color: 'var(--neon-blue)' }}>OmniTrace AI</h1>
          <form onSubmit={handleLogin}>
            <input className="input" type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
            <input className="input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <button className="btn" style={{ width: '100%' }} type="submit" disabled={loading}>{loading ? "Logging in..." : "Login"}</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <h1>OmniTrace AI Dashboard</h1>
        <button className="btn" onClick={handleLogout}>Logout</button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem', height: 'calc(100vh - 150px)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card">
            <h3>Configuration</h3>
            <input className="input" type="password" placeholder="Gemini API Key" value={geminiKey} onChange={(e) => setGeminiKey(e.target.value)} />
            <select className="input" value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
              {AVAILABLE_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
            <button className="btn" onClick={saveConfig}>Save Config</button>
          </div>

          <div className="card" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <h3>Chat</h3>
            <div style={{ flexGrow: 1, overflowY: 'auto', marginBottom: '0.5rem', background: '#0a0b10', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}>
              {messages.map((m, i) => <p key={i} style={{ marginBottom: '0.5rem' }}>{m}</p>)}
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input className="input" style={{ marginBottom: 0 }} placeholder="Message AI..." value={chatInput} onChange={(e) => setChatInput(e.target.value)} />
              <button className="btn" onClick={handleSendMessage}>Send</button>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card">
            <h3>Identity Discovery</h3>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input className="input" style={{ marginBottom: 0 }} placeholder="Enter name" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
              <button className="btn" onClick={searchIdentity}>Identify</button>
            </div>
          </div>

          <div className="card" style={{ flexGrow: 1, overflowY: 'auto' }}>
            <h3>Dashboard</h3>
            <div style={{
              marginTop: '1rem',
              background: '#0a0b10',
              padding: '1rem',
              borderRadius: '8px',
              border: '1px solid var(--border)'
            }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {identityData.map((entry, idx) => (
                  <div key={idx} style={{
                    display: 'flex',
                    gap: '0.5rem',
                    alignItems: 'center',
                    background: 'rgba(255, 255, 255, 0.05)',
                    padding: '0.5rem',
                    borderRadius: '4px'
                  }}>
                    <input className="input" style={{ marginBottom: 0 }} placeholder="Platform" value={entry.platform} onChange={(e) => updateEntry(idx, 'platform', e.target.value)} />
                    <input className="input" style={{ marginBottom: 0 }} placeholder="Username" value={entry.username} onChange={(e) => updateEntry(idx, 'username', e.target.value)} />
                    <input className="input" style={{ marginBottom: 0 }} placeholder="URL" value={entry.url} onChange={(e) => updateEntry(idx, 'url', e.target.value)} />
                  </div>
                ))}
              </div>
              <button className="btn" style={{ marginTop: '1rem', width: '100%' }} onClick={addIdentityEntry}>+ Add Platform</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
