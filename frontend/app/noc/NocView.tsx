"use client";

import Link from "next/link";
import type { Occupation } from "@/lib/types";
import { useState } from "react";

export default function NocView({ occupation }: { occupation: Occupation }) {
  const confidence = occupation.noc_confidence ?? 0;
  const groupTags = [
    occupation.teer != null ? `TEER ${occupation.teer}` : null,
    occupation.major_group_code
      ? `Major group ${occupation.major_group_code}`
      : null,
    occupation.submajor_group_code
      ? `Sub-major ${occupation.submajor_group_code}`
      : null,
    occupation.minor_group_code
      ? `Minor group ${occupation.minor_group_code}`
      : null,
  ].filter((t): t is string => Boolean(t));

  const [page, setPage] = useState<number>(1);

  return (
    <div className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20">
      <div className="flex flex-wrap items-start justify-between gap-5">
        <div>
          <div className="mb-2 text-[10px] tracking-[.1em] text-[#9184d9] uppercase">
            Occupation match
          </div>
          <h3 className="m-0">
            {occupation.noc_code
              ? `${occupation.noc_code} · ${occupation.title}`
              : "No confident match"}
          </h3>
          <div className="mt-2.5 flex flex-wrap gap-2">
            {groupTags.length > 0 ? (
              groupTags.map((t) => (
                <span key={t} className="tag tag-outline">
                  {t}
                </span>
              ))
            ) : (
              <span className="tag tag-neutral">No classification group</span>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="text-[11px] tracking-[.08em] text-[rgba(233,233,237,.6)] uppercase">
            Confidence
          </div>
          <div className="text-[34px] font-medium">
            {confidence.toFixed(2)}
          </div>
          <div className="mt-1 h-[5px] w-[130px] rounded-[3px] bg-[rgba(233,233,237,.1)]">
            <div
              className="h-[5px] rounded-[3px] bg-[#9184d9]"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        </div>
      </div>
      {occupation.reasoning && (
        <p className="mx-0 mt-4.5 mb-0 max-w-[74ch] text-[14px] text-[rgba(233,233,237,.75)]">
          {occupation.reasoning}
        </p>
      )}
      <div className="mt-[26px] mb-3 flex items-baseline gap-2.5">
        <h5 className="m-0">Retrieved candidates</h5>
        <span className="text-[12px] text-[rgba(233,233,237,.5)]">
          Semantic search - the model could only choose a NOC code from this
          list
        </span>
      </div>
      {occupation.candidates.length > 0 ? (
        <>
          <table className="table">
            <thead>
              <tr>
                <th className="w-[74px]">NOC</th>
                <th>Title</th>
                <th className="w-[100px]">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {occupation.candidates
                .slice((page - 1) * 10, page * 10)
                .map((c) => {
                  const chosen = c.noc_code === occupation.noc_code;
                  const textClass = chosen
                    ? "text-[#e9e9ed]"
                    : "text-[rgba(233,233,237,.62)]";
                  return (
                    <tr key={c.noc_code}>
                      <td className={`tabular-nums ${textClass}`}>
                        {c.noc_code}
                      </td>
                      <td className={textClass}>
                        {c.title}
                      </td>
                      <td>
                        <span
                          className={`tag ${chosen ? "tag-accent" : "tag-neutral"}`}
                        >
                          {chosen ? "Chosen" : "Candidate"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
          <div className="mt-2 flex items-center justify-end gap-2 border-t border-[rgba(233,233,237,.08)] pt-3.5">
            {page > 1 && (
              <button
                type="button"
                onClick={() => {
                  setPage((prev) => prev - 1);
                }}
                className="h-8 cursor-pointer rounded-lg bg-[#161826] px-3 text-[13px] text-[rgba(233,233,237,.72)] shadow-[var(--shadow-sm)] transition-colors hover:text-[#b5abfc] hover:shadow-[0_0_0_1px_#9184d9] focus-visible:outline-none focus-visible:shadow-[0_0_0_1px_#b5abfc]"
              >
                ← Prev
              </button>
            )}
            <div className="flex h-8 min-w-8 items-center justify-center rounded-lg bg-[#161826] px-2.5 text-[13px] tabular-nums text-[#b5abfc] shadow-[0_0_0_1px_#9184d9]">
              {page}
            </div>
            {page < occupation.candidates.length / 10 && (
              <button
                type="button"
                onClick={() => {
                  setPage((prev) => prev + 1);
                }}
                className="h-8 cursor-pointer rounded-lg bg-[#161826] px-3 text-[13px] text-[rgba(233,233,237,.72)] shadow-[var(--shadow-sm)] transition-colors hover:text-[#b5abfc] hover:shadow-[0_0_0_1px_#9184d9] focus-visible:outline-none focus-visible:shadow-[0_0_0_1px_#b5abfc]"
              >
                Next →
              </button>
            )}
          </div>
        </>
      ) : (
        <p className="text-[13.5px] text-[rgba(233,233,237,.5)]">
          No candidates were retrieved for this profile.
        </p>
      )}
      <div className="mt-[22px] flex flex-wrap gap-2.5">
        <Link href="/benchmark" className="btn btn-ghost">
          How accurate is this search? ↗
        </Link>
      </div>
    </div>
  );
}
