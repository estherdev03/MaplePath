import { crsCategoryMaxes } from "./crs-maxes";
import { educationLabel } from "./format";
import type { CLBScore, CRSBreakdown, NCLCScore, UserProfile } from "./types";

export interface CrsRow {
  label: string;
  pts: number;
  max: number;
  pct: number;
}

function minAbility(scores: CLBScore | NCLCScore | null | undefined): number | null {
  if (!scores) return null;
  return Math.min(scores.speaking, scores.writing, scores.listening, scores.reading);
}

function languageSummary(profile: UserProfile, first: boolean): string | null {
  const languages = profile.languages;
  if (!languages) return null;
  const english = languages.english;
  const french = languages.french;
  const test = [english, french].find((t) => t?.is_first_language === first);
  if (!test) return null;
  const level = minAbility(test === english ? english?.clb_scores : french?.nclc_scores);
  const scale = test === english ? "CLB" : "NCLC";
  const name = test.test_name.toUpperCase();
  return level != null ? `${name}, ${scale} ${level}` : `${name}, sub-scores needed`;
}

function educationDetail(profile: UserProfile): string {
  const edu = profile.education;
  if (!edu) return "not stated";
  const eca = edu.eca_completed ? " with ECA" : "";
  return `${educationLabel(edu.level).toLowerCase()}${eca}`;
}

/** Builds display rows for the CRS breakdown returned by the API, with maxima
 * mirrored from crs/constants.py — never invented, only ceilings. */
export function buildCrsRows(profile: UserProfile): CrsRow[] {
  const score = profile.crs_score;
  if (!score) return [];
  const b = score.breakdown;
  const maxes = crsCategoryMaxes(profile.marital_status);
  const married = profile.marital_status === "married";

  const entries: { key: keyof CRSBreakdown; label: string; show: boolean }[] = [
    { key: "age", label: `Age${profile.age != null ? ` · ${profile.age}` : ""}`, show: true },
    { key: "education", label: `Level of education · ${educationDetail(profile)}`, show: true },
    {
      key: "first_language",
      label: `First official language${languageSummary(profile, true) ? ` · ${languageSummary(profile, true)}` : ""}`,
      show: true,
    },
    {
      key: "second_language",
      label: `Second official language${languageSummary(profile, false) ? ` · ${languageSummary(profile, false)}` : ""}`,
      show: true,
    },
    {
      key: "canadian_experience",
      label: `Canadian work experience · ${profile.work_experience?.canada_years ?? 0} year(s)`,
      show: true,
    },
    { key: "skill_transferability", label: "Skill transferability · capped", show: true },
    { key: "spouse_total", label: "Spouse or partner factors", show: married },
    { key: "french_bonus", label: "Additional · French ability", show: true },
    { key: "provincial_nomination", label: "Additional · provincial nomination", show: true },
    { key: "canadian_study", label: "Additional · Canadian study", show: true },
    { key: "sibling_in_canada", label: "Additional · sibling in Canada", show: true },
  ];

  return entries
    .filter((e) => e.show)
    .map((e) => {
      const pts = b[e.key];
      const max = maxes[e.key];
      return { label: e.label, pts, max, pct: max > 0 ? Math.round((pts / max) * 100) : 0 };
    });
}
