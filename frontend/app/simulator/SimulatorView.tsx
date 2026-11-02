"use client";

import { useEffect, useRef, useState } from "react";
import { simulateCrsAction } from "@/lib/actions";
import { EDUCATION_OPTIONS } from "@/lib/confirm-form";
import { CRS_TOTAL_MAX } from "@/lib/crs-maxes";
import { LATEST_DRAW } from "@/lib/latest-draw";
import { simToUserProfile, type CanStudy, type SimProfile } from "@/lib/sim-profile";
import type { CRSBreakdown, CRSScore, EducationLevel, UserProfile } from "@/lib/types";

// Waits for the slider to settle before asking the backend to rescore.
const RESCORE_DELAY_MS = 250;

const CAN_STUDY_OPTIONS: { value: CanStudy; label: string }[] = [
  { value: "none", label: "None" },
  { value: "short", label: "1-2 year credential (+15)" },
  { value: "long", label: "3+ year credential (+30)" },
];

function sameSim(a: SimProfile, b: SimProfile): boolean {
  return (Object.keys(a) as (keyof SimProfile)[]).every((k) => a[k] === b[k]);
}

export default function SimulatorView({
  profile,
  initial,
  baseline,
}: {
  profile: UserProfile;
  initial: SimProfile;
  baseline: CRSScore;
}) {
  const [sim, setSim] = useState<SimProfile>({ ...initial });
  // null while the controls match the confirmed profile - the baseline score
  // already is the backend's answer for that.
  const [scored, setScored] = useState<CRSScore | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const requestId = useRef(0);

  useEffect(() => () => clearTimeout(timer.current), []);

  // Every change is rescored by the backend's own CRS engine, so the
  // simulator can never disagree with the results page.
  const update = (next: SimProfile) => {
    setSim(next);
    clearTimeout(timer.current);
    const id = ++requestId.current;
    if (sameSim(next, initial)) {
      setScored(null);
      setError(null);
      setPending(false);
      return;
    }
    setPending(true);
    timer.current = setTimeout(async () => {
      const res = await simulateCrsAction(simToUserProfile(profile, next, initial));
      // A newer change has been made since - its request owns the result.
      if (id !== requestId.current) return;
      setPending(false);
      if ("error" in res) {
        setError(res.error);
      } else {
        setError(null);
        setScored(res.crs_score);
      }
    }, RESCORE_DELAY_MS);
  };

  const setField = <K extends keyof SimProfile>(
    key: K,
    value: SimProfile[K],
  ) => {
    update({ ...sim, [key]: value });
  };

  const now = scored ?? baseline;
  const d = now.total - baseline.total;

  const row = (label: string, key: keyof CRSBreakdown) => {
    const delta = now.breakdown[key] - baseline.breakdown[key];
    return {
      label,
      pts: now.breakdown[key],
      delta: delta === 0 ? "-" : delta > 0 ? `+${delta}` : String(delta),
      dColorClass:
        delta > 0
          ? "text-[#b5abfc]"
          : delta < 0
            ? "text-[#cfd3e5]"
            : "text-[rgba(233,233,237,.35)]",
    };
  };

  type Slider = {
    label: string;
    value: number;
    min: number;
    max: number;
    step: number;
    display: string;
    key: "age" | "canYears" | "foreignYears" | "clb" | "nclc" | "spouseLang" | "spouseCanYears";
  };
  const years = (n: number) => n + (n === 1 ? " year" : " years");

  const sliders: Slider[] = [
    {
      label: "Age",
      value: sim.age,
      min: 18,
      max: 44,
      step: 1,
      display: String(sim.age),
      key: "age",
    },
    {
      label: "Canadian work experience",
      value: sim.canYears,
      min: 0,
      max: 5,
      step: 1,
      display: years(sim.canYears),
      key: "canYears",
    },
    {
      label: "Foreign work experience",
      value: sim.foreignYears,
      min: 0,
      max: 5,
      step: 1,
      display: years(sim.foreignYears),
      key: "foreignYears",
    },
    {
      label: "English - lowest CLB across abilities",
      value: sim.clb,
      min: 0,
      max: 10,
      step: 1,
      display: sim.clb === 0 ? "no test" : "CLB " + sim.clb,
      key: "clb",
    },
    {
      label: "French - lowest NCLC across abilities",
      value: sim.nclc,
      min: 0,
      max: 10,
      step: 1,
      display: sim.nclc === 0 ? "no test" : "NCLC " + sim.nclc,
      key: "nclc",
    },
  ];

  const spouseSliders: Slider[] = [
    {
      label: "Spouse language - lowest CLB/NCLC",
      value: sim.spouseLang,
      min: 0,
      max: 10,
      step: 1,
      display: sim.spouseLang === 0 ? "no test" : "level " + sim.spouseLang,
      key: "spouseLang",
    },
    {
      label: "Spouse Canadian work experience",
      value: sim.spouseCanYears,
      min: 0,
      max: 5,
      step: 1,
      display: years(sim.spouseCanYears),
      key: "spouseCanYears",
    },
  ];

  const renderSlider = (s: Slider) => (
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
        onChange={(e) => setField(s.key, +e.target.value)}
        className="w-full"
      />
    </div>
  );

  const simRows = [
    row("Age", "age"),
    row("Education", "education"),
    row("First language", "first_language"),
    row("Second language", "second_language"),
    row("Canadian experience", "canadian_experience"),
    ...(sim.married || initial.married ? [row("Spouse factors", "spouse_total")] : []),
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
          live · same engine as your results
        </span>
      </div>
      <p className="mt-1.5 mb-6 text-[14px] text-[rgba(233,233,237,.6)]">
        Move any input and your confirmed profile is rescored by the same CRS
        engine as your results, including marital status and spouse factors.
        Anything the controls don&apos;t cover stays as you confirmed it.
      </p>
      <div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] items-start gap-5">
        <div className="flex flex-col gap-4.5 rounded-[14px] bg-[#161826] p-5 shadow-[var(--shadow-sm)]">
          <div className="field">
            <label>Marital status</label>
            <div className="seg w-full">
              <label className="seg-opt flex-1 justify-center">
                <input
                  type="radio"
                  name="sim_marital_status"
                  checked={!sim.married}
                  onChange={() => setField("married", false)}
                />
                Single
              </label>
              <label className="seg-opt flex-1 justify-center">
                <input
                  type="radio"
                  name="sim_marital_status"
                  checked={sim.married}
                  onChange={() => setField("married", true)}
                />
                Married
              </label>
            </div>
          </div>
          {sliders.map(renderSlider)}
          <div className="field">
            <label>Highest education</label>
            <select
              className="input"
              value={sim.edu}
              onChange={(e) =>
                setField("edu", e.target.value as EducationLevel)
              }
            >
              {EDUCATION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
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
          </div>
          <div className="field">
            <label>Canadian post-secondary credential</label>
            <select
              className="input"
              value={sim.canStudy}
              onChange={(e) => setField("canStudy", e.target.value as CanStudy)}
            >
              {CAN_STUDY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          {sim.married && (
            <div className="flex flex-col gap-4.5 border-t border-[rgba(233,233,237,.12)] pt-4">
              <div className="text-[10px] tracking-[.1em] text-[#9184d9] uppercase">
                Spouse or partner
              </div>
              <div className="field">
                <label>Spouse highest education</label>
                <select
                  className="input"
                  value={sim.spouseEdu}
                  onChange={(e) =>
                    setField("spouseEdu", e.target.value as EducationLevel | "none")
                  }
                >
                  <option value="none">No credential</option>
                  {EDUCATION_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              {spouseSliders.map(renderSlider)}
            </div>
          )}
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => update({ ...initial })}
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
              <span
                className={`text-[56px] leading-none font-medium tracking-[-.03em] tabular-nums transition-opacity ${pending ? "opacity-50" : ""}`}
                aria-busy={pending}
              >
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
                Confirmed profile: {baseline.total}
              </span>
              <span>Latest draw cut-off: {LATEST_DRAW.cutoff}</span>
            </div>
            <div className="mt-4 text-[13.5px] text-[rgba(233,233,237,.78)]">
              {verdict}
            </div>
            {error && (
              <p className="mt-3 mb-0 text-[13px] text-[#f2a3a3]">
                Couldn&apos;t rescore these inputs: {error}
              </p>
            )}
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
