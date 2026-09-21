import { ApiError, getEvaluation } from "@/lib/api";
import type { RetrievalScore } from "@/lib/types";

export const dynamic = "force-dynamic";

const METHOD_LABELS: { key: "bm25" | "vector" | "rrf" | "hybrid"; name: string; note: string }[] = [
  { key: "bm25", name: "BM25 full-text", note: "keyword matching only" },
  { key: "vector", name: "pgvector semantic", note: "embedding similarity only" },
  { key: "rrf", name: "Reciprocal rank fusion", note: "both lists merged" },
  { key: "hybrid", name: "Hybrid + Cohere rerank", note: "shipped" },
];

function pct(score: RetrievalScore): number {
  return Math.round(score[0] * 100);
}

export default async function BenchmarkPage() {
  let error: string | null = null;
  let report: Awaited<ReturnType<typeof getEvaluation>> | null = null;
  try {
    report = await getEvaluation();
  } catch (e) {
    error = e instanceof ApiError ? e.message : "Could not reach the evaluation endpoint.";
  }

  if (error || !report) {
    return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
        <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 12 }}>
          <h3 style={{ margin: 0 }}>Does the occupation search actually work?</h3>
          <span className="tag tag-outline">GET /evaluate</span>
        </div>
        <p style={{ margin: "16px 0 0", fontSize: 14, color: "#f2a3a3" }}>{error}</p>
      </div>
    );
  }

  const { examples_report, mean_report } = report;
  const misses = examples_report.filter((e) => e.hybrid[1] === 0).length;
  const stats = [
    {
      label: "Correct NOC in top 10",
      value: `${Math.round(mean_report.hybrid[1] * 100)}%`,
      note: `${examples_report.length - misses} of ${examples_report.length} descriptions`,
    },
    { label: "Ranking quality", value: mean_report.hybrid[0].toFixed(3), note: "NDCG@10, shipped method" },
    {
      label: "Lift over keyword search",
      value: `${mean_report.hybrid[0] - mean_report.bm25[0] >= 0 ? "+" : ""}${(mean_report.hybrid[0] - mean_report.bm25[0]).toFixed(3)}`,
      note: "NDCG vs BM25 alone",
      color: "#b5abfc",
    },
    { label: "Misses", value: String(misses), note: "hybrid method, outside top 10" },
  ];

  const methodRows = METHOD_LABELS.map((m) => {
    const score = mean_report[m.key];
    const shipped = m.key === "hybrid";
    return {
      ...m,
      ndcg: score[0].toFixed(3),
      hit: score[1].toFixed(2),
      pctVal: pct(score),
      fg: shipped ? "#b5abfc" : "rgba(233,233,237,.72)",
      bar: shipped ? "#9184d9" : "#595d6c",
    };
  });

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 12 }}>
        <h3 style={{ margin: 0 }}>Does the occupation search actually work?</h3>
        <span className="tag tag-outline">GET /evaluate</span>
      </div>
      <p style={{ margin: "8px 0 0", maxWidth: "72ch", fontSize: 15, color: "rgba(233,233,237,.72)" }}>
        Classifying a job description into one of the NOC 2021 unit groups is the one place in MaplePath where a
        wrong answer is plausible and consequential — it decides TEER, and TEER decides program eligibility. So
        retrieval is measured, not asserted. {examples_report.length} job descriptions, hand-labelled with their
        correct NOC code, run through four retrieval methods with identical queries.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(190px,1fr))", gap: 14, marginTop: 26 }}>
        {stats.map((s) => (
          <div key={s.label} style={{ padding: "16px 18px", borderRadius: 12, background: "#161826", boxShadow: "var(--shadow-sm)" }}>
            <div style={{ fontSize: 11, letterSpacing: ".06em", textTransform: "uppercase", color: "rgba(233,233,237,.55)" }}>
              {s.label}
            </div>
            <div style={{ fontSize: 32, fontWeight: 500, marginTop: 4, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 12, color: "rgba(233,233,237,.5)" }}>{s.note}</div>
          </div>
        ))}
      </div>

      <h5 style={{ margin: "32px 0 4px" }}>Each method against the same {examples_report.length} labels</h5>
      <p style={{ margin: "0 0 16px", fontSize: 13, color: "rgba(233,233,237,.55)" }}>
        Higher NDCG@10 means the correct code sits nearer the top of the list. The shipped method is the last row.
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {methodRows.map((m) => (
          <div key={m.name} style={{ padding: "13px 0", borderTop: "1px solid rgba(233,233,237,.08)" }}>
            <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 8, fontSize: 14 }}>
              <span style={{ color: m.fg, minWidth: 190 }}>{m.name}</span>
              <span style={{ fontSize: 12, color: "rgba(233,233,237,.45)" }}>{m.note}</span>
              <span style={{ marginLeft: "auto", fontVariantNumeric: "tabular-nums", color: m.fg, width: 66, textAlign: "right" }}>
                {m.ndcg}
              </span>
              <span style={{ fontSize: 12, color: "rgba(233,233,237,.45)", width: 86, textAlign: "right" }}>hit {m.hit}</span>
            </div>
            <div style={{ marginTop: 8, height: 6, borderRadius: 3, background: "rgba(233,233,237,.1)" }}>
              <div style={{ width: `${m.pctVal}%`, height: 6, borderRadius: 3, background: m.bar }} />
            </div>
          </div>
        ))}
      </div>

      <h5 style={{ margin: "34px 0 4px" }}>Per-example report</h5>
      <p style={{ margin: "0 0 14px", fontSize: 13, color: "rgba(233,233,237,.55)" }}>
        One row per labelled description, from <code style={{ fontSize: 12 }}>examples_report</code>. NDCG and hit
        are for the shipped hybrid + rerank method.
      </p>
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
          {examples_report.map((e) => {
            const [ndcg, hit] = e.hybrid;
            const outcome = ndcg === 1 ? "Top hit" : hit === 1 ? "Top 10" : "Missed";
            const tagClass = ndcg === 1 ? "tag-accent" : hit === 1 ? "tag-outline" : "tag-neutral";
            const color = ndcg === 1 ? "#b5abfc" : hit === 1 ? "rgba(233,233,237,.82)" : "#cfd3e5";
            return (
              <tr key={`${e.job_title}-${e.case_type}`}>
                <td style={{ color: "rgba(233,233,237,.85)" }}>{e.job_title}</td>
                <td style={{ color: "rgba(233,233,237,.62)" }}>{e.case_type}</td>
                <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color }}>{ndcg.toFixed(3)}</td>
                <td>
                  <span className={`tag ${tagClass}`}>{outcome}</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p style={{ margin: "18px 0 0", fontSize: 12, color: "rgba(233,233,237,.45)", maxWidth: "74ch" }}>
        Labels live in data/noc_eval_labels.csv. This report is produced live by the /evaluate endpoint on each
        visit.
      </p>
    </div>
  );
}
