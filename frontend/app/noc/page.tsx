"use client";

import Link from "next/link";
import { useDevPanel } from "@/components/DevPanelContext";
import { CANDIDATES } from "@/lib/mock-data";

export default function NocPage() {
  const { toggleDev } = useDevPanel();

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 20, alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#9184d9", marginBottom: 8 }}>
            Occupation match
          </div>
          <h3 style={{ margin: 0 }}>21232 · Software developers and programmers</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 }}>
            <span className="tag tag-outline">TEER 1</span>
            <span className="tag tag-neutral">Major group 21</span>
            <span className="tag tag-neutral">Sub-major 212</span>
            <span className="tag tag-neutral">Minor group 2123</span>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(233,233,237,.6)" }}>
            Confidence
          </div>
          <div style={{ fontSize: 34, fontWeight: 500 }}>0.92</div>
          <div style={{ width: 130, height: 5, borderRadius: 3, background: "rgba(233,233,237,.1)", marginTop: 4 }}>
            <div style={{ width: "92%", height: 5, borderRadius: 3, background: "#9184d9" }} />
          </div>
        </div>
      </div>
      <p style={{ margin: "18px 0 0", fontSize: 14, color: "rgba(233,233,237,.75)", maxWidth: "74ch" }}>
        Chosen because the stated duties — designing REST services, data models and deployment pipelines — map onto
        this unit group&apos;s main duties for writing, modifying and testing code, while the lead-and-plan duties
        that would push toward 20012 are absent.
      </p>
      <div style={{ margin: "26px 0 12px", display: "flex", alignItems: "baseline", gap: 10 }}>
        <h5 style={{ margin: 0 }}>Retrieved candidates</h5>
        <span style={{ fontSize: 12, color: "rgba(233,233,237,.5)" }}>
          BM25 + pgvector, fused by RRF, reranked by Cohere — the model could only choose from these six
        </span>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th style={{ width: 74 }}>NOC</th>
            <th>Title</th>
            <th style={{ textAlign: "right", width: 70 }}>BM25</th>
            <th style={{ textAlign: "right", width: 76 }}>Vector</th>
            <th style={{ textAlign: "right", width: 70 }}>RRF</th>
            <th style={{ textAlign: "right", width: 84 }}>Rerank</th>
            <th style={{ width: 88 }}>Outcome</th>
          </tr>
        </thead>
        <tbody>
          {CANDIDATES.map((c) => (
            <tr key={c.code}>
              <td style={{ fontVariantNumeric: "tabular-nums", color: c.color }}>{c.code}</td>
              <td style={{ color: c.color }}>{c.title}</td>
              <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: "rgba(233,233,237,.6)" }}>
                {c.bm25}
              </td>
              <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: "rgba(233,233,237,.6)" }}>
                {c.vec}
              </td>
              <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: "rgba(233,233,237,.6)" }}>
                {c.rrf}
              </td>
              <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{c.rerank}</td>
              <td>
                <span className={`tag ${c.tagClass}`}>{c.outcome}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 22 }}>
        <button type="button" className="btn btn-secondary">
          This is not my occupation
        </button>
        <button type="button" className="btn btn-ghost" onClick={toggleDev}>
          Inspect this retrieval run ↗
        </button>
        <Link href="/benchmark" className="btn btn-ghost">
          How accurate is this search? ↗
        </Link>
      </div>
    </div>
  );
}
