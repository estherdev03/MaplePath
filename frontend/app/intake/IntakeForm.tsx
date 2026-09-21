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
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit,minmax(340px,1fr))",
        gap: 1,
        background: "rgba(233,233,237,.1)",
        minHeight: "calc(100vh - 57px)",
      }}
    >
      <div
        style={{
          background: "#0f111c",
          padding: 26,
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        <div>
          <h4 style={{ margin: 0 }}>Describe your situation</h4>
          <p
            style={{
              margin: "4px 0 0",
              fontSize: 13,
              color: "rgba(233,233,237,.55)",
            }}
          >
            POST /profile/parse · structured extraction
          </p>
        </div>
        <form
          action={formAction}
          className="field"
          style={{ display: "flex", flexDirection: "column" }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
              gap: 12,
              marginBottom: 5,
            }}
          >
            <label
              htmlFor="text"
              style={{ fontSize: 12, color: "rgba(233,233,237,.7)" }}
            >
              Your profile, in your own words
            </label>
            <button
              type="button"
              className="btn btn-ghost"
              style={{ fontSize: 12 }}
              onClick={fillExample}
            >
              Use example profile
            </button>
          </div>
          <textarea
            id="text"
            name="text"
            ref={textareaRef}
            className="input"
            style={{ height: 300, lineHeight: 1.6, resize: "vertical" }}
            defaultValue={intakeText}
            placeholder={EXAMPLE_TEXT}
            onChange={(e) => setIntakeText(e.target.value)}
          />
          <p
            style={{
              margin: "8px 0 0",
              fontSize: 12.5,
              color: "rgba(233,233,237,.55)",
            }}
          >
            Age, duties, work history, test scores, education, marital status,
            family in Canada, funds. Anything left out is reported as missing —
            never guessed.
          </p>
          {state.error && (
            <p style={{ margin: "10px 0 0", fontSize: 13, color: "#f2a3a3" }}>
              {state.error}
            </p>
          )}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
              alignItems: "center",
              marginTop: 12,
            }}
          >
            <button
              type="submit"
              className="btn btn-primary"
              disabled={pending}
            >
              {pending ? "Extracting…" : "Extract my profile"}
            </button>
            <Link href="/confirm" className="btn btn-secondary">
              Skip — fill the form myself
            </Link>
            <span
              style={{
                marginLeft: "auto",
                fontSize: 11.5,
                color: "rgba(233,233,237,.45)",
              }}
            >
              Parsed into the fields on the right
            </span>
          </div>
        </form>
      </div>
      <div
        style={{
          background: "#13151f",
          padding: 26,
          display: "flex",
          flexDirection: "column",
          gap: 14,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            gap: 12,
          }}
        >
          <h4 style={{ margin: 0 }}>Extracted profile</h4>
          {draft && (
            <span className="tag tag-accent">
              {rows.length - missingCount} of {rows.length} fields
            </span>
          )}
        </div>
        {!draft && (
          <p style={{ fontSize: 13.5, color: "rgba(233,233,237,.5)" }}>
            Extract a profile to see what was read from your description, field
            by field.
          </p>
        )}
        {draft && (
          <>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 1,
                borderRadius: 12,
                overflow: "hidden",
                background: "rgba(233,233,237,.08)",
              }}
            >
              {rows.map((row) => (
                <div
                  key={row.label}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    padding: "11px 14px",
                    background: "#161826",
                  }}
                >
                  <span
                    style={{
                      fontSize: 13,
                      color: "rgba(233,233,237,.62)",
                      width: "38%",
                    }}
                  >
                    {row.label}
                  </span>
                  <span
                    style={{
                      fontSize: 13.5,
                      flex: 1,
                      color: row.missing ? "#b5abfc" : "#e9e9ed",
                    }}
                  >
                    {row.value}
                  </span>
                  <span
                    style={{
                      fontSize: 10.5,
                      letterSpacing: ".04em",
                      textTransform: "uppercase",
                      color: row.missing ? "#b5abfc" : "rgba(233,233,237,.4)",
                    }}
                  >
                    {row.missing ? "missing" : "read"}
                  </span>
                </div>
              ))}
            </div>
            {draft.warnings.length > 0 && (
              <div
                style={{
                  borderRadius: 12,
                  padding: "16px 18px",
                  background: "#161826",
                  boxShadow: "0 0 0 1px #3f424d",
                }}
              >
                <div
                  style={{
                    fontSize: 10,
                    letterSpacing: ".1em",
                    textTransform: "uppercase",
                    color: "rgba(233,233,237,.6)",
                    marginBottom: 10,
                  }}
                >
                  Warning · {draft.warnings.length}
                </div>
                <div
                  style={{ display: "flex", flexDirection: "column", gap: 8 }}
                >
                  {draft.warnings.map((w) => (
                    <p
                      key={w}
                      style={{
                        margin: 0,
                        fontSize: 13,
                        color: "rgba(233,233,237,.72)",
                      }}
                    >
                      {w}
                    </p>
                  ))}
                </div>
              </div>
            )}
            <Link
              href="/confirm"
              className="btn btn-primary btn-block"
              style={{ textAlign: "center" }}
            >
              Continue to the confirm form
            </Link>
            <p
              style={{
                margin: 0,
                fontSize: 11.5,
                color: "rgba(233,233,237,.45)",
              }}
            >
              Nothing here is scored until you confirm it. You can correct any
              extracted value on the next step.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
