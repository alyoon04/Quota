import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiFetch } from "../lib/api";

export default function ApiKeys() {
  const [keys, setKeys] = useState([]);
  const [plans, setPlans] = useState([]);
  const [label, setLabel] = useState("");
  const [planId, setPlanId] = useState("");
  const [newKey, setNewKey] = useState("");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const loadData = async () => {
    try {
      const [keysData, plansData] = await Promise.all([
        apiFetch("/admin/api-keys"),
        apiFetch("/admin/plans"),
      ]);
      setKeys(keysData);
      setPlans(plansData);
      if (plansData.length > 0 && !planId) {
        setPlanId(plansData[0].id);
      }
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    setNewKey("");
    setCopied(false);
    try {
      const data = await apiFetch("/admin/api-keys", {
        method: "POST",
        body: JSON.stringify({ label, plan_id: planId }),
      });
      setNewKey(data.plaintext_key);
      setLabel("");
      await loadData();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(newKey);
    setCopied(true);
  };

  const getPlanName = (id) => {
    const plan = plans.find((p) => p.id === id);
    return plan ? plan.name : id;
  };

  return (
    <Layout>
      <h2>API Keys</h2>

      <form onSubmit={handleCreate} style={{ marginBottom: "2rem", display: "flex", gap: "0.5rem", alignItems: "flex-end" }}>
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", marginBottom: "0.25rem" }}>Label</label>
          <input
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            required
            style={{ padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", marginBottom: "0.25rem" }}>Plan</label>
          <select
            value={planId}
            onChange={(e) => setPlanId(e.target.value)}
            required
            style={{ padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          >
            {plans.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.default_rpm} RPM)
              </option>
            ))}
          </select>
        </div>
        <button type="submit" style={{ padding: "0.5rem 1rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          Create Key
        </button>
      </form>

      {newKey && (
        <div style={{ padding: "1rem", background: "#f0f9ff", border: "1px solid #0070f3", borderRadius: 4, marginBottom: "1rem" }}>
          <p style={{ margin: "0 0 0.5rem 0", fontWeight: "bold" }}>New API Key (copy now — shown only once):</p>
          <code style={{ fontFamily: "monospace", fontSize: "1rem", wordBreak: "break-all" }}>{newKey}</code>
          <button
            onClick={handleCopy}
            style={{ marginLeft: "1rem", padding: "0.25rem 0.75rem", background: copied ? "#16a34a" : "#0070f3", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #eee", textAlign: "left" }}>
            <th style={{ padding: "0.5rem" }}>Label</th>
            <th style={{ padding: "0.5rem" }}>Plan</th>
            <th style={{ padding: "0.5rem" }}>Active</th>
            <th style={{ padding: "0.5rem" }}>Created</th>
            <th style={{ padding: "0.5rem" }}>Last Used</th>
          </tr>
        </thead>
        <tbody>
          {keys.map((k) => (
            <tr key={k.id} style={{ borderBottom: "1px solid #eee" }}>
              <td style={{ padding: "0.5rem" }}>{k.label}</td>
              <td style={{ padding: "0.5rem" }}>{getPlanName(k.plan_id)}</td>
              <td style={{ padding: "0.5rem" }}>{k.is_active ? "Yes" : "No"}</td>
              <td style={{ padding: "0.5rem" }}>{new Date(k.created_at).toLocaleString()}</td>
              <td style={{ padding: "0.5rem" }}>{k.last_used_at ? new Date(k.last_used_at).toLocaleString() : "Never"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Layout>
  );
}
