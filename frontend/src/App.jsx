import { useState } from "react"
import Chat from "./components/Chat"
import Dashboard from "./components/Dashboard"
import Customers from "./components/Customers"
import { MessageSquare, LayoutDashboard, Users } from "lucide-react"

export default function App() {
  const [tab, setTab] = useState("chat")
  const [refreshKey, setRefreshKey] = useState(0)

  const triggerRefresh = () => setRefreshKey(k => k + 1)

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      {/* Sidebar */}
      <div style={{
        width: 220, background: "#13131a", borderRight: "1px solid #2d2d3d",
        display: "flex", flexDirection: "column", padding: "24px 0"
      }}>
        <div style={{ padding: "0 20px 32px" }}>
          <div style={{ fontSize: 22, fontWeight: 800, color: "#6366f1" }}>Thread</div>
          <div style={{ fontSize: 22, fontWeight: 800, color: "#a78bfa" }}>Signal</div>
          <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>AI Campaign Agent</div>
        </div>
        {[
          { id: "chat", label: "Campaign Agent", icon: MessageSquare },
          { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
          { id: "customers", label: "Customers", icon: Users },
        ].map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setTab(id)} style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "12px 20px", border: "none", cursor: "pointer",
            background: tab === id ? "#1e1e2e" : "transparent",
            color: tab === id ? "#6366f1" : "#94a3b8",
            borderLeft: tab === id ? "3px solid #6366f1" : "3px solid transparent",
            fontSize: 14, fontWeight: tab === id ? 600 : 400, width: "100%", textAlign: "left"
          }}>
            <Icon size={16} /> {label}
          </button>
        ))}
      </div>

      {/* Main */}
      <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
        {tab === "chat" && <Chat onCampaignRun={triggerRefresh} />}
        {tab === "dashboard" && <Dashboard refreshKey={refreshKey} />}
        {tab === "customers" && <Customers />}
      </div>
    </div>
  )
}