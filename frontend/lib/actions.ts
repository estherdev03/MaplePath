"use server";

import { ApiError, completeProfile, parseProfile, simulateCrs } from "./api";
import { buildConfirmPayload } from "./confirm-form";
import type { CrsSimulateResponse, ProfileDraft, UserProfile } from "./types";

export interface ActionState {
  error?: string;
}

export interface ParseActionState extends ActionState {
  draft?: ProfileDraft;
  draftText?: string;
}

export async function parseProfileAction(
  _prev: ParseActionState,
  formData: FormData
): Promise<ParseActionState> {
  const text = String(formData.get("text") ?? "").trim();
  if (!text) {
    return { error: "Describe your situation before extracting a profile." };
  }

  try {
    const draft = await parseProfile(text);
    return { draft, draftText: text };
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message };
    throw e;
  }
}

export interface CompleteActionState extends ActionState {
  profile?: UserProfile;
}

export async function completeProfileAction(
  _prev: CompleteActionState,
  formData: FormData
): Promise<CompleteActionState> {
  let payload;
  try {
    payload = buildConfirmPayload(formData);
  } catch (e) {
    return { error: e instanceof Error ? e.message : "Invalid form input." };
  }

  try {
    const profile = await completeProfile(payload);
    return { profile };
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message };
    throw e;
  }
}

export async function simulateCrsAction(
  profile: UserProfile
): Promise<CrsSimulateResponse | { error: string }> {
  try {
    return await simulateCrs(profile);
  } catch (e) {
    if (e instanceof ApiError) return { error: e.message };
    throw e;
  }
}
