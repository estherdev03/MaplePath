export type EducationLevel =
  | "secondary"
  | "one_year"
  | "two_year"
  | "bachelor"
  | "two_or_more_credentials"
  | "masters"
  | "phd";

export const AGE_SINGLE: Record<number, number> = {
  18: 99, 19: 105, 20: 110, 21: 110, 22: 110, 23: 110, 24: 110, 25: 110, 26: 110,
  27: 110, 28: 110, 29: 110, 30: 105, 31: 99, 32: 94, 33: 88, 34: 83, 35: 77,
  36: 72, 37: 66, 38: 61, 39: 55, 40: 50, 41: 39, 42: 28, 43: 17, 44: 6,
};

export const EDU_SINGLE: Record<EducationLevel, number> = {
  secondary: 30,
  one_year: 90,
  two_year: 98,
  bachelor: 120,
  two_or_more_credentials: 128,
  masters: 135,
  phd: 150,
};

export const FIRST: Record<number, number> = { 4: 6, 5: 6, 6: 9, 7: 17, 8: 23, 9: 31, 10: 34 };
export const SECOND: Record<number, number> = { 5: 1, 6: 1, 7: 3, 8: 3, 9: 6, 10: 6 };
export const CANEXP: Record<number, number> = { 1: 40, 2: 53, 3: 64, 4: 72, 5: 80 };

export const TIER: Record<EducationLevel, number[]> = {
  secondary: [0, 0],
  one_year: [13, 25],
  two_year: [13, 25],
  bachelor: [13, 25],
  two_or_more_credentials: [25, 50],
  masters: [25, 50],
  phd: [25, 50],
};

export const EDU_LABEL: Record<EducationLevel, string> = {
  secondary: "Secondary school",
  one_year: "One-year credential",
  two_year: "Two-year credential",
  bachelor: "Bachelor's degree",
  two_or_more_credentials: "Two or more credentials",
  masters: "Master's degree",
  phd: "Doctoral degree",
};

export interface SimProfile {
  age: number;
  clb: number;
  nclc: number;
  canYears: number;
  foreignYears: number;
  edu: EducationLevel;
  pnp: boolean;
  sibling: boolean;
  canStudy: boolean;
}

export const BASE_PROFILE: SimProfile = {
  age: 29,
  clb: 9,
  nclc: 7,
  canYears: 1,
  foreignYears: 3,
  edu: "masters",
  pnp: false,
  sibling: false,
  canStudy: false,
};

export interface CrsBreakdown {
  age: number;
  education: number;
  first: number;
  second: number;
  canadian_experience: number;
  skill_transferability: number;
  french_bonus: number;
  provincial_nomination: number;
  sibling_in_canada: number;
  canadian_study: number;
  total: number;
}

export function calculateCrs(s: SimProfile): CrsBreakdown {
  const age = AGE_SINGLE[s.age] || 0;
  const education = EDU_SINGLE[s.edu];
  const first = (FIRST[s.clb] || 0) * 4;
  const second = s.nclc >= 5 ? (SECOND[s.nclc] || 0) * 4 : 0;
  const canadian_experience = s.canYears >= 1 ? CANEXP[Math.min(s.canYears, 5)] : 0;

  const t = TIER[s.edu];
  const lvl = s.clb >= 9 ? 1 : s.clb >= 7 ? 0 : -1;
  const eduLang = lvl < 0 ? 0 : t[lvl] ?? 0;
  const eduCan = s.canYears >= 2 ? t[1] : s.canYears >= 1 ? t[0] : 0;
  const fTier = s.foreignYears >= 3 ? 1 : s.foreignYears >= 1 ? 0 : -1;
  const fLang = fTier < 0 || lvl < 0 ? 0 : lvl === 1 && fTier === 1 ? 50 : fTier === 1 ? 25 : lvl === 1 ? 25 : 13;
  const fCan = fTier < 0 || s.canYears < 1 ? 0 : fTier === 1 && s.canYears >= 2 ? 50 : 25;
  const skill_transferability = Math.min(eduLang + eduCan + fLang + fCan, 100);

  const french_bonus = s.nclc >= 7 ? (s.clb >= 5 ? 50 : 25) : 0;
  const provincial_nomination = s.pnp ? 600 : 0;
  const sibling_in_canada = s.sibling ? 15 : 0;
  const canadian_study = s.canStudy ? 30 : 0;
  const extra = Math.min(provincial_nomination + sibling_in_canada + canadian_study + french_bonus, 600);

  const core = age + education + first + second + canadian_experience;

  return {
    age,
    education,
    first,
    second,
    canadian_experience,
    skill_transferability,
    french_bonus,
    provincial_nomination,
    sibling_in_canada,
    canadian_study,
    total: core + skill_transferability + extra,
  };
}
