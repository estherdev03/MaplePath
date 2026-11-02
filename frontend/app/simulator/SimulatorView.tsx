"use client";

import { useState } from "react";
import {
  EDU_LABEL,
  calculateCrs,
  type EducationLevel,
  type SimProfile,
} from "@/lib/crs";
import { CRS_TOTAL_MAX } from "@/lib/crs-maxes";
import { LATEST_DRAW } from "@/lib/latest-draw";

const EDU_OPTIONS: EducationLevel[] = [
  "secondary",
  "one_year",
  "two_year",
  "bachelor",
  "two_or_more_credentials",
  "masters",
  "phd",
];


export default function SimulatorView({
  initial,
  confirmedTotal,
}: {
  initial: SimProfile;
  confirmedTotal: number | null;
}) {
  const [sim, setSim] = useState<SimProfile>({ ...initial });

  const setField = <K extends keyof SimProfile>(
    key: K,
    value: SimProfile[K],
  ) => {
    setSim((s) => ({ ...s, [key]: value }));
  };

  const now = calculateCrs(sim);
  const base = calculateCrs(initial);
  const d = now.total - base.total;

  const row = (label: string, key: keyof typeof now) => {
    const delta = now[key] - base[key];
    return {
      label,
      pts: now[key],
      delta: delta === 0 ? "-" : delta > 0 ? `+${delta}` : String(delta),
      dColorClass:
        delta > 0
          ? "text-[#b5abfc]"
          : delta < 0
            ? "text-[#cfd3e5]"
            : "text-[rgba(233,233,237,.35)]",
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
    {
      label: "Age",
      value: sim.age,
      min: 18,
      max: 44,
      step: 1,
      display: String(sim.age),
      onInput: (v) => setField("age", v),
    },
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
      label: "English - lowest CLB across abilities",
      value: sim.clb,
      min: 0,
      max: 10,
      step: 1,
      display: sim.clb === 0 ? "no test" : "CLB " + sim.clb,
      onInput: (v) => setField("clb", v),
    },
    {
      label: "French - lowest NCLC across abilities",
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

  const simPct = Math.min(100, (now.total / CRS_TOTAL_MAX) * 100);
  const deltaLabel =
    d === 0
      ? "unchanged"
      : d > 0
        ? `+${d} vs your inputs`
        : `${d} vs your inputs`;
  const deltaColorClass =
    d > 0
      ? "text-[#b5abfc]"
      : d < 0
        ? "text-[#cfd3e5]"
        : "text-[rgba(233,233,237,.5)]";
  const drawLabel = `the latest draw (${LATEST_DRAW.stream.toLowerCase()}, ${LATEST_DRAW.date})`;
  const verdict =
    now.total >= LATEST_DRAW.cutoff
      ? `Above the cut-off of ${drawLabel} by ${now.total - LATEST_DRAW.cutoff} points. It was a category-based draw, so an invitation also required eligibility for that category.`
      : `Below the cut-off of ${drawLabel} by ${LATEST_DRAW.cutoff - now.total} points. This score would not have been invited in that round.`;

  return (
    <div className="mx-auto max-w-[1040px] px-[26px] pt-[34px] pb-20">
      <div className="flex flex-wrap items-baseline gap-3">
        <h3 className="m-0">Score simulator</h3>
        <span className="tag tag-outline">
          live · same tables as the scorer
        </span>
      </div>
      <p className="mt-1.5 mb-6 text-[14px] text-[rgba(233,233,237,.6)]">
        Move any input and the CRS recomputes from the published point tables -
        age, education, CLB/NCLC, Canadian experience, transferability tiers and
        the 600-point additional cap. This simplified model covers a single
        applicant&apos;s core and additional points. It does not model spouse or
        arranged-employment factors.
      </p>
      <div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] items-start gap-5">
        <div className="flex flex-col gap-4.5 rounded-[14px] bg-[#161826] p-5 shadow-[var(--shadow-sm)]">
          {sliders.map((s) => (
            <div key={s.label}>
              <div className="mb-[7px] flex justify-between text-[12.5px]">
                <span className="text-[rgba(233,233,237,.7)]">{s.label}</span>
                <span className="font-medium">{s.display}</span>
              </div>
              <input
                type="range"
                min={s.min}
                max={s.max}
                step={s.step}
                value={s.value}
                onChange={(e) => s.onInput(+e.target.value)}
                className="w-full"
              />
            </div>
          ))}
          <div className="field">
            <label>Highest education</label>
            <select
              className="input"
              value={sim.edu}
              onChange={(e) =>
                setField("edu", e.target.value as EducationLevel)
              }
            >
              {EDU_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {EDU_LABEL[opt]}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-2.5">
            <label className="radio">
              <input
                type="checkbox"
                checked={sim.pnp}
                onChange={(e) => setField("pnp", e.target.checked)}
              />
              <span className="dot" />
              Provincial nomination (+600)
            </label>
            <label className="radio">
              <input
                type="checkbox"
                checked={sim.sibling}
                onChange={(e) => setField("sibling", e.target.checked)}
              />
              <span className="dot" />
              Sibling in Canada (+15)
            </label>
            <label className="radio">
              <input
                type="checkbox"
                checked={sim.canStudy}
                onChange={(e) => setField("canStudy", e.target.checked)}
              />
              <span className="dot" />
              Canadian post-secondary credential, 3+ years (+30)
            </label>
          </div>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setSim({ ...initial })}
          >
            Reset to your confirmed inputs
          </button>
        </div>
        <div className="flex flex-col gap-3.5">
          <div className="rounded-[14px] bg-[radial-gradient(120%_90%_at_50%_0%,#2b2741,#161826_72%)] p-5 shadow-[var(--shadow-sm)]">
            <div className="text-[10px] tracking-[.1em] text-[#9184d9] uppercase">
              Simulated CRS
            </div>
            <div className="mt-1.5 flex items-baseline gap-3">
              <span className="text-[56px] leading-none font-medium tracking-[-.03em] tabular-nums">
                {now.total}
              </span>
              <span className={`text-[15px] font-medium ${deltaColorClass}`}>
                {deltaLabel}
              </span>
            </div>
            <div className="relative mt-4 h-2.5 overflow-visible rounded-[5px] bg-[rgba(233,233,237,.1)]">
              <div
                className="absolute inset-y-0 right-auto left-0 rounded-[5px] bg-[#9184d9]"
                style={{ width: `${simPct}%` }}
              />
              <div
                className="absolute -top-[5px] -bottom-[5px] w-px bg-[#e9e9ed]"
                style={{ left: `${(LATEST_DRAW.cutoff / CRS_TOTAL_MAX) * 100}%` }}
              />
            </div>
            <div className="mt-2 flex justify-between text-[11.5px] text-[rgba(233,233,237,.55)]">
              <span>
                {confirmedTotal != null
                  ? `Confirmed profile: ${confirmedTotal}`
                  : "No profile confirmed yet"}
              </span>
              <span>Latest draw cut-off: {LATEST_DRAW.cutoff}</span>
            </div>
            <div className="mt-4 text-[13.5px] text-[rgba(233,233,237,.78)]">
              {verdict}
            </div>
          </div>
          <div className="rounded-[14px] bg-[#161826] px-4 pt-1.5 pb-3 shadow-[var(--shadow-sm)]">
            <table className="table">
              <tbody>
                {simRows.map((r) => (
                  <tr key={r.label}>
                    <td className="text-[13px]">{r.label}</td>
                    <td className="w-[70px] text-right tabular-nums">
                      {r.pts}
                    </td>
                    <td className={`w-14 text-right text-[12px] ${r.dColorClass}`}>
                      {r.delta}
                    </td>
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
