"use client";
import { SingleExampleReport } from "@/lib/types";
import { useState } from "react";

export default function EvaluationExampleTable({
  examples_report,
}: {
  examples_report: SingleExampleReport[];
}) {
  const [pageNumber, setPageNumber] = useState(1);

  // Page OFFSET constant
  const OFFSET: number = 20;

  return (
    <>
      <table className="table">
        <thead>
          <tr>
            <th>Job title</th>
            <th style={{ width: 130 }}>Case type</th>
            <th style={{ textAlign: "right", width: 78 }}>NDCG</th>
            <th style={{ width: 96 }}>Outcome</th>
          </tr>
        </thead>
        <tbody>
          {examples_report
            .slice((pageNumber - 1) * OFFSET, pageNumber * OFFSET)
            .map((e) => {
              const [ndcg, hit] = e.vector;
              const outcome =
                ndcg === 1 ? "Top hit" : hit === 1 ? "Top 10" : "Missed";
              const tagClass =
                ndcg === 1
                  ? "tag-accent"
                  : hit === 1
                    ? "tag-outline"
                    : "tag-neutral";
              const color =
                ndcg === 1
                  ? "#b5abfc"
                  : hit === 1
                    ? "rgba(233,233,237,.82)"
                    : "#cfd3e5";
              return (
                <tr key={`${e.job_title}-${e.case_type}`}>
                  <td style={{ color: "rgba(233,233,237,.85)" }}>
                    {e.job_title}
                  </td>
                  <td style={{ color: "rgba(233,233,237,.62)" }}>
                    {e.case_type}
                  </td>
                  <td
                    style={{
                      textAlign: "right",
                      fontVariantNumeric: "tabular-nums",
                      color,
                    }}
                  >
                    {ndcg.toFixed(3)}
                  </td>
                  <td>
                    <span className={`tag ${tagClass}`}>{outcome}</span>
                  </td>
                </tr>
              );
            })}
        </tbody>
      </table>
      <div className="mt-2 flex items-center justify-end gap-2 border-t border-[rgba(233,233,237,.08)] pt-3.5">
        {pageNumber > 1 && (
          <button
            type="button"
            onClick={() => {
              setPageNumber((prev) => prev - 1);
            }}
            className="h-8 cursor-pointer rounded-lg bg-[#161826] px-3 text-[13px] text-[rgba(233,233,237,.72)] shadow-[var(--shadow-sm)] transition-colors hover:text-[#b5abfc] hover:shadow-[0_0_0_1px_#9184d9] focus-visible:outline-none focus-visible:shadow-[0_0_0_1px_#b5abfc]"
          >
            ← Prev
          </button>
        )}
        <div className="flex h-8 min-w-8 items-center justify-center rounded-lg bg-[#161826] px-2.5 text-[13px] tabular-nums text-[#b5abfc] shadow-[0_0_0_1px_#9184d9]">
          {pageNumber}
        </div>
        {pageNumber < examples_report.length / OFFSET && (
          <button
            type="button"
            onClick={() => {
              setPageNumber((prev) => prev + 1);
            }}
            className="h-8 cursor-pointer rounded-lg bg-[#161826] px-3 text-[13px] text-[rgba(233,233,237,.72)] shadow-[var(--shadow-sm)] transition-colors hover:text-[#b5abfc] hover:shadow-[0_0_0_1px_#9184d9] focus-visible:outline-none focus-visible:shadow-[0_0_0_1px_#b5abfc]"
          >
            Next →
          </button>
        )}
      </div>
    </>
  );
}
