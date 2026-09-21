"use client";

import Link from "next/link";
import { useRequireProfile } from "@/lib/use-require-profile";
import { buildCrsRows } from "@/lib/crs-view";
import { CRS_TOTAL_MAX } from "@/lib/crs-maxes";

const SEGMENT_COLORS = ["#9184d9", "#5d5294", "#796cbf", "#9690c9", "#d2cefd", "#423a6a", "#b5abfc", "#6a5fa8", "#c4bdf0", "#332c56", "#8478c9"];
const LAST_CEC_CUTOFF = 521;

export default function ResultsPage() {
  const profile = useRequireProfile();

  if (!profile) return null;

  if (!profile.crs_score) {
    return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
        <h3 style={{ margin: 0 }}>Comprehensive Ranking System</h3>
        <p style={{ margin: "10px 0 22px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
          Confirm your profile first — the CRS score is computed once the scorer has a complete profile.
        </p>
        <Link href="/intake" className="btn btn-primary">
          Describe your situation
        </Link>
      </div>
    );
  }

  const rows = buildCrsRows(profile);
  const total = profile.crs_score.total;
  const unclaimed = Math.max(CRS_TOTAL_MAX - total, 0);
  const cutoffPct = (LAST_CEC_CUTOFF / CRS_TOTAL_MAX) * 100;
  const segments = rows
    .filter((r) => r.pts > 0)
    .map((r, i) => ({ width: `${(r.pts / CRS_TOTAL_MAX) * 100}%`, color: SEGMENT_COLORS[i % SEGMENT_COLORS.length] }));
  const updated = new Date(profile.updated_at).toLocaleDateString("en-CA", { day: "numeric", month: "short", year: "numeric" });
  const occLabel = profile.occupation?.noc_code
    ? `NOC ${profile.occupation.noc_code}${profile.occupation.teer != null ? `, TEER ${profile.occupation.teer}` : ""}`
    : "occupation not classified";

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px", display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "flex-end", justifyContent: "space-between", gap: 16 }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#9184d9", marginBottom: 8 }}>
            Comprehensive Ranking System
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
            <span style={{ fontSize: 60, lineHeight: 1, fontWeight: 500, letterSpacing: "-.03em" }}>{total}</span>
            <span style={{ fontSize: 14, color: "rgba(233,233,237,.55)" }}>
              / {CRS_TOTAL_MAX} · {unclaimed} unclaimed
            </span>
          </div>
          <div style={{ fontSize: 13, color: "rgba(233,233,237,.6)", marginTop: 6 }}>
            {updated} · {profile.marital_status ?? "unknown"} applicant · {occLabel}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(233,233,237,.6)" }}>
            Last CEC round
          </div>
          <div style={{ fontSize: 26, fontWeight: 500 }}>{LAST_CEC_CUTOFF}</div>
          <span className="tag tag-accent" style={{ marginTop: 6 }}>
            {total >= LAST_CEC_CUTOFF ? `+${total - LAST_CEC_CUTOFF} above cut-off` : `${total - LAST_CEC_CUTOFF} below cut-off`}
          </span>
        </div>
      </div>

      <div>
        <div style={{ position: "relative", paddingTop: 26 }}>
          <div style={{ position: "absolute", left: `${cutoffPct}%`, top: 0, bottom: -6, width: 1, background: "#b5abfc" }} />
          <div
            style={{
              position: "absolute",
              left: `${cutoffPct}%`,
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
            Cut-off {LAST_CEC_CUTOFF}
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
          {rows.map((row) => (
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
          See the requirement-level breakdown for each Express Entry program, or explore how specific changes would
          move your score.
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
