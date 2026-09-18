import Link from "next/link";
import { CRS_ROWS } from "@/lib/mock-data";

export default function ResultsPage() {
  const segments = [
    { width: "11.25%", color: "#9184d9" },
    { width: "10.33%", color: "#5d5294" },
    { width: "9.17%", color: "#796cbf" },
    { width: "8.33%", color: "#9690c9" },
    { width: "4.17%", color: "#d2cefd" },
    { width: "3.33%", color: "#423a6a" },
    { width: "1%", color: "#b5abfc" },
  ];

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px", display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-end", justifyContent: "space-between", gap: 16 }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#9184d9", marginBottom: 8 }}>
            Comprehensive Ranking System
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <span style={{ fontSize: 60, lineHeight: 1, fontWeight: 500, letterSpacing: "-.03em" }}>571</span>
            <span style={{ fontSize: 14, color: "rgba(233,233,237,.55)" }}>/ 1200 · 629 unclaimed</span>
          </div>
          <div style={{ fontSize: 13, color: "rgba(233,233,237,.6)", marginTop: 6 }}>
            15 Sep 2026 · single applicant · NOC 21232, TEER 1
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(233,233,237,.6)" }}>
            Last CEC round
          </div>
          <div style={{ fontSize: 26, fontWeight: 500 }}>521</div>
          <span className="tag tag-accent" style={{ marginTop: 6 }}>
            +50 above cut-off
          </span>
        </div>
      </div>

      <div>
        <div style={{ position: "relative", paddingTop: 26 }}>
          <div style={{ position: "absolute", left: "43.4%", top: 0, bottom: -6, width: 1, background: "#b5abfc" }} />
          <div
            style={{
              position: "absolute",
              left: "43.4%",
              top: 0,
              transform: "translateX(-50%)",
              fontSize: 10,
              letterSpacing: ".06em",
              textTransform: "uppercase",
              color: "#b5abfc",
              whiteSpace: "nowrap",
              background: "#0f111c",
              padding: "0 6px",
            }}
          >
            Cut-off 521
          </div>
          <div style={{ display: "flex", height: 34, borderRadius: 6, overflow: "hidden", background: "rgba(233,233,237,.07)" }}>
            {segments.map((s, i) => (
              <div key={i} style={{ width: s.width, background: s.color }} />
            ))}
          </div>
        </div>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Category</th>
            <th style={{ width: 150 }}>Share of maximum</th>
            <th style={{ textAlign: "right", width: 88 }}>Points</th>
            <th style={{ textAlign: "right", width: 64 }}>Max</th>
          </tr>
        </thead>
        <tbody>
          {CRS_ROWS.map((row) => (
            <tr key={row.label}>
              <td>{row.label}</td>
              <td>
                <div style={{ height: 5, borderRadius: 3, background: "rgba(233,233,237,.1)" }}>
                  <div style={{ width: `${row.pct}%`, height: 5, borderRadius: 3, background: "#9184d9" }} />
                </div>
              </td>
              <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{row.pts}</td>
              <td style={{ textAlign: "right", color: "rgba(233,233,237,.45)", fontVariantNumeric: "tabular-nums" }}>
                {row.max}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 14,
          alignItems: "center",
          padding: "16px 18px",
          borderRadius: 12,
          background: "#1b1e2d",
        }}
      >
        <div style={{ flex: 1, minWidth: 240, fontSize: 13.5, color: "rgba(233,233,237,.78)" }}>
          Largest available gain: a second year of Canadian work experience adds{" "}
          <strong style={{ color: "#e9e9ed" }}>13</strong> core points and can unlock transferability tiers.
        </div>
        <Link href="/simulator" className="btn btn-primary">
          Run the simulator
        </Link>
        <Link href="/eligibility" className="btn btn-secondary">
          Program eligibility
        </Link>
      </div>
    </div>
  );
}
