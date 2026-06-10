import { useEffect, useState } from "react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { TrendingUp, Users, Send, MousePointer } from "lucide-react"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function Dashboard({ refreshKey }) {
  const [stats, setStats] = useState(null)
  const [campaigns, setCampaigns] = useState([])
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    let active = true

    const loadDashboard = () => {
      axios.get(`${API}/customers/stats`).then(r => {
        if (active) setStats(r.data)
      })

      axios.get(`${API}/campaigns/`).then(r => {
        if (!active) return
        setCampaigns(r.data)
        setSelected(current => {
          if (r.data.length === 0) return null
          return r.data.find(c => c.id === current?.id) || r.data[0]
        })
      })
    }

    loadDashboard()
    const interval = setInterval(loadDashboard, 3000)
    return () => {
      active = false
      clearInterval(interval)
    }
  }, [refreshKey])

  const statCards = stats ? [
    { label: "Total Customers", value: stats.total_customers, icon: Users, color: "#6366f1" },
    { label: "Inactive 60d+", value: stats.inactive_60d, icon: TrendingUp, color: "#f59e0b" },
    { label: "High Value", value: stats.high_value, icon: Send, color: "#10b981" },
    { label: "Total Revenue", value: `₹${stats.total_revenue?.toLocaleString()}`, icon: MousePointer, color: "#a78bfa" },
  ] : []

  const chartData = selected ? [
    { name: "Sent", value: selected.stats.sent || 0, color: "#6366f1" },
    { name: "Delivered", value: selected.stats.delivered || 0, color: "#10b981" },
    { name: "Opened", value: selected.stats.opened || 0, color: "#f59e0b" },
    { name: "Clicked", value: selected.stats.clicked || 0, color: "#a78bfa" },
    { name: "Failed", value: selected.stats.failed || 0, color: "#ef4444" },
  ] : []

  return (
    <div style={{ padding: 24, overflowY: "auto", height: "100%", background: "#0f0f13" }}>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 24 }}>Dashboard</h2>

      {/* Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
        {statCards.map((s, i) => (
          <div key={i} style={{
            background: "#13131a", border: "1px solid #2d2d3d", borderRadius: 12, padding: 20
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>{s.label}</div>
                <div style={{ fontSize: 24, fontWeight: 700, color: s.color }}>{s.value}</div>
              </div>
              <s.icon size={24} color={s.color} opacity={0.5} />
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Campaign List */}
        <div style={{ background: "#13131a", border: "1px solid #2d2d3d", borderRadius: 12, padding: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, color: "#94a3b8" }}>Recent Campaigns</h3>
          {campaigns.length === 0 ? (
            <div style={{ color: "#64748b", fontSize: 13 }}>No campaigns yet. Run one from the Agent tab.</div>
          ) : (
            campaigns.map(c => (
              <div key={c.id} onClick={() => setSelected(c)} style={{
                padding: "12px 14px", borderRadius: 8, marginBottom: 8, cursor: "pointer",
                background: selected?.id === c.id ? "#1e1e2e" : "transparent",
                border: selected?.id === c.id ? "1px solid #6366f1" : "1px solid transparent",
                transition: "all 0.2s"
              }}>
                <div style={{ fontSize: 13, fontWeight: 500 }}>{c.name}</div>
                <div style={{ fontSize: 11, color: "#64748b", marginTop: 3 }}>
                  {c.total_messages} messages · {new Date(c.created_at).toLocaleDateString()}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Chart */}
        <div style={{ background: "#13131a", border: "1px solid #2d2d3d", borderRadius: 12, padding: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, color: "#94a3b8" }}>
            {selected ? `Performance: ${selected.name}` : "Select a campaign"}
          </h3>
          {selected && (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: "#1e1e2e", border: "1px solid #2d2d3d", borderRadius: 8 }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Message Logs */}
      {selected && <CampaignLogs campaignId={selected.id} />}
    </div>
  )
}

function CampaignLogs({ campaignId }) {
  const [logs, setLogs] = useState([])

  useEffect(() => {
    axios.get(`${API}/campaigns/${campaignId}/logs`).then(r => setLogs(r.data))
    const interval = setInterval(() => {
      axios.get(`${API}/campaigns/${campaignId}/logs`).then(r => setLogs(r.data))
    }, 3000)
    return () => clearInterval(interval)
  }, [campaignId])

  const statusColor = {
    queued: "#64748b", sent: "#6366f1", delivered: "#10b981",
    opened: "#f59e0b", clicked: "#a78bfa", failed: "#ef4444"
  }

  return (
    <div style={{ marginTop: 24, background: "#13131a", border: "1px solid #2d2d3d", borderRadius: 12, padding: 20 }}>
      <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, color: "#94a3b8" }}>
        Message Log — {logs.length} messages
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {logs.map(log => (
          <div key={log.id} style={{
            padding: "12px 16px", borderRadius: 8,
            background: "#0f0f13", border: "1px solid #2d2d3d"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
              <span style={{ fontSize: 12, color: "#64748b" }}>Customer #{log.customer_id} · {log.channel}</span>
              <span style={{
                fontSize: 11, padding: "2px 8px", borderRadius: 10,
                background: statusColor[log.status] + "22",
                color: statusColor[log.status], border: `1px solid ${statusColor[log.status]}44`
              }}>{log.status}</span>
            </div>
            <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.5 }}>{log.message}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
