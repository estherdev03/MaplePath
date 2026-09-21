import type { CRSBreakdown, MaritalStatus } from "./types";

// Mirrors the ceilings baked into crs/constants.py — used only to draw
// "share of maximum" bars next to the real points returned by the API.
export function crsCategoryMaxes(maritalStatus: MaritalStatus | null): Record<keyof CRSBreakdown, number> {
  const married = maritalStatus === "married";
  return {
    age: married ? 100 : 110,
    education: married ? 140 : 150,
    first_language: married ? 128 : 136,
    second_language: 24,
    canadian_experience: married ? 70 : 80,
    spouse_total: married ? 40 : 0,
    skill_transferability: 100,
    provincial_nomination: 600,
    canadian_study: 30,
    french_bonus: 50,
    sibling_in_canada: 15,
  };
}

export const CRS_TOTAL_MAX = 1200;
