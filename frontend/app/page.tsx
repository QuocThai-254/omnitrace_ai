"use client";

import { useState, useMemo } from "react";
import axios from "axios";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const AVAILABLE_MODELS = [
  "gemini-3.1-pro-preview",
  "gemini-3-flash-preview",
  "gemini-3.1-flash-lite-preview",
  "gemini-2.5-flash",
  "gemini-2.5-flash-lite",
  "gemini-2.5-pro",
];

const COLORS = ["#00f2ff", "#9d4edd", "#2563eb", "#22c55e", "#ef4444", "#f59e0b"];

// Hàm chuẩn hóa số
const formatNumber = (num: number): string => {
  if (num >= 1e9) return (num / 1e9).toFixed(1) + "B";
  if (num >= 1e6) return (num / 1e6).toFixed(1) + "M";
  if (num >= 1e3) return (num / 1e3).toFixed(1) + "K";
  return num.toString();
};

export default function Home() {
  const [geminiKey, setGeminiKey] = useState("");
  const [selectedModel, setSelectedModel] = useState("gemini-2.5-flash-lite");
  const [messages, setMessages] = useState<string[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [identityData, setIdentityData] = useState<any[]>([]);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [showChart, setShowChart] = useState(false);

  // Tính toán dữ liệu biểu đồ bao gồm cả những nền tảng có 0 followers
  const chartData = useMemo(() => {
    return identityData.map((d) => ({ 
      name: d.platform, 
      value: d.followers || 0 
    }));
  }, [identityData]);

  const totalFollowers = useMemo(() => {
    return identityData.reduce((acc, curr) => acc + (curr.followers || 0), 0);
  }, [identityData]);

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setMessages(prev => [...prev, `🧑 User: ${userMsg}`]);
    setChatInput("");
    try {
      const res = await axios.post(`${API_BASE}/chat-message`, { message: userMsg, api_key: geminiKey });
      setMessages(prev => [...prev, `🤖 AI: ${res.data.response}`]);
    } catch (err: any) {
      setMessages(prev => [...prev, `🤖 AI: Error`]);
    }
  };

  const searchIdentity = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/search-identity`, { query: searchQuery, api_key: geminiKey });
      if (res.data.suggested_usernames?.data) {
        const data = res.data.suggested_usernames.data;
        const validData = data.filter((item: any) => item !== null && item !== undefined);
        const insightRes = await axios.post(`${API_BASE}/infer-insight`, { profiles: validData });
        setIdentityData(insightRes.data.results);
      }
    } catch (err) {
      alert("Search failed");
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    localStorage.setItem("gemini_api_key", geminiKey);
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/chat-init`, { api_key: geminiKey, model_id: selectedModel });
      setMessages([`🤖 AI: ${res.data.message}`]);
    } catch (err: any) { alert("Config saved"); } finally { setLoading(false); }
  };

  return (
    <div className="container">
      <header className="header"><h1>OmniTrace AI Dashboard</h1></header>
      
      <div className="card" style={{ marginBottom: '1rem' }}>
        <h3>Configuration & Identity</h3>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input className="input" type="password" placeholder="Gemini API Key" value={geminiKey} onChange={(e) => setGeminiKey(e.target.value)} />
          <button className="btn" onClick={saveConfig}>Save Config & Init Chat</button>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <input className="input" placeholder="Search Query" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
          <button className="btn" onClick={searchIdentity}>Identify</button>
          {loading && <p style={{ marginLeft: '1rem', color: 'var(--neon-blue)' }}>Loading...</p>}
        </div>
      </div>

      <button className="btn" onClick={() => setShowChart(!showChart)} style={{ marginBottom: '1rem' }}>
        {showChart ? "Hide Insight Chart" : "Show Insight Chart"}
      </button>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1rem' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3>Chat Assistant</h3>
          <select className="input" value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
            {AVAILABLE_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <div style={{ height: '300px', overflowY: 'auto', background: '#0a0b10', padding: '0.5rem', marginBottom: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}>
            {messages.map((m, i) => <p key={i} style={{ marginBottom: '0.5rem' }}>{m}</p>)}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input className="input" style={{ marginBottom: 0 }} placeholder="Message AI..." value={chatInput} onChange={(e) => setChatInput(e.target.value)} />
            <button className="btn" onClick={handleSendMessage}>Send</button>
          </div>
        </div>
        <div className="card">
          <h3>Analysis Dashboard</h3>
          <div style={{ display: 'grid', gridTemplateColumns: showChart ? '1.5fr 1fr' : '1fr', gap: '2rem' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', color: 'white' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th>Platform</th>
                  <th>Username</th>
                  <th>Link</th>
                  <th>Valid</th>
                </tr>
              </thead>
              <tbody>
                {identityData.map((entry, idx) => (
                  <tr key={idx} style={{ textAlign: 'center', padding: '0.5rem' }}>
                    <td>{entry.platform}</td>
                    <td>{entry.username}</td>
                    <td><a href={entry.url} target="_blank" style={{ color: 'var(--neon-blue)' }}>Open</a></td>
                    <td>{entry.valid === undefined ? "⚪" : entry.valid ? "✅" : "❌"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {showChart && chartData.length > 0 && (
              <div style={{ height: '300px', position: 'relative' }}>
                <div style={{ position: 'absolute', top: '40%', left: '0', right: '0', textAlign: 'center', pointerEvents: 'none' }}>
                  <p style={{ fontSize: '12px', margin: 0 }}>Total</p>
                  <p style={{ fontWeight: 'bold', fontSize: '18px', margin: 0 }}>{formatNumber(totalFollowers)}</p>
                </div>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie 
                      data={chartData} dataKey="value" innerRadius={60} outerRadius={80} 
                      onMouseEnter={(_, i) => setActiveIndex(i)}
                      onMouseLeave={() => setActiveIndex(null)}
                    >
                      {chartData.map((_, i) => (
                        <Cell 
                          key={i} 
                          fill={COLORS[i % COLORS.length]} 
                          opacity={activeIndex === i || activeIndex === null ? 1 : 0.3} 
                        />
                      ))}
                    </Pie>
                    <Tooltip formatter={(val: number) => formatNumber(val)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
