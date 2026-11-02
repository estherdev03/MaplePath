"use client";

import Link from "next/link";
import { useRequireProfile } from "@/lib/use-require-profile";
import NocView from "./NocView";

export default function NocPage() {
  const profile = useRequireProfile();

  if (!profile) return null;

  const occupation = profile.occupation;

  if (!occupation) {
    return (
      <div className="mx-auto max-w-[1000px] px-[26px] pt-[34px] pb-20">
        <h3 className="m-0">Occupation match</h3>
        <p className="mt-2.5 mb-[22px] text-[14px] text-[rgba(233,233,237,.6)]">
          Confirm your profile first — the occupation classifier runs once your job title and duties are submitted.
        </p>
        <Link href="/intake" className="btn btn-primary">
          Describe your situation
        </Link>
      </div>
    );
  }

  return <NocView occupation={occupation} />;
}
