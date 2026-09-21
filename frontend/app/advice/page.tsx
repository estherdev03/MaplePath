"use client";

import Link from "next/link";
import { useRequireProfile } from "@/lib/use-require-profile";
import { renderAdvice } from "@/lib/advice-format";

export default function AdvicePage() {
  const profile = useRequireProfile();

  if (!profile) return null;

  const advice = profile.advice;

  if (!advice) {
    return (
      <div style={{ maxWidth: 880, margin: "0 auto", padding: "34px 26px 80px" }}>
        <h3 style={{ margin: 0 }}>What to do next</h3>
        <p style={{ margin: "10px 0 22px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
          Confirm your profile first — advice is generated from your CRS breakdown and eligibility results.
        </p>
        <Link href="/intake" className="btn btn-primary">
          Describe your situation
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 880, margin: "0 auto", padding: "34px 26px 80px" }}>
      <h3 style={{ margin: 0 }}>What to do next</h3>
      <p style={{ margin: "6px 0 24px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
        Generated from your own CRS breakdown and eligibility results — not open-ended model output.
      </p>
      <div
        style={{
          padding: "22px 24px",
          borderRadius: 14,
          background: "#161826",
          boxShadow: "var(--shadow-sm)",
        }}
      >
        {renderAdvice(advice)}
      </div>
      <p style={{ margin: "22px 0 0", fontSize: 12, color: "rgba(233,233,237,.45)", maxWidth: "70ch" }}>
        This is not legal advice and does not replace IRCC tools or a licensed representative.
      </p>
    </div>
  );
}
