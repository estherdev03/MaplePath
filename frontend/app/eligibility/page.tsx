import { PROGRAMS, FSW_GRID } from "@/lib/mock-data";

export default function EligibilityPage() {
  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
      <h3 style={{ margin: 0 }}>Express Entry eligibility</h3>
      <p style={{ margin: "6px 0 22px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
        Requirement-level results. A program is eligible only when every requirement is met.
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {PROGRAMS.map((p) => (
          <div
            key={p.name}
            style={{ borderRadius: 14, background: "#161826", boxShadow: `0 0 0 1px ${p.edge}`, overflow: "hidden" }}
          >
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 12, padding: "16px 20px" }}>
              <div style={{ flex: 1, minWidth: 200 }}>
                <div style={{ fontSize: 18, fontWeight: 500 }}>{p.name}</div>
                <div style={{ fontSize: 12, color: "rgba(233,233,237,.55)" }}>{p.sub}</div>
              </div>
              <span className={`tag ${p.tagClass}`}>{p.verdict}</span>
            </div>
            <div style={{ padding: "0 20px 18px", display: "flex", flexDirection: "column", gap: 1 }}>
              {p.reqs.map((r) => (
                <div
                  key={r.label}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 10,
                    padding: "9px 0",
                    borderTop: "1px solid rgba(233,233,237,.07)",
                  }}
                >
                  <span
                    style={{
                      color: r.ok ? "#b5abfc" : "rgba(233,233,237,.35)",
                      fontSize: 13,
                      width: 14,
                      flex: "none",
                      textAlign: "center",
                    }}
                  >
                    {r.ok ? "●" : "○"}
                  </span>
                  <span style={{ fontSize: 13.5, flex: 1 }}>{r.label}</span>
                  <span style={{ fontSize: 12.5, color: "rgba(233,233,237,.55)", textAlign: "right", maxWidth: "44%" }}>
                    {r.detail}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 20, borderRadius: 14, background: "#161826", boxShadow: "var(--shadow-sm)", padding: "18px 20px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 12 }}>
          <h5 style={{ margin: 0 }}>FSW selection grid — 67-point threshold</h5>
          <span className="tag tag-accent">78 / 100 · passed</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 12 }}>
          {FSW_GRID.map((g) => (
            <div key={g.label} style={{ padding: "11px 13px", borderRadius: 8, background: "#1b1e2d" }}>
              <div style={{ fontSize: 11.5, color: "rgba(233,233,237,.58)" }}>{g.label}</div>
              <div style={{ fontSize: 19, fontWeight: 500, fontVariantNumeric: "tabular-nums" }}>
                {g.val}
                <span style={{ fontSize: 12, color: "rgba(233,233,237,.45)" }}> / {g.max}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
