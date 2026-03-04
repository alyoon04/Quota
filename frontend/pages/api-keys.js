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
  const [loading, setLoading] = useState(false);

  // Filter state
  const [filterPlanId, setFilterPlanId] = useState("");

  // Toggle state
  const [togglingId, setTogglingId] = useState(null);
  const [toggleError, setToggleError] = useState("");

  // Delete confirmation state
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const loadData = async () => {
    setLoading(true);
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
    } finally {
      setLoading(false);
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
    setLoading(true);
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
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(newKey);
    setCopied(true);
  };

  const handleToggle = async (key) => {
    setTogglingId(key.id);
    setToggleError("");
    try {
      await apiFetch(`/admin/api-keys/${key.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !key.is_active }),
      });
      await loadData();
    } catch (e) {
      setToggleError(e.message);
    } finally {
      setTogglingId(null);
    }
  };

  const handleDelete = async () => {
    setDeleteError("");
    setDeleteLoading(true);
    try {
      await apiFetch(`/admin/api-keys/${confirmDeleteId}`, { method: "DELETE" });
      setConfirmDeleteId(null);
      await loadData();
    } catch (e) {
      setDeleteError(e.message);
    } finally {
      setDeleteLoading(false);
    }
  };

  const getPlanName = (id) => {
    const plan = plans.find((p) => p.id === id);
    return plan ? plan.name : id;
  };

  const keyToDelete = keys.find((k) => k.id === confirmDeleteId);
  const filteredKeys = filterPlanId ? keys.filter((k) => k.plan_id === filterPlanId) : keys;

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
            disabled={loading}
            style={{ padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          />
        </div>
        <div>
          <label style={{ display: "block", fontSize: "0.875rem", marginBottom: "0.25rem" }}>Plan</label>
          <select
            value={planId}
            onChange={(e) => setPlanId(e.target.value)}
            required
            disabled={loading}
            style={{ padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
          >
            {plans.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.default_rpm} RPM)
              </option>
            ))}
          </select>
        </div>
        <button
          type="submit"
          disabled={loading}
          style={{ padding: "0.5rem 1rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: 4, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.6 : 1 }}
        >
          {loading ? "Creating..." : "Create Key"}
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
      {toggleError && <p style={{ color: "red" }}>{toggleError}</p>}

      {/* Filter bar */}
      <div style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <label style={{ fontSize: "0.875rem" }}>Filter by plan:</label>
        <select
          value={filterPlanId}
          onChange={(e) => setFilterPlanId(e.target.value)}
          style={{ padding: "0.375rem 0.5rem", border: "1px solid #ccc", borderRadius: 4 }}
        >
          <option value="">All plans</option>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        {filterPlanId && (
          <span style={{ fontSize: "0.85rem", color: "#888" }}>
            {filteredKeys.length} key{filteredKeys.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {loading && keys.length === 0 && <p style={{ color: "#888" }}>Loading...</p>}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #eee", textAlign: "left" }}>
            <th style={{ padding: "0.5rem" }}>Label</th>
            <th style={{ padding: "0.5rem" }}>Plan</th>
            <th style={{ padding: "0.5rem" }}>Status</th>
            <th style={{ padding: "0.5rem" }}>Created</th>
            <th style={{ padding: "0.5rem" }}>Last Used</th>
            <th style={{ padding: "0.5rem" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredKeys.map((k) => (
            <tr key={k.id} style={{ borderBottom: "1px solid #eee", opacity: k.is_active ? 1 : 0.6 }}>
              <td style={{ padding: "0.5rem" }}>{k.label}</td>
              <td style={{ padding: "0.5rem" }}>{getPlanName(k.plan_id)}</td>
              <td style={{ padding: "0.5rem" }}>
                <span style={{
                  display: "inline-block",
                  padding: "0.15rem 0.5rem",
                  borderRadius: 12,
                  fontSize: "0.8rem",
                  fontWeight: "bold",
                  background: k.is_active ? "#d1fae5" : "#fee2e2",
                  color: k.is_active ? "#065f46" : "#991b1b",
                }}>
                  {k.is_active ? "Active" : "Inactive"}
                </span>
              </td>
              <td style={{ padding: "0.5rem" }}>{new Date(k.created_at).toLocaleString()}</td>
              <td style={{ padding: "0.5rem" }}>{k.last_used_at ? new Date(k.last_used_at).toLocaleString() : "Never"}</td>
              <td style={{ padding: "0.5rem", display: "flex", gap: "0.5rem" }}>
                <button
                  onClick={() => handleToggle(k)}
                  disabled={togglingId === k.id}
                  style={{
                    padding: "0.25rem 0.75rem",
                    background: k.is_active ? "#f59e0b" : "#16a34a",
                    color: "#fff",
                    border: "none",
                    borderRadius: 4,
                    cursor: togglingId === k.id ? "not-allowed" : "pointer",
                    opacity: togglingId === k.id ? 0.6 : 1,
                  }}
                >
                  {togglingId === k.id ? "..." : k.is_active ? "Deactivate" : "Activate"}
                </button>
                <button
                  onClick={() => { setConfirmDeleteId(k.id); setDeleteError(""); }}
                  style={{ padding: "0.25rem 0.75rem", background: "#ff4444", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Delete confirmation dialog */}
      {confirmDeleteId && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100,
        }}>
          <div style={{ background: "#fff", borderRadius: 8, padding: "2rem", maxWidth: 400, width: "100%", boxShadow: "0 4px 24px rgba(0,0,0,0.15)" }}>
            <h3 style={{ marginTop: 0 }}>Delete API key?</h3>
            <p>
              Are you sure you want to delete <strong>{keyToDelete?.label}</strong>?
              This action cannot be undone.
            </p>
            {deleteError && <p style={{ color: "red", fontSize: "0.9rem" }}>{deleteError}</p>}
            <div style={{ display: "flex", gap: "0.75rem", justifyContent: "flex-end", marginTop: "1.5rem" }}>
              <button
                onClick={() => { setConfirmDeleteId(null); setDeleteError(""); }}
                disabled={deleteLoading}
                style={{ padding: "0.5rem 1rem", background: "#eee", color: "#333", border: "none", borderRadius: 4, cursor: "pointer" }}
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleteLoading}
                style={{ padding: "0.5rem 1rem", background: "#ff4444", color: "#fff", border: "none", borderRadius: 4, cursor: deleteLoading ? "not-allowed" : "pointer", opacity: deleteLoading ? 0.6 : 1 }}
              >
                {deleteLoading ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
