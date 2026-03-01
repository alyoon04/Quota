import { useState, useEffect } from "react";
import Layout from "../components/Layout";
import { apiFetch } from "../lib/api";

export default function Plans() {
  const [plans, setPlans] = useState([]);
  const [name, setName] = useState("");
  const [rpm, setRpm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Inline edit state
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editRpm, setEditRpm] = useState("");
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState("");

  // Delete confirmation state
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const loadPlans = async () => {
    setLoading(true);
    try {
      const data = await apiFetch("/admin/plans");
      setPlans(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlans();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
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
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (plan) => {
    setEditingId(plan.id);
    setEditName(plan.name);
    setEditRpm(String(plan.default_rpm));
    setEditError("");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditError("");
  };

  const handleEdit = async (planId) => {
    setEditError("");
    setEditLoading(true);
    try {
      await apiFetch(`/admin/plans/${planId}`, {
        method: "PATCH",
        body: JSON.stringify({ name: editName, default_rpm: parseInt(editRpm, 10) }),
      });
      setEditingId(null);
      await loadPlans();
    } catch (e) {
      setEditError(e.message);
    } finally {
      setEditLoading(false);
    }
  };

  const handleDelete = async () => {
    setDeleteError("");
    setDeleteLoading(true);
    try {
      await apiFetch(`/admin/plans/${confirmDeleteId}`, { method: "DELETE" });
      setConfirmDeleteId(null);
      await loadPlans();
    } catch (e) {
      setDeleteError(e.message);
    } finally {
      setDeleteLoading(false);
    }
  };

  const planToDelete = plans.find((p) => p.id === confirmDeleteId);

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
            disabled={loading}
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
            disabled={loading}
            style={{ padding: "0.5rem", border: "1px solid #ccc", borderRadius: 4, width: 80 }}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          style={{ padding: "0.5rem 1rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: 4, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.6 : 1 }}
        >
          {loading ? "Creating..." : "Create Plan"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {loading && plans.length === 0 && <p style={{ color: "#888" }}>Loading...</p>}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #eee", textAlign: "left" }}>
            <th style={{ padding: "0.5rem" }}>Name</th>
            <th style={{ padding: "0.5rem" }}>RPM</th>
            <th style={{ padding: "0.5rem" }}>Keys</th>
            <th style={{ padding: "0.5rem" }}>ID</th>
            <th style={{ padding: "0.5rem" }}>Created</th>
            <th style={{ padding: "0.5rem" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {plans.map((p) =>
            editingId === p.id ? (
              <tr key={p.id} style={{ borderBottom: "1px solid #eee", background: "#f9f9f9" }}>
                <td style={{ padding: "0.5rem" }}>
                  <input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    disabled={editLoading}
                    style={{ padding: "0.375rem", border: "1px solid #ccc", borderRadius: 4, width: "100%" }}
                  />
                </td>
                <td style={{ padding: "0.5rem" }}>
                  <input
                    type="number"
                    value={editRpm}
                    onChange={(e) => setEditRpm(e.target.value)}
                    min="1"
                    disabled={editLoading}
                    style={{ padding: "0.375rem", border: "1px solid #ccc", borderRadius: 4, width: 80 }}
                  />
                </td>
                <td style={{ padding: "0.5rem" }}>{p.key_count}</td>
                <td style={{ padding: "0.5rem", fontFamily: "monospace", fontSize: "0.8rem" }}>{p.id}</td>
                <td style={{ padding: "0.5rem" }}>{new Date(p.created_at).toLocaleString()}</td>
                <td style={{ padding: "0.5rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  <button
                    onClick={() => handleEdit(p.id)}
                    disabled={editLoading || !editName || !editRpm}
                    style={{ padding: "0.25rem 0.75rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", opacity: editLoading ? 0.6 : 1 }}
                  >
                    {editLoading ? "Saving..." : "Save"}
                  </button>
                  <button
                    onClick={cancelEdit}
                    disabled={editLoading}
                    style={{ padding: "0.25rem 0.75rem", background: "#eee", color: "#333", border: "none", borderRadius: 4, cursor: "pointer" }}
                  >
                    Cancel
                  </button>
                  {editError && <span style={{ color: "red", fontSize: "0.85rem" }}>{editError}</span>}
                </td>
              </tr>
            ) : (
              <tr key={p.id} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "0.5rem" }}>{p.name}</td>
                <td style={{ padding: "0.5rem" }}>{p.default_rpm}</td>
                <td style={{ padding: "0.5rem" }}>{p.key_count}</td>
                <td style={{ padding: "0.5rem", fontFamily: "monospace", fontSize: "0.8rem" }}>{p.id}</td>
                <td style={{ padding: "0.5rem" }}>{new Date(p.created_at).toLocaleString()}</td>
                <td style={{ padding: "0.5rem", display: "flex", gap: "0.5rem" }}>
                  <button
                    onClick={() => startEdit(p)}
                    style={{ padding: "0.25rem 0.75rem", background: "#eee", color: "#333", border: "none", borderRadius: 4, cursor: "pointer" }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => { setConfirmDeleteId(p.id); setDeleteError(""); }}
                    style={{ padding: "0.25rem 0.75rem", background: "#ff4444", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>

      {/* Delete confirmation dialog */}
      {confirmDeleteId && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100,
        }}>
          <div style={{ background: "#fff", borderRadius: 8, padding: "2rem", maxWidth: 400, width: "100%", boxShadow: "0 4px 24px rgba(0,0,0,0.15)" }}>
            <h3 style={{ marginTop: 0 }}>Delete plan?</h3>
            <p>
              Are you sure you want to delete <strong>{planToDelete?.name}</strong>?
            </p>
            {planToDelete?.key_count > 0 && (
              <p style={{ color: "#e67e00", background: "#fff8e1", padding: "0.5rem 0.75rem", borderRadius: 4, fontSize: "0.9rem" }}>
                This plan has {planToDelete.key_count} API key{planToDelete.key_count !== 1 ? "s" : ""}. Delete or reassign them first.
              </p>
            )}
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
                disabled={deleteLoading || planToDelete?.key_count > 0}
                style={{ padding: "0.5rem 1rem", background: "#ff4444", color: "#fff", border: "none", borderRadius: 4, cursor: deleteLoading || planToDelete?.key_count > 0 ? "not-allowed" : "pointer", opacity: deleteLoading || planToDelete?.key_count > 0 ? 0.6 : 1 }}
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
