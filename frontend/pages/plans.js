import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiFetch } from "../lib/api";

export default function Plans() {
  const [plans, setPlans] = useState([]);
  const [name, setName] = useState("");
  const [rpm, setRpm] = useState("");
  const [error, setError] = useState("");

  const loadPlans = async () => {
    try {
      const data = await apiFetch("/admin/plans");
      setPlans(data);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadPlans();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await apiFetch("/admin/plans", {
        method: "POST",
        body: JSON.stringify({ name, default_rpm: parseInt(rpm, 10) }),
      });
      setName("");
      setRpm("");
      await loadPlans();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <Layout>
      <h2>Plans</h2>

      <form onSubmit={handleCreate} style={{ marginBottom: "2rem", display: "flex", gap: "0.5rem", alignItems: "flex-end" }}>
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", marginBottom: "0.25rem" }}>Name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", marginBottom: "0.25rem" }}>RPM</label>
          <input
            type="number"
            value={rpm}
            onChange={(e) => setRpm(e.target.value)}
            required
            min="1"
            style={{ padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4, width: 80 }}
          />
        </div>
        <button type="submit" style={{ padding: "0.5rem 1rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
          Create Plan
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #eee", textAlign: "left" }}>
            <th style={{ padding: "0.5rem" }}>Name</th>
            <th style={{ padding: "0.5rem" }}>RPM</th>
            <th style={{ padding: "0.5rem" }}>ID</th>
            <th style={{ padding: "0.5rem" }}>Created</th>
          </tr>
        </thead>
        <tbody>
          {plans.map((p) => (
            <tr key={p.id} style={{ borderBottom: "1px solid #eee" }}>
              <td style={{ padding: "0.5rem" }}>{p.name}</td>
              <td style={{ padding: "0.5rem" }}>{p.default_rpm}</td>
              <td style={{ padding: "0.5rem", fontFamily: "monospace", fontSize: "0.8rem" }}>{p.id}</td>
              <td style={{ padding: "0.5rem" }}>{new Date(p.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Layout>
  );
}
