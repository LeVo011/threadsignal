import { useState, useRef, useEffect } from "react"
import axios from "axios"
import { Send, Bot, User, Zap } from "lucide-react"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

const suggestions = [
  "Find customers who haven't ordered in 60 days and send a win-back offer",
  "Reach high-value customers who spent over ₹3000 with an exclusive preview",
  "Target customers in Delhi with a city-exclusive flash sale",
  "Find customers with only 1 order and nudge them to buy again",
]

export default function Chat({ onCampaignRun }) {
  const [messages, setMessages] = useState([{
    role: "agent",
    content: "Hi! I'm ThreadSignal's AI campaign agent 👋\n\nTell me who you want to reach and what you want to say — I'll handle the segmentation, personalized messaging, and campaign execution.\n\nTry one of the suggestions below or type your own."
  }])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const send = async (text) => {
    const msg = text || input.trim()
    if (!msg) return
    setInput("")
    setMessages(m => [...m, { role: "user", content: msg }])
    setLoading(true)
    try {
      const res = await axios.post(`${API}/campaigns/chat`, { message: msg })
      setMessages(m => [...m, { role: "agent", content: res.data.response }])
      onCampaignRun()
    } catch {
      setMessages(m => [...m, { role: "agent", content: "Something went wrong. Please try again." }])
    }
    setLoading(false)
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#0f0f13" }}>
      {/* Header */}
      <div style={{
        padding: "16px 24px", borderBottom: "1px solid #2d2d3d",
        background: "#13131a", display: "flex", alignItems: "center", gap: 10
      }}>
        <Zap size={18} color="#6366f1" />
        <span style={{ fontWeight: 600, fontSize: 15 }}>Campaign Agent</span>
        <span style={{
          marginLeft: "auto", fontSize: 11, background: "#1a2e1a",
          color: "#4ade80", padding: "3px 10px", borderRadius: 20, border: "1px solid #166534"
        }}>● Live</span>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "24px", display: "flex", flexDirection: "column", gap: 16 }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            display: "flex", gap: 12, flexDirection: m.role === "user" ? "row-reverse" : "row",
            alignItems: "flex-start"
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: "50%", flexShrink: 0,
              background: m.role === "user" ? "#6366f1" : "#1e1e2e",
              border: "1px solid #2d2d3d",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              {m.role === "user" ? <User size={14} /> : <Bot size={14} color="#6366f1" />}
            </div>
            <div style={{
              maxWidth: "70%", padding: "12px 16px", borderRadius: 12,
              background: m.role === "user" ? "#6366f1" : "#1a1a2e",
              border: m.role === "agent" ? "1px solid #2d2d3d" : "none",
              fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap"
            }}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
            <div style={{
              width: 32, height: 32, borderRadius: "50%", background: "#1e1e2e",
              border: "1px solid #2d2d3d", display: "flex", alignItems: "center", justifyContent: "center"
            }}>
              <Bot size={14} color="#6366f1" />
            </div>
            <div style={{
              padding: "12px 16px", borderRadius: 12, background: "#1a1a2e",
              border: "1px solid #2d2d3d", fontSize: 14, color: "#64748b"
            }}>
              Segmenting customers and crafting messages...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div style={{ padding: "0 24px 16px", display: "flex", flexWrap: "wrap", gap: 8 }}>
          {suggestions.map((s, i) => (
            <button key={i} onClick={() => send(s)} style={{
              padding: "8px 14px", borderRadius: 20, border: "1px solid #2d2d3d",
              background: "#1a1a2e", color: "#94a3b8", fontSize: 12, cursor: "pointer",
              transition: "all 0.2s"
            }}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div style={{
        padding: "16px 24px", borderTop: "1px solid #2d2d3d",
        background: "#13131a", display: "flex", gap: 12
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          placeholder="Describe your campaign goal..."
          style={{
            flex: 1, padding: "12px 16px", borderRadius: 10,
            background: "#1e1e2e", border: "1px solid #2d2d3d",
            color: "#e2e8f0", fontSize: 14, outline: "none"
          }}
        />
        <button onClick={() => send()} disabled={loading} style={{
          padding: "12px 20px", borderRadius: 10, border: "none",
          background: loading ? "#2d2d3d" : "#6366f1", color: "white",
          cursor: loading ? "not-allowed" : "pointer", display: "flex", alignItems: "center", gap: 6
        }}>
          <Send size={16} />
        </button>
      </div>
    </div>
  )
}
