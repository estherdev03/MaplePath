// Mirrors graph/state/profile.py, graph/state/eligibility.py, graph/state/shared.py,
// and noc/types.py. Keep in sync with the backend Pydantic models.

export type EducationLevel =
  | "secondary"
  | "one_year"
  | "two_year"
  | "bachelor"
  | "two_or_more_credentials"
  | "masters"
  | "phd";

export type EnglishTest = "ielts" | "celpip" | "pte";
export type FrenchTest = "tef" | "tcf";
export type MaritalStatus = "single" | "married";

export interface LanguageScore {
  speaking?: number | null;
  writing?: number | null;
  listening?: number | null;
  reading?: number | null;
}

export interface CLBScore {
  speaking: number;
  writing: number;
  listening: number;
  reading: number;
}

export interface NCLCScore {
  speaking: number;
  writing: number;
  listening: number;
  reading: number;
}

export interface EnglishScore {
  test_name: EnglishTest;
  overall_score?: number | null;
  detail_scores?: LanguageScore | null;
  clb_scores?: CLBScore | null;
  is_first_language: boolean;
}

export interface FrenchScore {
  test_name: FrenchTest;
  overall_score?: number | null;
  detail_scores?: LanguageScore | null;
  nclc_scores?: NCLCScore | null;
  is_first_language: boolean;
}

export interface Languages {
  english: EnglishScore | null;
  french: FrenchScore | null;
}

export interface Experience {
  foreign_years: number;
  canada_years: number;
  alberta_years: number;
  continuous_fulltime_foreign_years: number;
  continuous_fulltime_canada_years: number;
  canada_work_exp_within_3_years: number;
  trade_exp_within_5_years: number;
}

export interface Education {
  level: EducationLevel;
  has_COQ: boolean;
  from_canada: boolean;
  eca_completed: boolean;
}

export interface CanadaEducation {
  completed: boolean;
  credential_years: number;
}

export interface SpouseProfile {
  education: Education | null;
  languages: Languages | null;
  canadian_experience: number;
  relative_in_can: boolean;
}

export interface OccupationCandidate {
  noc_code: string;
  title: string;
}

export interface Occupation {
  title: string;
  noc_code: string | null;
  teer: number | null;
  major_group_code: string | null;
  minor_group_code: string | null;
  submajor_group_code: string | null;
  have_canada_job_offer: boolean;
  noc_confidence: number | null;
  reasoning: string | null;
  candidates: OccupationCandidate[];
}

export interface CRSBreakdown {
  age: number;
  education: number;
  first_language: number;
  second_language: number;
  canadian_experience: number;
  spouse_total: number;
  skill_transferability: number;
  provincial_nomination: number;
  canadian_study: number;
  french_bonus: number;
  sibling_in_canada: number;
}

export interface SpouseBreakdown {
  education: number;
  language: number;
  canadian_experience: number;
}

export interface CRSScore {
  total: number;
  breakdown: CRSBreakdown;
  spouse_breakdown: SpouseBreakdown | null;
}

export interface FSWScoreBreakdown {
  education_pts: number;
  first_lang_pts: number;
  second_lang_pts: number;
  work_exp_pts: number;
  age_pts: number;
  employment_pts: number;
  adaptability_pts: number;
}

export interface FederalSkilledWorkerEligibility {
  continuous_work_experience_met: boolean;
  eligible_teer_met: boolean;
  language_requirement_met: boolean;
  education_requirement_met: boolean;
  selection_factor_breakdown: FSWScoreBreakdown | null;
  selection_factor_score: number;
  selection_factor_passed: boolean;
  settlement_funds_required: boolean;
  settlement_funds_met: boolean;
}

export interface CanadianExperienceClassEligibility {
  canadian_work_experience_met: boolean;
  eligible_teer_met: boolean;
  language_requirement_met: boolean;
}

export interface FederalSkilledTradesEligibility {
  skilled_trade_experience_within_5_years_met: boolean;
  eligible_trade_met: boolean;
  speaking_listening_requirement_met: boolean;
  reading_writing_requirement_met: boolean;
  valid_job_offer_or_certificate_met: boolean;
  settlement_funds_required: boolean;
  settlement_funds_met: boolean;
}

export interface EligibilityResult<T> {
  eligible: boolean;
  breakdown: T | null;
}

export interface ExpressEntryEligibility {
  federal_skilled_worker: EligibilityResult<FederalSkilledWorkerEligibility> | null;
  federal_skilled_trade: EligibilityResult<FederalSkilledTradesEligibility> | null;
  canadian_exp_class: EligibilityResult<CanadianExperienceClassEligibility> | null;
}

export interface UserProfile {
  age: number | null;
  occupation: Occupation | null;
  languages: Languages | null;
  work_experience: Experience | null;
  marital_status: MaritalStatus | null;
  education: Education | null;
  canada_education: CanadaEducation | null;
  provincial_nomination: boolean;
  sibling_in_can: boolean;
  relative_in_can: boolean;
  spouse: SpouseProfile | null;
  crs_score: CRSScore | null;
  eligibility: ExpressEntryEligibility | null;
  current_available_funds: number;
  advice: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileDraft {
  age: number | null;
  languages: Languages | null;
  job_title: string | null;
  job_responsibility: string | null;
  work_experience: Experience | null;
  education: Education | null;
  canada_education: CanadaEducation | null;
  provincial_nomination: boolean;
  sibling_in_can: boolean;
  relative_in_can: boolean;
  marital_status: MaritalStatus | null;
  spouse: SpouseProfile | null;
  current_available_funds: number | null;
  missing_fields: string[];
  warnings: string[];
}

export interface ProfileConfirmFormPayload {
  age: number;
  job_title: string;
  job_responsibility: string;
  have_canada_job_offer: boolean;
  languages: Languages;
  work_experience: Experience;
  marital_status: MaritalStatus;
  education: Education;
  canada_education: CanadaEducation;
  provincial_nomination: boolean;
  sibling_in_can: boolean;
  relative_in_can: boolean;
  spouse: SpouseProfile;
  current_available_funds: number;
}

// [ndcg, hit_rate]
export type RetrievalScore = [number, number];

export interface SingleExampleReport {
  case_type: string;
  job_title: string;
  bm25: RetrievalScore;
  vector: RetrievalScore;
  rrf: RetrievalScore;
  hybrid: RetrievalScore;
}

export interface RetrievalMethodMeanReport {
  bm25: RetrievalScore;
  vector: RetrievalScore;
  rrf: RetrievalScore;
  hybrid: RetrievalScore;
}

export interface EvaluateResponse {
  examples_report: SingleExampleReport[];
  mean_report: RetrievalMethodMeanReport;
}

export interface CrsSimulateResponse {
  crs_score: CRSScore;
  eligibility: ExpressEntryEligibility;
}
