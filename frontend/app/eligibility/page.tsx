"use client";

import Link from "next/link";
import { useRequireProfile } from "@/lib/use-require-profile";
import { buildProgramViews, FSW_GRID_LABELS, FSW_GRID_MAX } from "@/lib/eligibility-view";

export default function EligibilityPage() {
  const profile = useRequireProfile();

  if (!profile) return null;

  if (!profile.eligibility) {
    return (
      <div className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20">
        <h3 className="m-0">Express Entry eligibility</h3>
        <p className="mt-2.5 mb-[22px] text-[14px] text-[rgba(233,233,237,.6)]">
          Confirm your profile first - eligibility is computed once the scorer has a complete profile.
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
    <div className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20">
      <h3 className="m-0">Express Entry eligibility</h3>
      <p className="mt-1.5 mb-[22px] text-[14px] text-[rgba(233,233,237,.6)]">
        Requirement-level results. A program is eligible only when every requirement is met.
      </p>
      <div className="flex flex-col gap-3.5">
        {programs.map((p) => (
          <div
            key={p.name}
            className={`overflow-hidden rounded-[14px] bg-[#161826] ${p.edgeClass}`}
          >
            <div className="flex flex-wrap items-center gap-3 px-5 py-4">
              <div className="min-w-[200px] flex-1">
                <div className="text-[18px] font-medium">{p.name}</div>
                <div className="text-[12px] text-[rgba(233,233,237,.55)]">{p.sub}</div>
              </div>
              <span className={`tag ${p.tagClass}`}>{p.verdict}</span>
            </div>
            <div className="flex flex-col gap-px px-5 pt-0 pb-4.5">
              {p.reqs.map((r) => (
                <div
                  key={r.label}
                  className="flex items-start gap-2.5 border-t border-[rgba(233,233,237,.07)] py-[9px]"
                >
                  <span
                    className={`w-3.5 flex-none text-center text-[13px] ${
                      r.ok ? "text-[#b5abfc]" : "text-[rgba(233,233,237,.35)]"
                    }`}
                  >
                    {r.ok ? "●" : "○"}
                  </span>
                  <span className="flex-1 text-[13.5px]">{r.label}</span>
                  <span className="max-w-[44%] text-right text-[12.5px] text-[rgba(233,233,237,.55)]">
                    {r.detail}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      {fswGrid && fsw && (
        <div className="mt-5 rounded-[14px] bg-[#161826] px-5 py-4.5 shadow-[var(--shadow-sm)]">
          <div className="mb-3 flex flex-wrap items-baseline gap-2.5">
            <h5 className="m-0">FSW selection grid - 67-point threshold</h5>
            <span className={`tag ${fsw.selection_factor_passed ? "tag-accent" : "tag-neutral"}`}>
              {fsw.selection_factor_score} / 100 · {fsw.selection_factor_passed ? "passed" : "not passed"}
            </span>
          </div>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-3">
            {(Object.keys(FSW_GRID_LABELS) as (keyof typeof FSW_GRID_LABELS)[]).map((key) => (
              <div key={key} className="rounded-lg bg-[#1b1e2d] px-[13px] py-[11px]">
                <div className="text-[11.5px] text-[rgba(233,233,237,.58)]">{FSW_GRID_LABELS[key]}</div>
                <div className="text-[19px] font-medium tabular-nums">
                  {fswGrid[key]}
                  <span className="text-[12px] text-[rgba(233,233,237,.45)]"> / {FSW_GRID_MAX[key]}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
