import { formatEducation, formatLanguages } from "./format";
import type {
  CanadianExperienceClassEligibility,
  FSWScoreBreakdown,
  FederalSkilledTradesEligibility,
  FederalSkilledWorkerEligibility,
  UserProfile,
} from "./types";

export interface RequirementRow {
  ok: boolean;
  label: string;
  detail: string;
}

export interface ProgramView {
  name: string;
  sub: string;
  verdict: string;
  tagClass: string;
  edge: string;
  reqs: RequirementRow[];
}

function verdictFor(eligible: boolean, reqs: RequirementRow[]): { verdict: string; tagClass: string; edge: string } {
  if (eligible) return { verdict: "Eligible", tagClass: "tag-accent", edge: "#5d5294" };
  const open = reqs.filter((r) => !r.ok).length;
  return {
    verdict: open === reqs.length ? "Not eligible" : `${open} requirement${open === 1 ? "" : "s"} open`,
    tagClass: "tag-neutral",
    edge: "#3f424d",
  };
}

function fundsDetail(profile: UserProfile, required: boolean, met: boolean): string {
  if (!required) return "not required — job offer on file";
  return met ? `CAD ${profile.current_available_funds.toLocaleString()}` : `CAD ${profile.current_available_funds.toLocaleString()} — below threshold`;
}

function cecRows(profile: UserProfile, b: CanadianExperienceClassEligibility): RequirementRow[] {
  const wx = profile.work_experience;
  return [
    {
      ok: b.canadian_work_experience_met,
      label: "1 year Canadian work experience within 3 years",
      detail: wx ? `${wx.canada_work_exp_within_3_years} yr` : "not established",
    },
    {
      ok: b.eligible_teer_met,
      label: "Occupation in TEER 0, 1, 2 or 3",
      detail: profile.occupation?.teer != null ? `TEER ${profile.occupation.teer}` : "unknown",
    },
    {
      ok: b.language_requirement_met,
      label: "CLB 7 in all abilities (TEER 0–1) or CLB 5 (TEER 2–3)",
      detail: formatLanguages(profile.languages),
    },
  ];
}

function fswRows(profile: UserProfile, b: FederalSkilledWorkerEligibility): RequirementRow[] {
  return [
    {
      ok: b.continuous_work_experience_met,
      label: "1 year continuous full-time experience",
      detail: b.continuous_work_experience_met ? "established" : "not established — field missing",
    },
    {
      ok: b.eligible_teer_met,
      label: "Occupation in TEER 0–3",
      detail: profile.occupation?.teer != null ? `TEER ${profile.occupation.teer}` : "unknown",
    },
    {
      ok: b.language_requirement_met,
      label: "CLB 7 first language and NCLC 5 second",
      detail: formatLanguages(profile.languages),
    },
    {
      ok: b.education_requirement_met,
      label: "Education with ECA or Canadian credential",
      detail: formatEducation(profile.education),
    },
    {
      ok: b.selection_factor_passed,
      label: "Selection grid ≥ 67",
      detail: `${b.selection_factor_score} / 100`,
    },
    {
      ok: b.settlement_funds_met || !b.settlement_funds_required,
      label: "Settlement funds meet the threshold",
      detail: fundsDetail(profile, b.settlement_funds_required, b.settlement_funds_met),
    },
  ];
}

function fstRows(profile: UserProfile, b: FederalSkilledTradesEligibility): RequirementRow[] {
  return [
    {
      ok: b.skilled_trade_experience_within_5_years_met,
      label: "2 years skilled trade experience within 5 years",
      detail: profile.work_experience ? `${profile.work_experience.trade_exp_within_5_years} yr` : "0 yr",
    },
    {
      ok: b.eligible_trade_met,
      label: "Occupation in an eligible trade group",
      detail: profile.occupation?.noc_code ? `${profile.occupation.noc_code} is not a trade group` : "unknown",
    },
    {
      ok: b.speaking_listening_requirement_met,
      label: "CLB 5 speaking and listening",
      detail: formatLanguages(profile.languages),
    },
    {
      ok: b.reading_writing_requirement_met,
      label: "CLB 4 reading and writing",
      detail: formatLanguages(profile.languages),
    },
    {
      ok: b.valid_job_offer_or_certificate_met,
      label: "Job offer or certificate of qualification",
      detail: b.valid_job_offer_or_certificate_met ? "on file" : "neither",
    },
    {
      ok: b.settlement_funds_met || !b.settlement_funds_required,
      label: "Settlement funds meet the threshold",
      detail: fundsDetail(profile, b.settlement_funds_required, b.settlement_funds_met),
    },
  ];
}

export function buildProgramViews(profile: UserProfile): ProgramView[] {
  const el = profile.eligibility;
  if (!el) return [];
  const views: ProgramView[] = [];

  const cec = el.canadian_exp_class;
  if (cec?.breakdown) {
    const reqs = cecRows(profile, cec.breakdown);
    views.push({ name: "Canadian Experience Class", sub: "CEC · TEER 0–3 with Canadian experience", reqs, ...verdictFor(cec.eligible, reqs) });
  }

  const fsw = el.federal_skilled_worker;
  if (fsw?.breakdown) {
    const reqs = fswRows(profile, fsw.breakdown);
    views.push({ name: "Federal Skilled Worker", sub: "FSW · 67-point selection grid", reqs, ...verdictFor(fsw.eligible, reqs) });
  }

  const fst = el.federal_skilled_trade;
  if (fst?.breakdown) {
    const reqs = fstRows(profile, fst.breakdown);
    views.push({ name: "Federal Skilled Trades", sub: "FST · eligible trade groups only", reqs, ...verdictFor(fst.eligible, reqs) });
  }

  return views;
}

export const FSW_GRID_MAX: Record<keyof FSWScoreBreakdown, number> = {
  education_pts: 25,
  first_lang_pts: 24,
  second_lang_pts: 4,
  work_exp_pts: 15,
  age_pts: 12,
  employment_pts: 10,
  adaptability_pts: 10,
};

export const FSW_GRID_LABELS: Record<keyof FSWScoreBreakdown, string> = {
  education_pts: "Education",
  first_lang_pts: "First language",
  second_lang_pts: "Second language",
  work_exp_pts: "Work experience",
  age_pts: "Age",
  employment_pts: "Arranged employment",
  adaptability_pts: "Adaptability",
};
