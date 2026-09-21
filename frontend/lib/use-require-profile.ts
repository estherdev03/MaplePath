"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useProfile } from "./profile-context";
import type { UserProfile } from "./types";

/** Every route besides home/intake/confirm assumes a confirmed profile —
 * bounce back to home instead of rendering a page with nothing to show. */
export function useRequireProfile(): UserProfile | undefined {
  const router = useRouter();
  const { profile } = useProfile();

  useEffect(() => {
    if (!profile) router.replace("/");
  }, [profile, router]);

  return profile;
}
