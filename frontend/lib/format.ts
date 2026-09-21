import { EDUCATION_OPTIONS } from "./confirm-form";
import type { Education, Languages, ProfileDraft, Experience } from "./types";

export function educationLabel(level: string | null | undefined): string {
  if (!level) return "Not stated";
  return EDUCATION_OPTIONS.find((o) => o.value === level)?.label ?? level;
}

export function formatEducation(education: Education | null | undefined): string {
  if (!education) return "Not stated";
  const eca = education.eca_completed ? " · ECA completed" : "";
  return `${educationLabel(education.level)}${eca}`;
}

export function formatLanguages(languages: Languages | null | undefined): string {
  if (!languages || (!languages.english && !languages.french)) return "Not stated";
  const parts: string[] = [];
  if (languages.english) {
    const scores = languages.english.detail_scores;
    parts.push(
      scores
        ? `${languages.english.test_name.toUpperCase()} ${scores.speaking ?? "?"}/${scores.writing ?? "?"}/${scores.listening ?? "?"}/${scores.reading ?? "?"}`
        : `${languages.english.test_name.toUpperCase()} sub-scores needed`
    );
  }
  if (languages.french) {
    const scores = languages.french.detail_scores;
    parts.push(
      scores
        ? `${languages.french.test_name.toUpperCase()} ${scores.speaking ?? "?"}/${scores.writing ?? "?"}/${scores.listening ?? "?"}/${scores.reading ?? "?"}`
        : `${languages.french.test_name.toUpperCase()} sub-scores needed`
    );
  }
  return parts.join(" · ");
}

export function formatFunds(amount: number | null | undefined): string {
  if (amount == null) return "Not stated";
  return `CAD ${amount.toLocaleString()}`;
}

export function formatExperience(experience: Experience | null | undefined): string {
  if (!experience) return "Not stated";
  const parts: string[] = [];
  if (experience.foreign_years) parts.push(`${experience.foreign_years} yr foreign`);
  if (experience.canada_years) parts.push(`${experience.canada_years} yr Canada`);
  if (!parts.length) return "Not stated";
  return parts.join(" · ");
}

export function humanizeFieldPath(path: string): string {
  return path
    .split(".")
    .map((segment) => segment.replaceAll("_", " "))
    .join(" · ");
}

export interface DraftRow {
  label: string;
  value: string;
  missing: boolean;
}

/** Turns a parsed ProfileDraft into display rows, without inventing values
 * for anything the extractor didn't return. */
export function draftToRows(draft: ProfileDraft): DraftRow[] {
  const missing = new Set(draft.missing_fields);
  const isMissing = (prefix: string) =>
    [...missing].some((m) => m === prefix || m.startsWith(`${prefix}.`));

  return [
    {
      label: "Age",
      value: draft.age != null ? String(draft.age) : "not extracted",
      missing: draft.age == null || isMissing("age"),
    },
    {
      label: "Job title",
      value: draft.job_title ?? "not extracted",
      missing: draft.job_title == null || isMissing("job_title"),
    },
    {
      label: "Job responsibility",
      value: draft.job_responsibility ?? "not extracted",
      missing: draft.job_responsibility == null || isMissing("job_responsibility"),
    },
    {
      label: "Education",
      value: draft.education ? formatEducation(draft.education) : "not extracted",
      missing: !draft.education || isMissing("education"),
    },
    {
      label: "Languages",
      value: formatLanguages(draft.languages),
      missing: !draft.languages || isMissing("languages"),
    },
    {
      label: "Work experience",
      value: formatExperience(draft.work_experience),
      missing: !draft.work_experience || isMissing("work_experience"),
    },
    {
      label: "Marital status",
      value: draft.marital_status ?? "not extracted",
      missing: draft.marital_status == null || isMissing("marital_status"),
    },
    {
      label: "Settlement funds",
      value: draft.current_available_funds != null ? formatFunds(draft.current_available_funds) : "not extracted",
      missing: draft.current_available_funds == null || isMissing("current_available_funds"),
    },
  ];
}
