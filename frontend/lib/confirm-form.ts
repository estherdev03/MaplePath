import type {
  EducationLevel,
  EnglishTest,
  FrenchTest,
  MaritalStatus,
  ProfileConfirmFormPayload,
} from "./types";

export const EDUCATION_OPTIONS: { value: EducationLevel; label: string }[] = [
  { value: "secondary", label: "Secondary school" },
  { value: "one_year", label: "One-year credential" },
  { value: "two_year", label: "Two-year credential" },
  { value: "bachelor", label: "Bachelor's degree" },
  { value: "two_or_more_credentials", label: "Two or more credentials" },
  { value: "masters", label: "Master's degree" },
  { value: "phd", label: "Doctoral degree" },
];

export const ENGLISH_TEST_OPTIONS: EnglishTest[] = ["ielts", "celpip", "pte"];
export const FRENCH_TEST_OPTIONS: FrenchTest[] = ["tef", "tcf"];

function num(formData: FormData, name: string, fallback = 0): number {
  const raw = formData.get(name);
  if (raw === null || raw === "") return fallback;
  const value = Number(raw);
  if (Number.isNaN(value)) {
    throw new Error(`"${name.replaceAll("_", " ")}" must be a number.`);
  }
  return value;
}

function requiredNum(formData: FormData, name: string, label: string): number {
  const raw = formData.get(name);
  if (raw === null || raw === "") {
    throw new Error(`${label} is required.`);
  }
  const value = Number(raw);
  if (Number.isNaN(value)) {
    throw new Error(`${label} must be a number.`);
  }
  return value;
}

function str(formData: FormData, name: string): string {
  return String(formData.get(name) ?? "").trim();
}

function bool(formData: FormData, name: string): boolean {
  return formData.get(name) === "on" || formData.get(name) === "true";
}

/** Builds the languages block from the confirm form's language fields. */
function buildLanguages(formData: FormData, prefix: "" | "spouse_") {
  const hasEnglish = bool(formData, `${prefix}has_english`);
  const hasFrench = bool(formData, `${prefix}has_french`);
  const firstLanguage = str(formData, `${prefix}first_language`) || "english";

  const english = hasEnglish
    ? {
        test_name: (str(formData, `${prefix}english_test`) || "ielts") as EnglishTest,
        overall_score: null,
        detail_scores: {
          speaking: requiredNum(formData, `${prefix}english_speaking`, "English speaking score"),
          writing: requiredNum(formData, `${prefix}english_writing`, "English writing score"),
          listening: requiredNum(formData, `${prefix}english_listening`, "English listening score"),
          reading: requiredNum(formData, `${prefix}english_reading`, "English reading score"),
        },
        clb_scores: null,
        is_first_language: !hasFrench || firstLanguage === "english",
      }
    : null;

  const french = hasFrench
    ? {
        test_name: (str(formData, `${prefix}french_test`) || "tef") as FrenchTest,
        overall_score: null,
        detail_scores: {
          speaking: requiredNum(formData, `${prefix}french_speaking`, "French speaking score"),
          writing: requiredNum(formData, `${prefix}french_writing`, "French writing score"),
          listening: requiredNum(formData, `${prefix}french_listening`, "French listening score"),
          reading: requiredNum(formData, `${prefix}french_reading`, "French reading score"),
        },
        nclc_scores: null,
        is_first_language: !hasEnglish || firstLanguage === "french",
      }
    : null;

  if (!english && !french) {
    throw new Error("At least one language test (English or French) is required.");
  }

  return { english, french };
}

export function buildConfirmPayload(formData: FormData): ProfileConfirmFormPayload {
  const maritalStatus = (str(formData, "marital_status") || "single") as MaritalStatus;
  const isMarried = maritalStatus === "married";
  const educationFromCanada = str(formData, "education_location") === "canada";

  const payload: ProfileConfirmFormPayload = {
    age: requiredNum(formData, "age", "Age"),
    job_title: str(formData, "job_title") || (() => {
      throw new Error("Job title is required.");
    })(),
    job_responsibility:
      str(formData, "job_responsibility") ||
      (() => {
        throw new Error("Main responsibilities are required for NOC classification.");
      })(),
    have_canada_job_offer: bool(formData, "have_canada_job_offer"),
    languages: buildLanguages(formData, ""),
    work_experience: {
      foreign_years: num(formData, "work_foreign_years"),
      canada_years: num(formData, "work_canada_years"),
      alberta_years: num(formData, "work_alberta_years"),
      continuous_fulltime_foreign_years: num(formData, "work_continuous_foreign_years"),
      continuous_fulltime_canada_years: num(formData, "work_continuous_canada_years"),
      canada_work_exp_within_3_years: num(formData, "work_canada_within_3_years"),
      trade_exp_within_5_years: num(formData, "work_trade_within_5_years"),
    },
    marital_status: maritalStatus,
    education: {
      level: (str(formData, "education_level") || "bachelor") as EducationLevel,
      has_COQ: bool(formData, "education_has_coq"),
      from_canada: educationFromCanada,
      eca_completed: educationFromCanada ? true : bool(formData, "education_eca_completed"),
    },
    canada_education: {
      completed: bool(formData, "canada_education_completed"),
      credential_years: bool(formData, "canada_education_completed")
        ? num(formData, "canada_education_years")
        : 0,
    },
    provincial_nomination: bool(formData, "provincial_nomination"),
    sibling_in_can: bool(formData, "sibling_in_can"),
    relative_in_can: bool(formData, "relative_in_can"),
    spouse: {
      education: null,
      languages: null,
      canadian_experience: 0,
      relative_in_can: false,
    },
    current_available_funds: requiredNum(formData, "current_available_funds", "Settlement funds"),
  };

  if (isMarried) {
    const spouseEducationLevel = str(formData, "spouse_education_level");
    const spouseEducationFromCanada = str(formData, "spouse_education_location") === "canada";
    const hasSpouseLanguage =
      bool(formData, "spouse_has_english") || bool(formData, "spouse_has_french");

    payload.spouse = {
      education: spouseEducationLevel
        ? {
            level: spouseEducationLevel as EducationLevel,
            has_COQ: false,
            from_canada: spouseEducationFromCanada,
            eca_completed: spouseEducationFromCanada
              ? true
              : bool(formData, "spouse_education_eca_completed"),
          }
        : null,
      languages: hasSpouseLanguage ? buildLanguages(formData, "spouse_") : null,
      canadian_experience: num(formData, "spouse_canadian_experience"),
      relative_in_can: bool(formData, "spouse_relative_in_can"),
    };
  }

  return payload;
}
