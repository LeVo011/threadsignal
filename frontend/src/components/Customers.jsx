import { useEffect, useState } from "react"
import axios from "axios"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function Customers() {
  const [customers, setCustomers] = useState([])

  useEffect(() => {
    axios.get(`${API}/customers/`).then(r => setCustomers(r.data))
  }, [])

  return (
    <div style={{ padding: 24, overflowY: "auto", height: "100%", background: "#0f0f13" }}>
      <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 24 }}>Customers</h2>
      <div style={{ background: "#13131a", border: "1px solid #2d2d3d", borderRadius: 12, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #2d2d3d" }}>
              {["Name", "Email", "City", "Total Spent", "Last Order"].map(h => (
                <th key={h} style={{ padding: "12px 16px", textAlign: "left", fontSize: 12, color: "#64748b", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {customers.map(c => (
              <tr key={c.id} style={{ borderBottom: "1px solid #1e1e2e" }}>
                <td style={{ padding: "12px 16px", fontSize: 13, fontWeight: 500 }}>{c.name}</td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#64748b" }}>{c.email}</td>
                <td style={{ padding: "12px 16px", fontSize: 13 }}>{c.city}</td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#10b981", fontWeight: 600 }}>₹{c.total_spent?.toLocaleString()}</td>
                <td style={{ padding: "12px 16px", fontSize: 13, color: "#64748b" }}>
                  {c.last_order_date ? new Date(c.last_order_date).toLocaleDateString() : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
