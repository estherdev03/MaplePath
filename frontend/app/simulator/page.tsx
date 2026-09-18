"use client";

import { useState } from "react";
import {
  BASE_PROFILE,
  EDU_LABEL,
  calculateCrs,
  type EducationLevel,
  type SimProfile,
} from "@/lib/crs";

const EDU_OPTIONS: EducationLevel[] = [
  "secondary",
  "one_year",
  "two_year",
  "bachelor",
  "two_or_more_credentials",
  "masters",
  "phd",
];

export default function SimulatorPage() {
  const [sim, setSim] = useState<SimProfile>({ ...BASE_PROFILE });

  const setField = <K extends keyof SimProfile>(key: K, value: SimProfile[K]) => {
    setSim((s) => ({ ...s, [key]: value }));
  };

  const now = calculateCrs(sim);
  const base = calculateCrs(BASE_PROFILE);
  const d = now.total - base.total;

  const row = (label: string, key: keyof typeof now) => {
    const delta = now[key] - base[key];
    return {
      label,
      pts: now[key],
      delta: delta === 0 ? "—" : delta > 0 ? `+${delta}` : String(delta),
      dColor: delta > 0 ? "#b5abfc" : delta < 0 ? "#cfd3e5" : "rgba(233,233,237,.35)",
    };
  };

  const sliders: {
    label: string;
    value: number;
    min: number;
    max: number;
    step: number;
    display: string;
    onInput: (v: number) => void;
  }[] = [
    { label: "Age", value: sim.age, min: 18, max: 44, step: 1, display: String(sim.age), onInput: (v) => setField("age", v) },
    {
      label: "Canadian work experience",
      value: sim.canYears,
      min: 0,
      max: 5,
      step: 1,
      display: sim.canYears + (sim.canYears === 1 ? " year" : " years"),
      onInput: (v) => setField("canYears", v),
    },
    {
      label: "Foreign work experience",
      value: sim.foreignYears,
      min: 0,
      max: 5,
      step: 1,
      display: sim.foreignYears + (sim.foreignYears === 1 ? " year" : " years"),
      onInput: (v) => setField("foreignYears", v),
    },
    {
      label: "English — lowest CLB across abilities",
      value: sim.clb,
      min: 4,
      max: 10,
      step: 1,
      display: "CLB " + sim.clb,
      onInput: (v) => setField("clb", v),
    },
    {
      label: "French — lowest NCLC across abilities",
      value: sim.nclc,
      min: 0,
      max: 10,
      step: 1,
      display: sim.nclc === 0 ? "no test" : "NCLC " + sim.nclc,
      onInput: (v) => setField("nclc", v),
    },
  ];

  const simRows = [
    row("Age", "age"),
    row("Education", "education"),
    row("First language", "first"),
    row("Second language", "second"),
    row("Canadian experience", "canadian_experience"),
    row("Skill transferability", "skill_transferability"),
    row("French bonus", "french_bonus"),
    row("Provincial nomination", "provincial_nomination"),
    row("Sibling in Canada", "sibling_in_canada"),
    row("Canadian study", "canadian_study"),
  ];

  const simPct = Math.min(100, (now.total / 1200) * 100);
  const deltaLabel = d === 0 ? "unchanged" : d > 0 ? `+${d} vs confirmed` : `${d} vs confirmed`;
  const deltaColor = d > 0 ? "#b5abfc" : d < 0 ? "#cfd3e5" : "rgba(233,233,237,.5)";
  const verdict =
    now.total >= 521
      ? `Above the last CEC cut-off by ${now.total - 521} points. A profile at this score would have been invited in the most recent round.`
      : `Below the last CEC cut-off by ${521 - now.total} points. This score would not have been invited in the most recent round.`;

  return (
    <div style={{ maxWidth: 1040, margin: "0 auto", padding: "34px 26px 80px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 12 }}>
        <h3 style={{ margin: 0 }}>Score simulator</h3>
        <span className="tag tag-outline">live · same tables as the scorer</span>
      </div>
      <p style={{ margin: "6px 0 24px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
        Move any input and the CRS recomputes from the published point tables — age, education, CLB/NCLC, Canadian
        experience, transferability tiers and the 600-point additional cap.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(300px,1fr))", gap: 20, alignItems: "start" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 18, padding: 20, borderRadius: 14, background: "#161826", boxShadow: "var(--shadow-sm)" }}>
          {sliders.map((s) => (
            <div key={s.label}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12.5, marginBottom: 7 }}>
                <span style={{ color: "rgba(233,233,237,.7)" }}>{s.label}</span>
                <span style={{ fontWeight: 500 }}>{s.display}</span>
              </div>
              <input
                type="range"
                min={s.min}
                max={s.max}
                step={s.step}
                value={s.value}
                onChange={(e) => s.onInput(+e.target.value)}
                style={{ width: "100%" }}
              />
            </div>
          ))}
          <div className="field">
            <label>Highest education</label>
            <select
              className="input"
              value={sim.edu}
              onChange={(e) => setField("edu", e.target.value as EducationLevel)}
            >
              {EDU_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {EDU_LABEL[opt]}
                </option>
              ))}
            </select>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <label className="radio">
              <input type="checkbox" checked={sim.pnp} onChange={(e) => setField("pnp", e.target.checked)} />
              <span className="dot" />
              Provincial nomination (+600)
            </label>
            <label className="radio">
              <input type="checkbox" checked={sim.sibling} onChange={(e) => setField("sibling", e.target.checked)} />
              <span className="dot" />
              Sibling in Canada (+15)
            </label>
            <label className="radio">
              <input type="checkbox" checked={sim.canStudy} onChange={(e) => setField("canStudy", e.target.checked)} />
              <span className="dot" />
              Canadian post-secondary credential, 2+ years (+30)
            </label>
          </div>
          <button type="button" className="btn btn-secondary" onClick={() => setSim({ ...BASE_PROFILE })}>
            Reset to the confirmed profile
          </button>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div
            style={{
              padding: 20,
              borderRadius: 14,
              background: "radial-gradient(120% 90% at 50% 0%,#2b2741,#161826 72%)",
              boxShadow: "var(--shadow-sm)",
            }}
          >
            <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#9184d9" }}>
              Simulated CRS
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 6 }}>
              <span style={{ fontSize: 56, lineHeight: 1, fontWeight: 500, letterSpacing: "-.03em", fontVariantNumeric: "tabular-nums" }}>
                {now.total}
              </span>
              <span style={{ fontSize: 15, fontWeight: 500, color: deltaColor }}>{deltaLabel}</span>
            </div>
            <div style={{ marginTop: 16, position: "relative", height: 10, borderRadius: 5, background: "rgba(233,233,237,.1)", overflow: "visible" }}>
              <div style={{ position: "absolute", inset: "0 auto 0 0", width: `${simPct}%`, background: "#9184d9", borderRadius: 5 }} />
              <div style={{ position: "absolute", left: "43.4%", top: -5, bottom: -5, width: 1, background: "#e9e9ed" }} />
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8, fontSize: 11.5, color: "rgba(233,233,237,.55)" }}>
              <span>Confirmed profile: 571</span>
              <span>Last CEC cut-off: 521</span>
            </div>
            <div style={{ marginTop: 16, fontSize: 13.5, color: "rgba(233,233,237,.78)" }}>{verdict}</div>
          </div>
          <div style={{ padding: "6px 16px 12px", borderRadius: 14, background: "#161826", boxShadow: "var(--shadow-sm)" }}>
            <table className="table">
              <tbody>
                {simRows.map((r) => (
                  <tr key={r.label}>
                    <td style={{ fontSize: 13 }}>{r.label}</td>
                    <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", width: 70 }}>{r.pts}</td>
                    <td style={{ textAlign: "right", width: 56, fontSize: 12, color: r.dColor }}>{r.delta}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
