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
      <div className="mx-auto max-w-[880px] px-[26px] pt-[34px] pb-20">
        <h3 className="m-0">What to do next</h3>
        <p className="mt-2.5 mb-[22px] text-[14px] text-[rgba(233,233,237,.6)]">
          Confirm your profile first — advice is generated from your CRS
          breakdown and eligibility results.
        </p>
        <Link href="/intake" className="btn btn-primary">
          Describe your situation
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[880px] px-[26px] pt-[34px] pb-20">
      <h3 className="m-0">What to do next</h3>
      <p className="mt-1.5 mb-6 text-[14px] text-[rgba(233,233,237,.6)]">
        Generated from your own CRS breakdown and eligibility results - not
        open-ended model output.
      </p>
      <div className="rounded-[14px] bg-[#161826] px-6 py-[22px] shadow-[var(--shadow-sm)]">
        {renderAdvice(advice)}
      </div>
      <p className="mt-[22px] mb-0 max-w-[70ch] text-[12px] text-[rgba(233,233,237,.45)]">
        This is not legal advice and does not replace IRCC tools or a licensed
        representative.
      </p>
    </div>
  );
}
