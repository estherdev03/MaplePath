export const NAV_ITEMS = [
  { href: "/", label: "Landing" },
  { href: "/intake", label: "Intake" },
  { href: "/draft", label: "Draft review" },
  { href: "/confirm", label: "Confirm" },
  { href: "/results", label: "Results" },
  { href: "/eligibility", label: "Eligibility" },
  { href: "/noc", label: "Occupation" },
  { href: "/advice", label: "Advice" },
  { href: "/simulator", label: "Simulator" },
  { href: "/benchmark", label: "Benchmark" },
] as const;

export const INTAKE_FIELDS = [
  { label: "Age", value: "29", state: "read", color: "#e9e9ed", stateColor: "rgba(233,233,237,.4)" },
  { label: "Occupation", value: "21232 · Software developers · TEER 1", state: "matched 0.92", color: "#e9e9ed", stateColor: "#b5abfc" },
  { label: "Education", value: "Master's degree · ECA completed", state: "read", color: "#e9e9ed", stateColor: "rgba(233,233,237,.4)" },
  { label: "English (IELTS)", value: "CLB 9 / 8 / 10 / 9", state: "converted", color: "#e9e9ed", stateColor: "rgba(233,233,237,.4)" },
  { label: "French (TEF)", value: "sub-scores needed", state: "missing", color: "#b5abfc", stateColor: "#b5abfc" },
  { label: "Work experience", value: "3 yr foreign · 1 yr Canada", state: "read", color: "#e9e9ed", stateColor: "rgba(233,233,237,.4)" },
  { label: "Continuous full-time", value: "not established", state: "missing", color: "#b5abfc", stateColor: "#b5abfc" },
  { label: "Marital status", value: "Single", state: "read", color: "#e9e9ed", stateColor: "rgba(233,233,237,.4)" },
  { label: "Settlement funds", value: "CAD 18,500", state: "warning", color: "#e9e9ed", stateColor: "rgba(233,233,237,.6)" },
];

export const CRS_ROWS = [
  { label: "Age · 29", pts: 110, max: 110, pct: 100 },
  { label: "Level of education · master's with ECA", pts: 135, max: 150, pct: 90 },
  { label: "First official language · English, CLB 9", pts: 124, max: 150, pct: 83 },
  { label: "Second official language · French, NCLC 7", pts: 12, max: 24, pct: 50 },
  { label: "Canadian work experience · 1 year", pts: 40, max: 160, pct: 25 },
  { label: "Skill transferability · capped", pts: 100, max: 100, pct: 100 },
  { label: "Additional · French ability (NCLC 7 + CLB 5)", pts: 50, max: 600, pct: 8 },
  { label: "Additional · provincial nomination", pts: 0, max: 600, pct: 0 },
];

interface Requirement {
  ok: boolean;
  label: string;
  detail: string;
}

function mk(ok: boolean, label: string, detail: string): Requirement {
  return { ok, label, detail };
}

export const PROGRAMS = [
  {
    name: "Canadian Experience Class",
    sub: "CEC · TEER 0–3 with Canadian experience",
    verdict: "Eligible",
    tagClass: "tag-accent",
    edge: "#5d5294",
    reqs: [
      mk(true, "1 year Canadian work experience within 3 years", "1.0 yr"),
      mk(true, "Occupation in TEER 0, 1, 2 or 3", "TEER 1"),
      mk(true, "CLB 7 in all abilities (TEER 0–1)", "CLB 9 / 8 / 10 / 9"),
    ],
  },
  {
    name: "Federal Skilled Worker",
    sub: "FSW · 67-point selection grid",
    verdict: "Two requirements open",
    tagClass: "tag-neutral",
    edge: "#3f424d",
    reqs: [
      mk(false, "1 year continuous full-time experience", "not established — field missing"),
      mk(true, "Occupation in TEER 0–3", "TEER 1"),
      mk(false, "CLB 7 first language and NCLC 5 second", "TEF sub-scores missing"),
      mk(true, "Education with ECA or Canadian credential", "ECA completed"),
      mk(true, "Selection grid ≥ 67", "78 / 100"),
      mk(true, "Settlement funds ≥ CAD 15,263", "CAD 18,500"),
    ],
  },
  {
    name: "Federal Skilled Trades",
    sub: "FST · eligible trade groups only",
    verdict: "Not eligible",
    tagClass: "tag-neutral",
    edge: "#3f424d",
    reqs: [
      mk(false, "2 years skilled trade experience within 5 years", "0 yr"),
      mk(false, "Occupation in an eligible trade group", "21232 is not a trade group"),
      mk(true, "CLB 5 speaking and listening", "CLB 9 / 10"),
      mk(true, "CLB 4 reading and writing", "CLB 9 / 8"),
      mk(false, "Job offer or certificate of qualification", "neither"),
    ],
  },
];

export const FSW_GRID = [
  { label: "Education", val: 25, max: 25 },
  { label: "First language", val: 24, max: 24 },
  { label: "Second language", val: 4, max: 4 },
  { label: "Work experience", val: 13, max: 15 },
  { label: "Age", val: 12, max: 12 },
  { label: "Arranged employment", val: 0, max: 10 },
  { label: "Adaptability", val: 0, max: 10 },
];

export const CANDIDATES = [
  { code: "21232", title: "Software developers and programmers", bm25: "12.4", vec: "0.891", rrf: "0.033", rerank: "0.96", outcome: "Chosen", tagClass: "tag-accent", color: "#e9e9ed" },
  { code: "21231", title: "Software engineers and designers", bm25: "11.8", vec: "0.884", rrf: "0.032", rerank: "0.71", outcome: "Runner-up", tagClass: "tag-outline", color: "#e9e9ed" },
  { code: "21234", title: "Web developers and programmers", bm25: "9.6", vec: "0.842", rrf: "0.028", rerank: "0.44", outcome: "Rejected", tagClass: "tag-neutral", color: "rgba(233,233,237,.62)" },
  { code: "21211", title: "Data scientists", bm25: "7.1", vec: "0.818", rrf: "0.024", rerank: "0.21", outcome: "Rejected", tagClass: "tag-neutral", color: "rgba(233,233,237,.62)" },
  { code: "20012", title: "Computer and information systems managers", bm25: "6.8", vec: "0.803", rrf: "0.022", rerank: "0.18", outcome: "Rejected", tagClass: "tag-neutral", color: "rgba(233,233,237,.62)" },
  { code: "22220", title: "Computer network and web technicians", bm25: "5.2", vec: "0.777", rrf: "0.019", rerank: "0.09", outcome: "Rejected", tagClass: "tag-neutral", color: "rgba(233,233,237,.62)" },
];

export const ADVICE = [
  { gain: "+13", title: "Reach two years of Canadian work experience", body: "At two years the Canadian-experience table moves from 40 to 53 points, and the education-and-Canadian-experience transferability tier moves to its upper band.", rule: "CANADIAN_EXPERIENCE_SINGLE", effort: "11 months" },
  { gain: "+38", title: "Submit the TEF sub-scores you already hold", body: "Second-language points and the 50-point French bonus are being scored as zero because 'around B2' cannot be converted to NCLC. Entering four numbers resolves both, and closes one FSW requirement.", rule: "french_to_nclc", effort: "minutes" },
  { gain: "+11", title: "Retake IELTS writing to band 8", body: "Writing at CLB 8 is the one ability below 9. Lifting it raises first-language points and holds the CLB 9 threshold across all four abilities.", rule: "FIRST_LANGUAGE_SINGLE", effort: "one sitting" },
  { gain: "+600", title: "Pursue a provincial nomination", body: "The largest single move available, capped with the other additional points at 600. Alberta's AAIP streams are on the roadmap for this app.", rule: "provincial_nomination", effort: "months" },
];

export const EVAL_METHODS = [
  { name: "BM25 full-text", note: "keyword matching only", ndcg: "0.612", hit: "0.78", pct: 61, fg: "rgba(233,233,237,.72)", bar: "#595d6c" },
  { name: "pgvector semantic", note: "embedding similarity only", ndcg: "0.664", hit: "0.83", pct: 66, fg: "rgba(233,233,237,.72)", bar: "#595d6c" },
  { name: "Reciprocal rank fusion", note: "both lists merged", ndcg: "0.719", hit: "0.89", pct: 72, fg: "rgba(233,233,237,.72)", bar: "#796cbf" },
  { name: "Hybrid + Cohere rerank", note: "shipped", ndcg: "0.781", hit: "0.94", pct: 78, fg: "#b5abfc", bar: "#9184d9" },
];

export const EVAL_EXAMPLES = [
  { query: "Builds and maintains backend REST services", gold: "21232", rank: "1", ndcg: "1.000", color: "#b5abfc", outcome: "Top hit", tagClass: "tag-accent" },
  { query: "Designs system architecture for a SaaS platform", gold: "21231", rank: "1", ndcg: "1.000", color: "#b5abfc", outcome: "Top hit", tagClass: "tag-accent" },
  { query: "Writes SQL reports and maintains dashboards", gold: "21223", rank: "2", ndcg: "0.631", color: "rgba(233,233,237,.82)", outcome: "Top 10", tagClass: "tag-outline" },
  { query: "Installs and services residential furnaces", gold: "72402", rank: "1", ndcg: "1.000", color: "#b5abfc", outcome: "Top hit", tagClass: "tag-accent" },
  { query: "Prepares meals in a hotel kitchen, leads two cooks", gold: "63200", rank: "3", ndcg: "0.500", color: "rgba(233,233,237,.82)", outcome: "Top 10", tagClass: "tag-outline" },
  { query: "Assists registered nurses on a ward", gold: "33102", rank: "1", ndcg: "1.000", color: "#b5abfc", outcome: "Top hit", tagClass: "tag-accent" },
  { query: "Manages a small retail branch and its staff", gold: "60020", rank: "7", ndcg: "0.333", color: "rgba(233,233,237,.82)", outcome: "Top 10", tagClass: "tag-outline" },
  { query: "Operates a forklift in a distribution centre", gold: "75101", rank: "—", ndcg: "0.000", color: "#cfd3e5", outcome: "Missed", tagClass: "tag-neutral" },
  { query: "Teaches mathematics to secondary students", gold: "41220", rank: "1", ndcg: "1.000", color: "#b5abfc", outcome: "Top hit", tagClass: "tag-accent" },
  { query: "Coordinates payroll and benefits administration", gold: "12101", rank: "2", ndcg: "0.631", color: "rgba(233,233,237,.82)", outcome: "Top 10", tagClass: "tag-outline" },
];

export const TRACE = [
  { node: "route_event → profile_confirm", ms: "2 ms", mark: "●", color: "#b5abfc" },
  { node: "retrieve_noc_candidates", ms: "318 ms", mark: "●", color: "#b5abfc" },
  { node: "classify_occupation", ms: "1.24 s", mark: "●", color: "#b5abfc" },
  { node: "calculate_crs", ms: "4 ms", mark: "●", color: "#b5abfc" },
  { node: "evaluate_express_entry", ms: "3 ms", mark: "●", color: "#b5abfc" },
  { node: "persist_profile", ms: "46 ms", mark: "●", color: "#b5abfc" },
];

export const DEV_RESPONSE = {
  occupation: { noc_code: "21232", teer: 1, noc_confidence: 0.92 },
  crs_score: {
    total: 571,
    breakdown: {
      age: 110,
      education: 135,
      first_language: 124,
      second_language: 12,
      canadian_experience: 40,
      skill_transferability: 100,
      french_bonus: 50,
    },
  },
  eligibility: {
    canadian_exp_class: { eligible: true },
    federal_skilled_worker: { eligible: false },
    federal_skilled_trade: { eligible: false },
  },
};
