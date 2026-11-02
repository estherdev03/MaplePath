"use client";

import Link from "next/link";
import { useActionState, useEffect, useRef } from "react";
import { parseProfileAction, type ParseActionState } from "@/lib/actions";
import { draftToRows } from "@/lib/format";
import { useProfile } from "@/lib/profile-context";

const initialState: ParseActionState = {};

const EXAMPLE_TEXT =
  "I'm 29 years old. I've worked full-time as a backend software developer for 3 years in Vietnam, and I've been working full-time in the same role for 1 year in Toronto, Canada on a work permit. My day-to-day work is designing and building REST APIs, data models, and deployment pipelines for a SaaS product. I have a Master's degree in computer science, and my Educational Credential Assessment (ECA) is complete. My IELTS scores are 8 speaking, 7.5 writing, 8.5 listening, and 8 reading. I'm single, and I currently have about CAD 18,500 in savings.";

export default function IntakeForm() {
  const [state, formAction, pending] = useActionState(
    parseProfileAction,
    initialState,
  );
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const {
    draft: contextDraft,
    setDraft,
    intakeText,
    setIntakeText,
    setConfirmSnapshot,
  } = useProfile();
  // A fresh submission's result takes over once there is one, but the
  // previously extracted profile is still shown right after navigating back
  // to this page without re-submitting anything.
  const draft = state.draft ?? contextDraft;
  const rows = draft ? draftToRows(draft) : [];
  const missingCount = rows.filter((r) => r.missing).length;

  // A freshly parsed draft supersedes whatever was mid-edit on the confirm
  // form for a previous, unrelated description — drop that stale snapshot
  // so confirm rehydrates from this new draft instead.
  useEffect(() => {
    if (state.draft && state.draftText != null) {
      setDraft(state.draftText, state.draft);
      setConfirmSnapshot(undefined);
    }
  }, [state.draft, state.draftText, setDraft, setConfirmSnapshot]);

  const fillExample = () => {
    if (textareaRef.current) {
      textareaRef.current.value = EXAMPLE_TEXT;
      setIntakeText(EXAMPLE_TEXT);
    }
  };

  return (
    <div className="grid min-h-[calc(100vh-57px)] grid-cols-[repeat(auto-fit,minmax(340px,1fr))] gap-px bg-[rgba(233,233,237,.1)]">
      <div className="flex flex-col gap-4 bg-[#0f111c] p-[26px]">
        <div>
          <h4 className="m-0">Describe your situation</h4>
          <p className="mt-1 mb-0 text-[13px] text-[rgba(233,233,237,.55)]">
            POST /profile/parse · structured extraction
          </p>
        </div>
        <form
          action={formAction}
          className="field flex flex-col"
        >
          <div className="mb-[5px] flex items-baseline justify-between gap-3">
            <label
              htmlFor="text"
              className="text-[12px] text-[rgba(233,233,237,.7)]"
            >
              Your profile, in your own words
            </label>
            <button
              type="button"
              className="btn btn-ghost text-[12px]"
              onClick={fillExample}
            >
              Use example profile
            </button>
          </div>
          <textarea
            id="text"
            name="text"
            ref={textareaRef}
            className="input h-[300px] resize-y leading-[1.6]"
            defaultValue={intakeText}
            placeholder={EXAMPLE_TEXT}
            onChange={(e) => setIntakeText(e.target.value)}
          />
          <p className="mt-2 mb-0 text-[12.5px] text-[rgba(233,233,237,.55)]">
            Age, duties, work history, test scores, education, marital status,
            family in Canada, funds. Anything left out is reported as missing —
            never guessed.
          </p>
          {state.error && (
            <p className="mt-2.5 mb-0 text-[13px] text-[#f2a3a3]">
              {state.error}
            </p>
          )}
          <div className="mt-3 flex flex-wrap items-center gap-2.5">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={pending}
            >
              {pending ? "Extracting…" : "Extract my profile"}
            </button>
            <Link href="/confirm" className="btn btn-secondary">
              Skip - fill the form myself
            </Link>
            <span className="ml-auto text-[11.5px] text-[rgba(233,233,237,.45)]">
              Parsed into the fields on the right
            </span>
          </div>
        </form>
      </div>
      <div className="flex flex-col gap-3.5 bg-[#13151f] p-[26px]">
        <div className="flex items-baseline justify-between gap-3">
          <h4 className="m-0">Extracted profile</h4>
          {draft && (
            <span className="tag tag-accent">
              {rows.length - missingCount} of {rows.length} fields
            </span>
          )}
        </div>
        {!draft && (
          <p className="text-[13.5px] text-[rgba(233,233,237,.5)]">
            Extract a profile to see what was read from your description, field
            by field.
          </p>
        )}
        {draft && (
          <>
            <div className="flex flex-col gap-px overflow-hidden rounded-xl bg-[rgba(233,233,237,.08)]">
              {rows.map((row) => (
                <div
                  key={row.label}
                  className="flex items-center gap-2.5 bg-[#161826] px-3.5 py-[11px]"
                >
                  <span className="w-[38%] text-[13px] text-[rgba(233,233,237,.62)]">
                    {row.label}
                  </span>
                  <span
                    className={`flex-1 text-[13.5px] ${
                      row.missing ? "text-[#b5abfc]" : "text-[#e9e9ed]"
                    }`}
                  >
                    {row.value}
                  </span>
                  <span
                    className={`text-[10.5px] tracking-[.04em] uppercase ${
                      row.missing
                        ? "text-[#b5abfc]"
                        : "text-[rgba(233,233,237,.4)]"
                    }`}
                  >
                    {row.missing ? "missing" : "read"}
                  </span>
                </div>
              ))}
            </div>
            {draft.warnings.length > 0 && (
              <div className="rounded-xl bg-[#161826] px-4.5 py-4 shadow-[0_0_0_1px_#3f424d]">
                <div className="mb-2.5 text-[10px] tracking-[.1em] text-[rgba(233,233,237,.6)] uppercase">
                  Warning · {draft.warnings.length}
                </div>
                <div className="flex flex-col gap-2">
                  {draft.warnings.map((w) => (
                    <p
                      key={w}
                      className="m-0 text-[13px] text-[rgba(233,233,237,.72)]"
                    >
                      {w}
                    </p>
                  ))}
                </div>
              </div>
            )}
            <Link
              href="/confirm"
              className="btn btn-primary btn-block text-center"
            >
              Continue to the confirm form
            </Link>
            <p className="m-0 text-[11.5px] text-[rgba(233,233,237,.45)]">
              Nothing here is scored until you confirm it. You can correct any
              extracted value on the next step.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
