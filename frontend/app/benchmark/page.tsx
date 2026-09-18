import { EVAL_METHODS, EVAL_EXAMPLES } from "@/lib/mock-data";

export default function BenchmarkPage() {
  const stats = [
    { label: "Correct NOC in top 10", value: "94%", note: "79 of 84 descriptions" },
    { label: "Ranking quality", value: "0.781", note: "NDCG@10, shipped method" },
    { label: "Lift over keyword search", value: "+0.169", note: "NDCG vs BM25 alone", color: "#b5abfc" },
    { label: "Misses", value: "5", note: "all TEER-boundary titles" },
  ];

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 12 }}>
        <h3 style={{ margin: 0 }}>Does the occupation search actually work?</h3>
        <span className="tag tag-outline">GET /evaluate</span>
      </div>
      <p style={{ margin: "8px 0 0", maxWidth: "72ch", fontSize: 15, color: "rgba(233,233,237,.72)" }}>
        Classifying a job description into one of 516 NOC unit groups is the one place in MaplePath where a wrong
        answer is plausible and consequential — it decides TEER, and TEER decides program eligibility. So retrieval
        is measured, not asserted. Eighty-four job descriptions were hand-labelled with their correct NOC code, then
        run through four retrieval methods with identical queries.
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

      <h5 style={{ margin: "32px 0 4px" }}>Each method against the same 84 labels</h5>
      <p style={{ margin: "0 0 16px", fontSize: 13, color: "rgba(233,233,237,.55)" }}>
        Higher NDCG@10 means the correct code sits nearer the top of the list. The shipped method is the last row.
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {EVAL_METHODS.map((m) => (
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
              <div style={{ width: `${m.pct}%`, height: 6, borderRadius: 3, background: m.bar }} />
            </div>
          </div>
        ))}
      </div>

      <h5 style={{ margin: "34px 0 4px" }}>Per-example report</h5>
      <p style={{ margin: "0 0 14px", fontSize: 13, color: "rgba(233,233,237,.55)" }}>
        One row per labelled description, from <code style={{ fontSize: 12 }}>examples_report</code>. Rank is where
        the correct NOC landed under hybrid + rerank — a dash means it fell outside the top ten.
      </p>
      <table className="table">
        <thead>
          <tr>
            <th>Labelled job description</th>
            <th style={{ width: 78 }}>Gold NOC</th>
            <th style={{ textAlign: "right", width: 64 }}>Rank</th>
            <th style={{ textAlign: "right", width: 78 }}>NDCG</th>
            <th style={{ width: 96 }}>Outcome</th>
          </tr>
        </thead>
        <tbody>
          {EVAL_EXAMPLES.map((e) => (
            <tr key={e.query}>
              <td style={{ color: "rgba(233,233,237,.85)" }}>{e.query}</td>
              <td style={{ fontVariantNumeric: "tabular-nums", color: "rgba(233,233,237,.62)" }}>{e.gold}</td>
              <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: e.color }}>{e.rank}</td>
              <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: e.color }}>{e.ndcg}</td>
              <td>
                <span className={`tag ${e.tagClass}`}>{e.outcome}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p style={{ margin: "18px 0 0", fontSize: 12, color: "rgba(233,233,237,.45)", maxWidth: "74ch" }}>
        Showing 10 of 84 rows. Illustrative figures for the mockup — the real labels live in
        data/noc_eval_labels.csv and the report is produced by the /evaluate endpoint.
      </p>
    </div>
  );
}
