"use client";

import Link from "next/link";
import { useRequireProfile } from "@/lib/use-require-profile";
import { buildProgramViews, FSW_GRID_LABELS, FSW_GRID_MAX } from "@/lib/eligibility-view";

export default function EligibilityPage() {
  const profile = useRequireProfile();

  if (!profile) return null;

  if (!profile.eligibility) {
    return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
        <h3 style={{ margin: 0 }}>Express Entry eligibility</h3>
        <p style={{ margin: "10px 0 22px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
          Confirm your profile first — eligibility is computed once the scorer has a complete profile.
        </p>
        <Link href="/intake" className="btn btn-primary">
          Describe your situation
        </Link>
      </div>
    );
  }

  const programs = buildProgramViews(profile);
  const fsw = profile.eligibility.federal_skilled_worker?.breakdown;
  const fswGrid = fsw?.selection_factor_breakdown;

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
      <h3 style={{ margin: 0 }}>Express Entry eligibility</h3>
      <p style={{ margin: "6px 0 22px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
        Requirement-level results. A program is eligible only when every requirement is met.
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {programs.map((p) => (
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
      {fswGrid && fsw && (
        <div style={{ marginTop: 20, borderRadius: 14, background: "#161826", boxShadow: "var(--shadow-sm)", padding: "18px 20px" }}>
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 10, marginBottom: 12 }}>
            <h5 style={{ margin: 0 }}>FSW selection grid — 67-point threshold</h5>
            <span className={`tag ${fsw.selection_factor_passed ? "tag-accent" : "tag-neutral"}`}>
              {fsw.selection_factor_score} / 100 · {fsw.selection_factor_passed ? "passed" : "not passed"}
            </span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 12 }}>
            {(Object.keys(FSW_GRID_LABELS) as (keyof typeof FSW_GRID_LABELS)[]).map((key) => (
              <div key={key} style={{ padding: "11px 13px", borderRadius: 8, background: "#1b1e2d" }}>
                <div style={{ fontSize: 11.5, color: "rgba(233,233,237,.58)" }}>{FSW_GRID_LABELS[key]}</div>
                <div style={{ fontSize: 19, fontWeight: 500, fontVariantNumeric: "tabular-nums" }}>
                  {fswGrid[key]}
                  <span style={{ fontSize: 12, color: "rgba(233,233,237,.45)" }}> / {FSW_GRID_MAX[key]}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
