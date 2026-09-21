"use client";

import { useMemo } from "react";
import { useRequireProfile } from "@/lib/use-require-profile";
import { profileToSimProfile } from "@/lib/sim-profile";
import SimulatorView from "./SimulatorView";

export default function SimulatorPage() {
  const profile = useRequireProfile();
  const initial = useMemo(() => profileToSimProfile(profile), [profile]);
  const confirmedTotal = profile?.crs_score?.total ?? null;

  if (!profile) return null;

  return <SimulatorView initial={initial} confirmedTotal={confirmedTotal} />;
}
