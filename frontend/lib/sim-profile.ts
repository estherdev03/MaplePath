import { BASE_PROFILE, type SimProfile } from "./crs";
import type { UserProfile } from "./types";

function minAbility(scores?: { speaking: number; writing: number; listening: number; reading: number } | null): number {
  if (!scores) return 0;
  return Math.min(scores.speaking, scores.writing, scores.listening, scores.reading);
}

/** Seeds the simulator with the confirmed profile's own numbers so "reset"
 * returns to where the user actually stands, not a fixed demo persona. */
export function profileToSimProfile(profile: UserProfile | undefined): SimProfile {
  if (!profile) return { ...BASE_PROFILE };
  const english = profile.languages?.english;
  const french = profile.languages?.french;
  const canYears = Math.round(profile.work_experience?.canada_years ?? 0);
  const foreignYears = Math.round(profile.work_experience?.foreign_years ?? 0);

  return {
    age: profile.age ?? BASE_PROFILE.age,
    clb: english ? minAbility(english.clb_scores) : 0,
    nclc: french ? minAbility(french.nclc_scores) : 0,
    canYears: Math.min(Math.max(canYears, 0), 5),
    foreignYears: Math.min(Math.max(foreignYears, 0), 5),
    edu: profile.education?.level ?? BASE_PROFILE.edu,
    pnp: profile.provincial_nomination,
    sibling: profile.sibling_in_can,
    canStudy: (profile.canada_education?.completed ?? false) && (profile.canada_education?.credential_years ?? 0) >= 2,
  };
}
