import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiFetch } from "../lib/api";

function StatCard({ label, value, loading }) {
  return (
    <div style={{
      background: "#fff",
      border: "1px solid #e5e7eb",
      borderRadius: 8,
      padding: "24px 32px",
      minWidth: 160,
      textAlign: "center",
    }}>
      <div style={{ fontSize: 36, fontWeight: 700, color: "#111827" }}>
        {loading ? "—" : value}
      </div>
      <div style={{ fontSize: 14, color: "#6b7280", marginTop: 4 }}>{label}</div>
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/admin/stats")
      .then(setStats)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <Layout>
      <h1 style={{ marginBottom: 8 }}>Dashboard</h1>
      <p style={{ color: "#6b7280", marginBottom: 32 }}>Overview of your Quota instance.</p>

      {error && (
        <div style={{ color: "#dc2626", marginBottom: 24 }}>{error}</div>
      )}

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <StatCard label="Plans" value={stats?.total_plans} loading={!stats && !error} />
        <StatCard label="API Keys" value={stats?.total_keys} loading={!stats && !error} />
        <StatCard label="Requests Today" value={stats?.requests_today} loading={!stats && !error} />
      </div>
    </Layout>
  );
}
