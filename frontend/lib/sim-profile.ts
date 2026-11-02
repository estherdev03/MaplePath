import type { CLBScore, EducationLevel, Languages, SpouseProfile, UserProfile } from "./types";

export type CanStudy = "none" | "short" | "long";

/** What the simulator's controls can change. Everything else - ECA, trade
 * certificate, the subset work-experience fields, spouse study and relatives -
 * comes from the confirmed profile untouched. */
export interface SimProfile {
  age: number;
  clb: number; // lowest English CLB across abilities, 0 = no test
  nclc: number; // lowest French NCLC across abilities, 0 = no test
  canYears: number;
  foreignYears: number;
  edu: EducationLevel;
  pnp: boolean;
  sibling: boolean;
  canStudy: CanStudy; // Canadian credential: none, 1-2 years, 3+ years
  married: boolean;
  spouseEdu: EducationLevel | "none";
  spouseLang: number; // lowest CLB/NCLC of the spouse's first language, 0 = no test
  spouseCanYears: number;
}

const NO_SPOUSE: SpouseProfile = {
  education: null,
  languages: null,
  canadian_experience: 0,
  canada_study_years: 0,
  relative_in_can: false,
};

const SLIDER_MAX_YEARS = 5;

function minAbility(scores?: CLBScore | null): number {
  if (!scores) return 0;
  return Math.min(scores.speaking, scores.writing, scores.listening, scores.reading);
}

function clampYears(years: number): number {
  return Math.min(Math.max(Math.floor(years), 0), SLIDER_MAX_YEARS);
}

/** Seeds the simulator with the confirmed profile's own numbers so "reset"
 * returns to where the user actually stands. */
export function profileToSimProfile(profile: UserProfile): SimProfile {
  const canEdu = profile.canada_education;
  const canYears = canEdu?.completed ? canEdu.credential_years : 0;
  const spouse = profile.spouse;
  return {
    age: profile.age ?? 30,
    clb: minAbility(profile.languages?.english?.clb_scores),
    nclc: minAbility(profile.languages?.french?.nclc_scores),
    canYears: clampYears(profile.work_experience?.canada_years ?? 0),
    foreignYears: clampYears(profile.work_experience?.foreign_years ?? 0),
    edu: profile.education?.level ?? "bachelor",
    pnp: profile.provincial_nomination,
    sibling: profile.sibling_in_can,
    canStudy: canYears >= 3 ? "long" : canYears >= 1 ? "short" : "none",
    married: profile.marital_status === "married",
    spouseEdu: spouse?.education?.level ?? "none",
    spouseLang: spouseFirstLevel(spouse?.languages),
    spouseCanYears: clampYears(spouse?.canadian_experience ?? 0),
  };
}

// CRS scores only the spouse's first official language.
function spouseFirstLevel(langs: Languages | null | undefined): number {
  if (langs?.french?.is_first_language) return minAbility(langs.french.nclc_scores);
  return minAbility(langs?.english?.clb_scores);
}

function simSpouse(spouse: SpouseProfile, sim: SimProfile, initial: SimProfile): SpouseProfile {
  const next = { ...spouse };

  if (sim.spouseEdu !== initial.spouseEdu) {
    // A credential added here is assumed assessed (ECA) - unassessed foreign
    // credentials score 0, which is what "none" already shows.
    next.education =
      sim.spouseEdu === "none"
        ? null
        : spouse.education
          ? { ...spouse.education, level: sim.spouseEdu }
          : { level: sim.spouseEdu, has_COQ: false, from_canada: false, eca_completed: true };
  }

  if (sim.spouseLang !== initial.spouseLang) {
    const langs = spouse.languages;
    if (sim.spouseLang === 0) {
      next.languages = null;
    } else if (langs?.french?.is_first_language) {
      next.languages = {
        ...langs,
        french: {
          ...langs.french,
          detail_scores: null,
          nclc_scores: shiftLevels(langs.french.nclc_scores, initial.spouseLang, sim.spouseLang),
        },
      };
    } else {
      next.languages = {
        french: langs?.french ?? null,
        english: {
          test_name: langs?.english?.test_name ?? "celpip",
          is_first_language: true,
          detail_scores: null,
          clb_scores: shiftLevels(langs?.english?.clb_scores, initial.spouseLang, sim.spouseLang),
        },
      };
      if (next.languages.french) next.languages.french = { ...next.languages.french, is_first_language: false };
    }
  }

  if (sim.spouseCanYears !== initial.spouseCanYears) next.canadian_experience = sim.spouseCanYears;
  return next;
}

// Moves the lowest ability to `level`: raising lifts any ability below it,
// lowering caps every ability at it. Abilities already past the new floor
// keep their own level.
function shiftLevels(scores: CLBScore | null | undefined, from: number, level: number): CLBScore {
  const base = scores ?? { speaking: level, writing: level, listening: level, reading: level };
  const move = (v: number) => (level >= from ? Math.max(v, level) : Math.min(v, level));
  return {
    speaking: move(base.speaking),
    writing: move(base.writing),
    listening: move(base.listening),
    reading: move(base.reading),
  };
}

function simLanguages(profile: UserProfile, sim: SimProfile, initial: SimProfile): Languages | null {
  const langs = profile.languages;
  let english = langs?.english ?? null;
  let french = langs?.french ?? null;

  // A moved slider sends levels with no raw test scores - the backend
  // scores CLB/NCLC as given in that case.
  if (sim.clb !== initial.clb) {
    english =
      sim.clb === 0
        ? null
        : {
            test_name: english?.test_name ?? "celpip",
            is_first_language: english?.is_first_language ?? false,
            detail_scores: null,
            clb_scores: shiftLevels(english?.clb_scores, initial.clb, sim.clb),
          };
  }
  if (sim.nclc !== initial.nclc) {
    french =
      sim.nclc === 0
        ? null
        : {
            test_name: french?.test_name ?? "tef",
            is_first_language: french?.is_first_language ?? false,
            detail_scores: null,
            nclc_scores: shiftLevels(french?.nclc_scores, initial.nclc, sim.nclc),
          };
  }

  if (!english && !french) return null;
  // Exactly one test must be the first official language.
  if (english && !french) english = { ...english, is_first_language: true };
  else if (french && !english) french = { ...french, is_first_language: true };
  else if (english && french && english.is_first_language === french.is_first_language) {
    english = { ...english, is_first_language: true };
    french = { ...french, is_first_language: false };
  }
  return { english, french };
}

/** Applies the simulator's controls to the confirmed profile. Only controls
 * the user actually moved are written, so an untouched simulator sends the
 * confirmed profile back unchanged and scores identically to it. */
export function simToUserProfile(profile: UserProfile, sim: SimProfile, initial: SimProfile): UserProfile {
  const next: UserProfile = { ...profile, crs_score: null, eligibility: null, advice: null };

  if (sim.age !== initial.age) next.age = sim.age;
  if (sim.edu !== initial.edu && profile.education) next.education = { ...profile.education, level: sim.edu };
  if (sim.pnp !== initial.pnp) next.provincial_nomination = sim.pnp;
  if (sim.sibling !== initial.sibling) next.sibling_in_can = sim.sibling;

  if (sim.clb !== initial.clb || sim.nclc !== initial.nclc) {
    next.languages = simLanguages(profile, sim, initial);
  }

  const wx = profile.work_experience;
  if (wx && (sim.canYears !== initial.canYears || sim.foreignYears !== initial.foreignYears)) {
    const canada = sim.canYears !== initial.canYears ? sim.canYears : wx.canada_years;
    const foreign = sim.foreignYears !== initial.foreignYears ? sim.foreignYears : wx.foreign_years;
    // Subset fields can't exceed their totals (backend validation), so they
    // shrink with them.
    next.work_experience = {
      ...wx,
      canada_years: canada,
      foreign_years: foreign,
      continuous_fulltime_canada_years: Math.min(wx.continuous_fulltime_canada_years, canada),
      canada_work_exp_within_3_years: Math.min(wx.canada_work_exp_within_3_years, canada),
      alberta_years: Math.min(wx.alberta_years, canada),
      continuous_fulltime_foreign_years: Math.min(wx.continuous_fulltime_foreign_years, foreign),
      trade_exp_within_5_years: Math.min(wx.trade_exp_within_5_years, canada + foreign),
    };
  }

  if (sim.married !== initial.married) next.marital_status = sim.married ? "married" : "single";
  // Single drops the spouse. Switching a single profile to married starts
  // from an empty spouse, which the spouse controls then fill in.
  next.spouse = sim.married ? simSpouse(profile.spouse ?? NO_SPOUSE, sim, initial) : null;

  if (sim.canStudy !== initial.canStudy) {
    next.canada_education =
      sim.canStudy === "none"
        ? { completed: false, credential_years: 0 }
        : { completed: true, credential_years: sim.canStudy === "long" ? 3 : 2 };
  }

  return next;
}
