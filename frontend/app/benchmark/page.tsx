import EvaluationExampleTable from "@/components/EvaluationExampleTable";
import { ApiError, getEvaluation } from "@/lib/api";
import type { RetrievalScore } from "@/lib/types";

export const dynamic = "force-dynamic";

// All method labels included in the evaluation
const METHOD_LABELS: {
  key: "bm25" | "vector" | "rrf" | "hybrid";
  name: string;
  note: string;
}[] = [
  { key: "bm25", name: "BM25 full-text", note: "keyword matching only" },
  {
    key: "vector",
    name: "pgvector semantic",
    note: "embedding similarity only",
  },
  { key: "rrf", name: "Reciprocal rank fusion", note: "both lists merged" },
  {
    key: "hybrid",
    name: "Hybrid + Cohere rerank",
    note: "rerank with Cohere after merging",
  },
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
    error =
      e instanceof ApiError
        ? e.message
        : "Could not reach the evaluation endpoint.";
  }

  if (error || !report) {
    return (
      <div className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20">
        <div className="flex flex-wrap items-baseline gap-3">
          <h3 className="m-0">
            Does the occupation search actually work?
          </h3>
          <span className="tag tag-outline">GET /evaluate</span>
        </div>
        <p className="mt-4 mb-0 text-[14px] text-[#f2a3a3]">
          {error}
        </p>
      </div>
    );
  }

  const { examples_report, mean_report } = report;
  const misses = examples_report.filter((e) => e.vector[1] === 0).length;
  const stats = [
    {
      label: "Correct NOC in top 10",
      value: `${Math.round(mean_report.vector[1] * 100)}%`,
      note: `${examples_report.length - misses} of ${examples_report.length} descriptions`,
    },
    {
      label: "Ranking quality",
      value: mean_report.vector[0].toFixed(3),
      note: "NDCG@10, shipped method",
    },
    {
      label: "Lift over keyword search",
      value: `${mean_report.vector[0] - mean_report.bm25[0] >= 0 ? "+" : ""}${(mean_report.vector[0] - mean_report.bm25[0]).toFixed(3)}`,
      note: "Vector vs BM25 alone",
      colorClass: "text-[#b5abfc]",
    },
    {
      label: "Misses",
      value: String(misses),
      note: "vector method, outside top 10",
    },
  ];

  const methodRows = METHOD_LABELS.map((m) => {
    const score = mean_report[m.key];
    const shipped = m.key === "vector";
    return {
      ...m,
      ndcg: score[0].toFixed(3),
      hit: score[1].toFixed(2),
      pctVal: pct(score),
      fgClass: shipped ? "text-[#b5abfc]" : "text-[rgba(233,233,237,.72)]",
      barClass: shipped ? "bg-[#9184d9]" : "bg-[#595d6c]",
    };
  });

  return (
    <div className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20">
      <div className="flex flex-wrap items-baseline gap-3">
        <h3 className="m-0">Does the occupation search actually work?</h3>
        <span className="tag tag-outline">GET /evaluate</span>
      </div>
      <p className="mt-2 mb-0 max-w-[72ch] text-[15px] text-[rgba(233,233,237,.72)]">
        Classifying a job description into one of the NOC 2021 unit groups is
        the one place in MaplePath where a wrong answer is plausible and
        consequential - it decides TEER, and TEER decides program eligibility.
        So retrieval is measured, not asserted. {examples_report.length} job
        descriptions, hand-labelled with their correct NOC code, run through
        four retrieval methods with identical queries.
      </p>
      <div className="mt-[26px] grid grid-cols-[repeat(auto-fit,minmax(190px,1fr))] gap-3.5">
        {stats.map((s) => (
          <div
            key={s.label}
            className="rounded-xl bg-[#161826] px-4.5 py-4 shadow-[var(--shadow-sm)]"
          >
            <div className="text-[11px] tracking-[.06em] text-[rgba(233,233,237,.55)] uppercase">
              {s.label}
            </div>
            <div className={`mt-1 text-[32px] font-medium ${s.colorClass ?? ""}`}>
              {s.value}
            </div>
            <div className="text-[12px] text-[rgba(233,233,237,.5)]">
              {s.note}
            </div>
          </div>
        ))}
      </div>
      <h5 className="mx-0 mt-8 mb-1">
        Each method against the same {examples_report.length} labels
      </h5>
      <p className="mt-0 mb-4 text-[13px] text-[rgba(233,233,237,.55)]">
        Higher NDCG@10 means the correct code sits nearer the top of the list.
        The shipped method is the{" "}
        <span className="text-[#b5abfc]">second</span> row.
      </p>
      <div className="flex flex-col gap-0.5">
        {methodRows.map((m) => (
          <div
            key={m.name}
            className="border-t border-[rgba(233,233,237,.08)] py-[13px]"
          >
            <div className="flex flex-wrap items-baseline gap-2 text-[14px]">
              <span className={`min-w-[190px] ${m.fgClass}`}>{m.name}</span>
              <span className="text-[12px] text-[rgba(233,233,237,.45)]">
                {m.note}
              </span>
              <span
                className={`ml-auto w-[66px] text-right tabular-nums ${m.fgClass}`}
              >
                {m.ndcg}
              </span>
              <span className="w-[86px] text-right text-[12px] text-[rgba(233,233,237,.45)]">
                hit {m.hit}
              </span>
            </div>
            <div className="mt-2 h-1.5 rounded-[3px] bg-[rgba(233,233,237,.1)]">
              <div
                className={`h-1.5 rounded-[3px] ${m.barClass}`}
                style={{ width: `${m.pctVal}%` }}
              />
            </div>
          </div>
        ))}
      </div>
      <h5 className="mx-0 mt-[34px] mb-1">Per-example report</h5>
      <p className="mt-0 mb-3.5 text-[13px] text-[rgba(233,233,237,.55)]">
        One row per labelled description, from{" "}
        <code className="text-[12px]">examples_report</code>. NDCG and hit are
        for the shipped vector method.
      </p>
      <EvaluationExampleTable examples_report={examples_report} />
      <p className="mt-4.5 mb-0 max-w-[74ch] text-[12px] text-[rgba(233,233,237,.45)]">
        Labels live in data/noc_eval_labels.csv. This report is produced live by
        the /evaluate endpoint on each visit.
      </p>
    </div>
  );
}
