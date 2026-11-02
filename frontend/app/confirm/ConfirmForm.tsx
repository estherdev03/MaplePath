"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useActionState, useEffect, useRef, useState } from "react";
import { completeProfileAction, type CompleteActionState } from "@/lib/actions";
import { EDUCATION_OPTIONS, ENGLISH_TEST_OPTIONS, FRENCH_TEST_OPTIONS } from "@/lib/confirm-form";
import { applySnapshot, snapshotForm, type FormSnapshot } from "@/lib/form-persist";
import type { MaritalStatus } from "@/lib/types";
import { useProfile } from "@/lib/profile-context";

const initialState: CompleteActionState = {};

export default function ConfirmForm() {
  const router = useRouter();
  const { draft, setProfile, confirmSnapshot, setConfirmSnapshot } = useProfile();
  const [state, formAction, pending] = useActionState(completeProfileAction, initialState);
  const formRef = useRef<HTMLFormElement>(null);
  const restoredSnapshot = useRef<FormSnapshot | null>(null);
  const appliedSnapshot = useRef(false);

  const [maritalStatus, setMaritalStatus] = useState(draft?.marital_status ?? "single");
  const [hasEnglish, setHasEnglish] = useState(draft?.languages?.english != null || !draft);
  const [hasFrench, setHasFrench] = useState(draft?.languages?.french != null);
  const [firstLanguage, setFirstLanguage] = useState<"english" | "french">(
    draft?.languages?.french?.is_first_language ? "french" : "english"
  );
  const [educationLocation, setEducationLocation] = useState(
    draft?.education?.from_canada ? "canada" : "outside"
  );
  const [canadaEducationCompleted, setCanadaEducationCompleted] = useState(
    draft?.canada_education?.completed ?? false
  );
  const [hasSpouseEducation, setHasSpouseEducation] = useState(!!draft?.spouse?.education);
  const [spouseHasEnglish, setSpouseHasEnglish] = useState(
    draft?.spouse?.languages?.english != null
  );
  const [spouseHasFrench, setSpouseHasFrench] = useState(
    draft?.spouse?.languages?.french != null
  );
  const [spouseEducationLocation, setSpouseEducationLocation] = useState(
    draft?.spouse?.education?.from_canada ? "canada" : "outside"
  );

  const en = draft?.languages?.english;
  const fr = draft?.languages?.french;
  const wx = draft?.work_experience;
  const edu = draft?.education;
  const canEdu = draft?.canada_education;

  // Restores whatever the user had mid-edit before navigating away — first
  // the toggles that control which sections are visible, then (once that
  // render has committed and the matching fields exist) the plain field
  // values on top of them. Runs once; later toggle changes are the user's
  // own, not stale saved state, so they're left alone.
  useEffect(() => {
    const saved = confirmSnapshot;
    if (!saved) return;
    restoredSnapshot.current = saved;
    // Deferred to a microtask so these are callback-scoped rather than
    // synchronous effect-body writes — still resolves before paint.
    queueMicrotask(() => {
      if (typeof saved.marital_status === "string") setMaritalStatus(saved.marital_status as MaritalStatus);
      if (typeof saved.has_english === "boolean") setHasEnglish(saved.has_english);
      if (typeof saved.has_french === "boolean") setHasFrench(saved.has_french);
      if (typeof saved.first_language === "string") setFirstLanguage(saved.first_language as "english" | "french");
      if (typeof saved.education_location === "string") setEducationLocation(saved.education_location as "canada" | "outside");
      if (typeof saved.canada_education_completed === "boolean") setCanadaEducationCompleted(saved.canada_education_completed);
      if (typeof saved.has_spouse_education === "boolean") setHasSpouseEducation(saved.has_spouse_education);
      if (typeof saved.spouse_has_english === "boolean") setSpouseHasEnglish(saved.spouse_has_english);
      if (typeof saved.spouse_has_french === "boolean") setSpouseHasFrench(saved.spouse_has_french);
      if (typeof saved.spouse_education_location === "string") {
        setSpouseEducationLocation(saved.spouse_education_location as "canada" | "outside");
      }
    });
  }, []);

  useEffect(() => {
    if (appliedSnapshot.current || !restoredSnapshot.current || !formRef.current) return;
    applySnapshot(formRef.current, restoredSnapshot.current);
    appliedSnapshot.current = true;
  }, [
    maritalStatus,
    hasEnglish,
    hasFrench,
    firstLanguage,
    educationLocation,
    canadaEducationCompleted,
    hasSpouseEducation,
    spouseHasEnglish,
    spouseHasFrench,
    spouseEducationLocation,
  ]);

  const persist = () => {
    if (formRef.current) setConfirmSnapshot(snapshotForm(formRef.current));
  };

  // Server actions can't redirect to a page that reads client-only state, so
  // the confirmed profile is handed to the client here and the navigation
  // happens after it's in context.
  useEffect(() => {
    if (state.profile) {
      setProfile(state.profile);
      router.push("/results");
    }
  }, [state.profile, setProfile, router]);

  return (
    <form
      ref={formRef}
      action={formAction}
      onChange={persist}
      className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20"
    >
      <div className="flex flex-wrap items-baseline gap-3">
        <h3 className="m-0">Confirm your profile</h3>
        <span className="tag tag-outline">POST /profile/complete</span>
      </div>
      <p className="mt-1.5 mb-[26px] text-[14px] text-[rgba(233,233,237,.6)]">
        {draft
          ? "Pre-filled from the description you entered. Anything you change is re-validated by the same rules the scorer uses."
          : "Fill in your details below. Every field is re-validated by the same rules the scorer uses."}
      </p>

      <div className="flex flex-col gap-[26px]">
        <div>
          <h6 className="mb-3 text-[#9184d9]">Applicant</h6>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
            <div className="field">
              <label htmlFor="age">Age</label>
              <input id="age" name="age" type="number" className="input" defaultValue={draft?.age ?? undefined} required />
            </div>
            <div className="field">
              <label>Marital status</label>
              <div className="seg w-full">
                <label className="seg-opt flex-1 justify-center">
                  <input
                    type="radio"
                    name="marital_status"
                    value="single"
                    checked={maritalStatus === "single"}
                    onChange={() => setMaritalStatus("single")}
                  />
                  Single
                </label>
                <label className="seg-opt flex-1 justify-center">
                  <input
                    type="radio"
                    name="marital_status"
                    value="married"
                    checked={maritalStatus === "married"}
                    onChange={() => setMaritalStatus("married")}
                  />
                  Married
                </label>
              </div>
            </div>
            <div className="field">
              <label htmlFor="current_available_funds">Settlement funds (CAD)</label>
              <input
                id="current_available_funds"
                name="current_available_funds"
                type="number"
                className="input"
                defaultValue={draft?.current_available_funds ?? 0}
                required
              />
            </div>
          </div>
        </div>

        <div>
          <h6 className="mb-3 text-[#9184d9]">Occupation</h6>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
            <div className="field">
              <label htmlFor="job_title">Job title</label>
              <input
                id="job_title"
                name="job_title"
                className="input"
                defaultValue={draft?.job_title ?? ""}
                required
              />
            </div>
            <div className="field col-span-2">
              <label htmlFor="job_responsibility">Main responsibilities — used for NOC classification</label>
              <textarea
                id="job_responsibility"
                name="job_responsibility"
                className="input min-h-9"
                defaultValue={draft?.job_responsibility ?? ""}
                required
              />
            </div>
          </div>
          <label className="radio mt-3">
            <input type="checkbox" name="have_canada_job_offer" />
            <span className="dot" />
            I have a Canadian job offer of at least one year
          </label>
        </div>

        <div>
          <h6 className="mb-3 text-[#9184d9]">Language</h6>
          <label className="radio mb-3">
            <input
              type="checkbox"
              name="has_english"
              checked={hasEnglish}
              onChange={(e) => setHasEnglish(e.target.checked)}
            />
            <span className="dot" />
            English test
          </label>
          {hasEnglish && (
            <div className="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-3.5">
              <div className="field">
                <label htmlFor="english_test">Test</label>
                <select id="english_test" name="english_test" className="input" defaultValue={en?.test_name ?? "ielts"}>
                  {ENGLISH_TEST_OPTIONS.map((t) => (
                    <option key={t} value={t}>
                      {t.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label htmlFor="english_speaking">Speaking</label>
                <input
                  id="english_speaking"
                  name="english_speaking"
                  className="input"
                  type="number"
                  step="0.5"
                  defaultValue={en?.detail_scores?.speaking ?? undefined}
                  placeholder="required"
                />
              </div>
              <div className="field">
                <label htmlFor="english_writing">Writing</label>
                <input
                  id="english_writing"
                  name="english_writing"
                  className="input"
                  type="number"
                  step="0.5"
                  defaultValue={en?.detail_scores?.writing ?? undefined}
                  placeholder="required"
                />
              </div>
              <div className="field">
                <label htmlFor="english_listening">Listening</label>
                <input
                  id="english_listening"
                  name="english_listening"
                  className="input"
                  type="number"
                  step="0.5"
                  defaultValue={en?.detail_scores?.listening ?? undefined}
                  placeholder="required"
                />
              </div>
              <div className="field">
                <label htmlFor="english_reading">Reading</label>
                <input
                  id="english_reading"
                  name="english_reading"
                  className="input"
                  type="number"
                  step="0.5"
                  defaultValue={en?.detail_scores?.reading ?? undefined}
                  placeholder="required"
                />
              </div>
            </div>
          )}

          <label className="radio mx-0 mt-4 mb-3">
            <input
              type="checkbox"
              name="has_french"
              checked={hasFrench}
              onChange={(e) => setHasFrench(e.target.checked)}
            />
            <span className="dot" />
            French test
          </label>
          {hasFrench && (
            <div className="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-3.5">
              <div className="field">
                <label htmlFor="french_test">Test</label>
                <select id="french_test" name="french_test" className="input" defaultValue={fr?.test_name ?? "tef"}>
                  {FRENCH_TEST_OPTIONS.map((t) => (
                    <option key={t} value={t}>
                      {t.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label htmlFor="french_speaking">Speaking</label>
                <input
                  id="french_speaking"
                  name="french_speaking"
                  className="input"
                  type="number"
                  defaultValue={fr?.detail_scores?.speaking ?? undefined}
                  placeholder="required"
                />
              </div>
              <div className="field">
                <label htmlFor="french_writing">Writing</label>
                <input
                  id="french_writing"
                  name="french_writing"
                  className="input"
                  type="number"
                  defaultValue={fr?.detail_scores?.writing ?? undefined}
                  placeholder="required"
                />
              </div>
              <div className="field">
                <label htmlFor="french_listening">Listening</label>
                <input
                  id="french_listening"
                  name="french_listening"
                  className="input"
                  type="number"
                  defaultValue={fr?.detail_scores?.listening ?? undefined}
                  placeholder="required"
                />
              </div>
              <div className="field">
                <label htmlFor="french_reading">Reading</label>
                <input
                  id="french_reading"
                  name="french_reading"
                  className="input"
                  type="number"
                  defaultValue={fr?.detail_scores?.reading ?? undefined}
                  placeholder="required"
                />
              </div>
            </div>
          )}

          {hasEnglish && hasFrench && (
            <div className="field mt-3.5 max-w-[260px]">
              <label>First official language</label>
              <div className="seg w-full">
                <label className="seg-opt flex-1 justify-center">
                  <input
                    type="radio"
                    name="first_language"
                    value="english"
                    checked={firstLanguage === "english"}
                    onChange={() => setFirstLanguage("english")}
                  />
                  English
                </label>
                <label className="seg-opt flex-1 justify-center">
                  <input
                    type="radio"
                    name="first_language"
                    value="french"
                    checked={firstLanguage === "french"}
                    onChange={() => setFirstLanguage("french")}
                  />
                  French
                </label>
              </div>
            </div>
          )}
        </div>

        <div>
          <h6 className="mb-3 text-[#9184d9]">Work experience — full-time years, within the last ten</h6>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(170px,1fr))] gap-3.5">
            <div className="field">
              <label htmlFor="work_foreign_years">Foreign</label>
              <input id="work_foreign_years" name="work_foreign_years" type="number" step="0.5" className="input" defaultValue={wx?.foreign_years ?? 0} />
            </div>
            <div className="field">
              <label htmlFor="work_canada_years">In Canada</label>
              <input id="work_canada_years" name="work_canada_years" type="number" step="0.5" className="input" defaultValue={wx?.canada_years ?? 0} />
            </div>
            <div className="field">
              <label htmlFor="work_continuous_canada_years">Continuous full-time, Canada</label>
              <input
                id="work_continuous_canada_years"
                name="work_continuous_canada_years"
                type="number"
                step="0.5"
                className="input"
                defaultValue={wx?.continuous_fulltime_canada_years ?? 0}
              />
            </div>
            <div className="field">
              <label htmlFor="work_canada_within_3_years">Canada, within 3 years</label>
              <input
                id="work_canada_within_3_years"
                name="work_canada_within_3_years"
                type="number"
                step="0.5"
                className="input"
                defaultValue={wx?.canada_work_exp_within_3_years ?? 0}
              />
            </div>
            <div className="field">
              <label htmlFor="work_trade_within_5_years">Skilled trade, within 5 years</label>
              <input
                id="work_trade_within_5_years"
                name="work_trade_within_5_years"
                type="number"
                step="0.5"
                className="input"
                defaultValue={wx?.trade_exp_within_5_years ?? 0}
              />
            </div>
            <div className="field">
              <label htmlFor="work_continuous_foreign_years">Continuous full-time, foreign</label>
              <input
                id="work_continuous_foreign_years"
                name="work_continuous_foreign_years"
                type="number"
                step="0.5"
                className="input"
                defaultValue={wx?.continuous_fulltime_foreign_years ?? 0}
              />
            </div>
            <div className="field">
              <label htmlFor="work_alberta_years">Alberta</label>
              <input id="work_alberta_years" name="work_alberta_years" type="number" step="0.5" className="input" defaultValue={wx?.alberta_years ?? 0} />
            </div>
          </div>
          <p className="mt-2 mb-0 text-[12px] text-[rgba(233,233,237,.5)]">
            Validated: continuous years cannot exceed total years, and Canada-within-3 cannot exceed total Canadian
            years.
          </p>
        </div>

        <div>
          <h6 className="mb-3 text-[#9184d9]">Education &amp; adaptability</h6>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
            <div className="field">
              <label htmlFor="education_level">Highest level</label>
              <select id="education_level" name="education_level" className="input" defaultValue={edu?.level ?? "bachelor"}>
                {EDUCATION_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Where was it earned?</label>
              <div className="seg w-full">
                <label className="seg-opt flex-1 justify-center">
                  <input
                    type="radio"
                    name="education_location"
                    value="outside"
                    checked={educationLocation === "outside"}
                    onChange={() => setEducationLocation("outside")}
                  />
                  Outside Canada
                </label>
                <label className="seg-opt flex-1 justify-center">
                  <input
                    type="radio"
                    name="education_location"
                    value="canada"
                    checked={educationLocation === "canada"}
                    onChange={() => setEducationLocation("canada")}
                  />
                  Canada
                </label>
              </div>
            </div>
          </div>
          {educationLocation === "outside" && (
            <label className="radio mt-3">
              <input type="checkbox" name="education_eca_completed" defaultChecked={edu?.eca_completed ?? false} />
              <span className="dot" />
              Educational Credential Assessment (ECA) completed
            </label>
          )}

          <div className="mt-4.5">
            <label className="radio">
              <input
                type="checkbox"
                name="canada_education_completed"
                checked={canadaEducationCompleted}
                onChange={(e) => setCanadaEducationCompleted(e.target.checked)}
              />
              <span className="dot" />
              Completed a Canadian post-secondary credential
            </label>
            {canadaEducationCompleted && (
              <div className="field mt-2.5 max-w-[220px]">
                <label htmlFor="canada_education_years">Canadian credential years</label>
                <input
                  id="canada_education_years"
                  name="canada_education_years"
                  type="number"
                  step="0.5"
                  className="input"
                  defaultValue={canEdu?.credential_years ?? 0}
                />
              </div>
            )}
          </div>

          <div className="mt-4 flex flex-wrap gap-4">
            <label className="radio">
              <input type="checkbox" name="provincial_nomination" defaultChecked={draft?.provincial_nomination ?? false} />
              <span className="dot" />
              Provincial nomination
            </label>
            <label className="radio">
              <input type="checkbox" name="sibling_in_can" defaultChecked={draft?.sibling_in_can ?? false} />
              <span className="dot" />
              Sibling in Canada
            </label>
            <label className="radio">
              <input type="checkbox" name="relative_in_can" defaultChecked={draft?.relative_in_can ?? false} />
              <span className="dot" />
              Other relative in Canada
            </label>
            <label className="radio">
              <input type="checkbox" name="education_has_coq" />
              <span className="dot" />
              Certificate of qualification (trades)
            </label>
          </div>
        </div>

        {maritalStatus === "married" && (
          <div>
            <h6 className="mb-3 text-[#9184d9]">Spouse or common-law partner</h6>
            <label className="radio mb-3">
              <input
                type="checkbox"
                name="has_spouse_education"
                checked={hasSpouseEducation}
                onChange={(e) => setHasSpouseEducation(e.target.checked)}
              />
              <span className="dot" />
              Spouse has a post-secondary credential
            </label>
            {hasSpouseEducation && (
              <div className="mb-3 grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
                <div className="field">
                  <label htmlFor="spouse_education_level">Highest level</label>
                  <select id="spouse_education_level" name="spouse_education_level" className="input" defaultValue="bachelor">
                    {EDUCATION_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>Where was it earned?</label>
                  <div className="seg w-full">
                    <label className="seg-opt flex-1 justify-center">
                      <input
                        type="radio"
                        name="spouse_education_location"
                        value="outside"
                        checked={spouseEducationLocation === "outside"}
                        onChange={() => setSpouseEducationLocation("outside")}
                      />
                      Outside Canada
                    </label>
                    <label className="seg-opt flex-1 justify-center">
                      <input
                        type="radio"
                        name="spouse_education_location"
                        value="canada"
                        checked={spouseEducationLocation === "canada"}
                        onChange={() => setSpouseEducationLocation("canada")}
                      />
                      Canada
                    </label>
                  </div>
                </div>
                {spouseEducationLocation === "outside" && (
                  <label className="radio">
                    <input type="checkbox" name="spouse_education_eca_completed" />
                    <span className="dot" />
                    ECA completed
                  </label>
                )}
              </div>
            )}

            <label className="radio mb-3">
              <input
                type="checkbox"
                name="spouse_has_english"
                checked={spouseHasEnglish}
                onChange={(e) => setSpouseHasEnglish(e.target.checked)}
              />
              <span className="dot" />
              Spouse has an English test
            </label>
            {spouseHasEnglish && (
              <div className="mb-3 grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-3.5">
                <div className="field">
                  <label htmlFor="spouse_english_test">Test</label>
                  <select id="spouse_english_test" name="spouse_english_test" className="input" defaultValue="ielts">
                    {ENGLISH_TEST_OPTIONS.map((t) => (
                      <option key={t} value={t}>
                        {t.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="spouse_english_speaking">Speaking</label>
                  <input id="spouse_english_speaking" name="spouse_english_speaking" type="number" step="0.5" className="input" placeholder="required" />
                </div>
                <div className="field">
                  <label htmlFor="spouse_english_writing">Writing</label>
                  <input id="spouse_english_writing" name="spouse_english_writing" type="number" step="0.5" className="input" placeholder="required" />
                </div>
                <div className="field">
                  <label htmlFor="spouse_english_listening">Listening</label>
                  <input id="spouse_english_listening" name="spouse_english_listening" type="number" step="0.5" className="input" placeholder="required" />
                </div>
                <div className="field">
                  <label htmlFor="spouse_english_reading">Reading</label>
                  <input id="spouse_english_reading" name="spouse_english_reading" type="number" step="0.5" className="input" placeholder="required" />
                </div>
              </div>
            )}

            <label className="radio mb-3">
              <input
                type="checkbox"
                name="spouse_has_french"
                checked={spouseHasFrench}
                onChange={(e) => setSpouseHasFrench(e.target.checked)}
              />
              <span className="dot" />
              Spouse has a French test
            </label>
            {spouseHasFrench && (
              <div className="mb-3 grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-3.5">
                <div className="field">
                  <label htmlFor="spouse_french_test">Test</label>
                  <select id="spouse_french_test" name="spouse_french_test" className="input" defaultValue="tef">
                    {FRENCH_TEST_OPTIONS.map((t) => (
                      <option key={t} value={t}>
                        {t.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label htmlFor="spouse_french_speaking">Speaking</label>
                  <input id="spouse_french_speaking" name="spouse_french_speaking" type="number" className="input" placeholder="required" />
                </div>
                <div className="field">
                  <label htmlFor="spouse_french_writing">Writing</label>
                  <input id="spouse_french_writing" name="spouse_french_writing" type="number" className="input" placeholder="required" />
                </div>
                <div className="field">
                  <label htmlFor="spouse_french_listening">Listening</label>
                  <input id="spouse_french_listening" name="spouse_french_listening" type="number" className="input" placeholder="required" />
                </div>
                <div className="field">
                  <label htmlFor="spouse_french_reading">Reading</label>
                  <input id="spouse_french_reading" name="spouse_french_reading" type="number" className="input" placeholder="required" />
                </div>
              </div>
            )}

            <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-3.5">
              <div className="field">
                <label htmlFor="spouse_canadian_experience">Spouse Canadian work experience (years)</label>
                <input
                  id="spouse_canadian_experience"
                  name="spouse_canadian_experience"
                  type="number"
                  step="0.5"
                  className="input"
                  defaultValue={draft?.spouse?.canadian_experience ?? 0}
                />
              </div>
            </div>
            <label className="radio mt-3">
              <input type="checkbox" name="spouse_relative_in_can" defaultChecked={draft?.spouse?.relative_in_can ?? false} />
              <span className="dot" />
              Spouse has a relative in Canada
            </label>
          </div>
        )}
      </div>

      {state.error && (
        <p className="mt-5 mb-0 text-[13.5px] text-[#f2a3a3]">{state.error}</p>
      )}

      <div className="mt-[30px] flex flex-wrap gap-2.5 pt-5 [background:linear-gradient(to_right,transparent,rgba(233,233,237,.16)_48px,rgba(233,233,237,.16)_calc(100%_-_48px),transparent)_no-repeat_top_/_100%_1px]">
        <button type="submit" className="btn btn-primary" disabled={pending}>
          {pending ? "Scoring…" : "Confirm and score"}
        </button>
        <Link href="/intake" className="btn btn-secondary">
          Edit my description
        </Link>
      </div>
    </form>
  );
}
