"use client";

// In-memory only, on purpose: this is the entire "session" for the app now.
// It lives in a client component's state, so it survives client-side
// navigation between routes (the layout stays mounted) but is gone the
// instant the page is refreshed or reopened — there is no cookie, storage,
// or server-side store backing it.
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import type { FormSnapshot } from "./form-persist";
import type { ProfileDraft, UserProfile } from "./types";

export interface ProfileState {
  draftText?: string;
  draft?: ProfileDraft;
  profile?: UserProfile;
  // Mid-edit, unsubmitted input for the intake/confirm forms — kept here
  // (rather than storage) so it survives client-side navigation between
  // routes but is gone on refresh, same as the rest of this "session".
  intakeText?: string;
  confirmSnapshot?: FormSnapshot;
}

interface ProfileContextValue extends ProfileState {
  setDraft: (draftText: string, draft: ProfileDraft) => void;
  setProfile: (profile: UserProfile) => void;
  setIntakeText: (intakeText: string) => void;
  setConfirmSnapshot: (snapshot: FormSnapshot | undefined) => void;
}

const ProfileContext = createContext<ProfileContextValue | null>(null);

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ProfileState>({});

  const setDraft = useCallback((draftText: string, draft: ProfileDraft) => {
    setState((s) => ({ ...s, draftText, draft }));
  }, []);

  const setProfile = useCallback((profile: UserProfile) => {
    setState((s) => ({ ...s, profile }));
  }, []);

  const setIntakeText = useCallback((intakeText: string) => {
    setState((s) => ({ ...s, intakeText }));
  }, []);

  const setConfirmSnapshot = useCallback((confirmSnapshot: FormSnapshot | undefined) => {
    setState((s) => ({ ...s, confirmSnapshot }));
  }, []);

  const value = useMemo<ProfileContextValue>(
    () => ({ ...state, setDraft, setProfile, setIntakeText, setConfirmSnapshot }),
    [state, setDraft, setProfile, setIntakeText, setConfirmSnapshot]
  );

  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}

export function useProfile() {
  const ctx = useContext(ProfileContext);
  if (!ctx) throw new Error("useProfile must be used within a ProfileProvider");
  return ctx;
}
