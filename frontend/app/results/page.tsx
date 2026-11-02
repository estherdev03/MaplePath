"use client";

import Link from "next/link";
import { useRequireProfile } from "@/lib/use-require-profile";
import { buildCrsRows } from "@/lib/crs-view";
import { CRS_TOTAL_MAX } from "@/lib/crs-maxes";
import { LATEST_DRAW } from "@/lib/latest-draw";

const SEGMENT_COLORS = [
  "bg-[#9184d9]",
  "bg-[#5d5294]",
  "bg-[#796cbf]",
  "bg-[#9690c9]",
  "bg-[#d2cefd]",
  "bg-[#423a6a]",
  "bg-[#b5abfc]",
  "bg-[#6a5fa8]",
  "bg-[#c4bdf0]",
  "bg-[#332c56]",
  "bg-[#8478c9]",
];

export default function ResultsPage() {
  const profile = useRequireProfile();

  if (!profile) return null;

  if (!profile.crs_score) {
    return (
      <div className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20">
        <h3 className="m-0">Comprehensive Ranking System</h3>
        <p className="mt-2.5 mb-[22px] text-[14px] text-[rgba(233,233,237,.6)]">
          Confirm your profile first — the CRS score is computed once the scorer
          has a complete profile.
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
  const cutoffPct = (LATEST_DRAW.cutoff / CRS_TOTAL_MAX) * 100;
  const segments = rows
    .filter((r) => r.pts > 0)
    .map((r, i) => ({
      width: `${(r.pts / CRS_TOTAL_MAX) * 100}%`,
      colorClass: SEGMENT_COLORS[i % SEGMENT_COLORS.length],
    }));
  const updated = new Date(profile.updated_at).toLocaleDateString("en-CA", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
  const occLabel = profile.occupation?.noc_code
    ? `NOC ${profile.occupation.noc_code}${profile.occupation.teer != null ? `, TEER ${profile.occupation.teer}` : ""}`
    : "occupation not classified";

  return (
    <div className="mx-auto flex max-w-[1000px] flex-col gap-4.5 px-[26px] pt-[34px] pb-20">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <div className="mb-2 text-[10px] tracking-[.1em] text-[#9184d9] uppercase">
            Comprehensive Ranking System
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-[60px] leading-none font-medium tracking-[-.03em]">
              {total}
            </span>
            <span className="text-[14px] text-[rgba(233,233,237,.55)]">
              / {CRS_TOTAL_MAX} · {unclaimed} unclaimed
            </span>
          </div>
          <div className="mt-1.5 text-[13px] text-[rgba(233,233,237,.6)]">
            {updated} · {profile.marital_status ?? "unknown"} applicant ·{" "}
            {occLabel}
          </div>
        </div>
        <div className="text-right">
          <div className="text-[11px] tracking-[.08em] text-[rgba(233,233,237,.6)] uppercase">
            Latest draw
          </div>
          <div className="text-[26px] font-medium">{LATEST_DRAW.cutoff}</div>
          <div className="mb-1.5 text-[12px] text-[rgba(233,233,237,.55)]">
            {LATEST_DRAW.stream} · {LATEST_DRAW.date}
          </div>
          <span className="tag tag-accent">
            {total >= LATEST_DRAW.cutoff
              ? `+${total - LATEST_DRAW.cutoff} above cut-off`
              : `${total - LATEST_DRAW.cutoff} below cut-off`}
          </span>
        </div>
      </div>

      <div>
        <div className="relative pt-[26px]">
          <div
            className="absolute top-0 -bottom-1.5 w-px bg-[#b5abfc]"
            style={{ left: `${cutoffPct}%` }}
          />
          <div
            className="absolute top-0 -translate-x-1/2 bg-[#0f111c] px-1.5 text-[10px] tracking-[.06em] whitespace-nowrap text-[#b5abfc] uppercase"
            style={{ left: `${cutoffPct}%` }}
          >
            Cut-off {LATEST_DRAW.cutoff}
          </div>
          <div className="flex h-[34px] overflow-hidden rounded-md bg-[rgba(233,233,237,.07)]">
            {segments.map((s, i) => (
              <div
                key={i}
                className={s.colorClass}
                style={{ width: s.width }}
              />
            ))}
          </div>
        </div>
        <p className="mt-3 mb-0 text-[12px] text-[rgba(233,233,237,.5)]">
          Cut-off from Express Entry round #{LATEST_DRAW.round} on{" "}
          {LATEST_DRAW.date}: a category-based draw for{" "}
          {LATEST_DRAW.stream.toLowerCase()} that issued{" "}
          {LATEST_DRAW.invitations} invitations. Category-based draws only
          invite candidates eligible for that category, so treat this score as
          a reference point rather than the threshold for your profile.
        </p>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Category</th>
            <th className="w-[150px]">Share of maximum</th>
            <th className="w-[88px] text-right">Points</th>
            <th className="w-16 text-right">Max</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td>{row.label}</td>
              <td>
                <div className="h-[5px] rounded-[3px] bg-[rgba(233,233,237,.1)]">
                  <div
                    className="h-[5px] rounded-[3px] bg-[#9184d9]"
                    style={{ width: `${row.pct}%` }}
                  />
                </div>
              </td>
              <td className="text-right tabular-nums">{row.pts}</td>
              <td className="text-right text-[rgba(233,233,237,.45)] tabular-nums">
                {row.max}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex flex-wrap items-center gap-3.5 rounded-xl bg-[#1b1e2d] px-4.5 py-4">
        <div className="min-w-[240px] flex-1 text-[13.5px] text-[rgba(233,233,237,.78)]">
          See the requirement-level breakdown for each Express Entry program, or
          explore how specific changes would move your score.
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
