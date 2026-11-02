"use client";

import { useMemo } from "react";
import { useRequireProfile } from "@/lib/use-require-profile";
import { profileToSimProfile } from "@/lib/sim-profile";
import SimulatorView from "./SimulatorView";

export default function SimulatorPage() {
  const profile = useRequireProfile();
  const initial = useMemo(() => (profile ? profileToSimProfile(profile) : null), [profile]);

  if (!profile || !initial || !profile.crs_score) return null;

  return <SimulatorView profile={profile} initial={initial} baseline={profile.crs_score} />;
}
