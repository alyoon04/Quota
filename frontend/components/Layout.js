import Link from "next/link";
import { useRouter } from "next/router";

export default function Layout({ children }) {
  const router = useRouter();

  const linkStyle = (href) => ({
    padding: "0.5rem 1rem",
    textDecoration: "none",
    color: router.pathname === href ? "#0070f3" : "#666",
    fontWeight: router.pathname === href ? "bold" : "normal",
    borderBottom: router.pathname === href ? "2px solid #0070f3" : "2px solid transparent",
  });

  return (
    <div style={{ fontFamily: "system-ui", maxWidth: 960, margin: "0 auto", padding: "1rem" }}>
      <header style={{ borderBottom: "1px solid #eee", marginBottom: "2rem", paddingBottom: "1rem" }}>
        <h1 style={{ margin: "0 0 1rem 0", fontSize: "1.5rem" }}>Quota</h1>
        <nav style={{ display: "flex", gap: "0.5rem" }}>
          <Link href="/plans" style={linkStyle("/plans")}>Plans</Link>
          <Link href="/api-keys" style={linkStyle("/api-keys")}>API Keys</Link>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
