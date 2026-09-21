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
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
        <h3 style={{ margin: 0 }}>Occupation match</h3>
        <p style={{ margin: "10px 0 22px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
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
