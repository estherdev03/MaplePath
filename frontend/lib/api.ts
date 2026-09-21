// Server-only fetch helpers for the MaplePath FastAPI backend. Never import
// this from a "use client" component — call it from Server Components or
// Server Actions instead, and pass the result down as props.
import type {
  CrsSimulateResponse,
  EvaluateResponse,
  ProfileConfirmFormPayload,
  ProfileDraft,
  UserProfile,
} from "./types";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// fetch() throws (rather than resolving with a Response) when the backend
// is unreachable — surface that the same way as an HTTP error so callers
// only ever need to handle ApiError, instead of crashing the page/action.
async function safeFetch(url: URL, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, init);
  } catch {
    throw new ApiError(0, "Could not reach the MaplePath API. Is the backend running?");
  }
}

// The backend's own ValueErrors (e.g. from the profile graph) surface as
// Pydantic's raw ValidationError.__str__() dump — field path, indented
// message, then an indented pydantic.dev doc link. Pull out just the
// messages so the app doesn't show that dump to the user.
function formatPydanticDump(detail: string): string | null {
  const messages = [...detail.matchAll(/^ {2}(?! ).+$/gm)]
    .map((m) => m[0].trim().replace(/^Value error, /, "").replace(/\s*\[type=.*$/, ""))
    .filter(Boolean);
  return messages.length > 0 ? messages.join(" ") : null;
}

function formatDetail(detail: unknown): string {
  if (typeof detail === "string") return formatPydanticDump(detail) ?? detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const loc = Array.isArray(d?.loc) ? d.loc.join(".") : "field";
        return `${loc}: ${d?.msg ?? "invalid value"}`;
      })
      .join("; ");
  }
  return "Request failed";
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = formatDetail(body.detail);
    } catch {
      // response wasn't JSON; keep statusText
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export async function parseProfile(text: string): Promise<ProfileDraft> {
  const url = new URL("/profile/parse", API_URL);
  url.searchParams.set("profile_text", text);
  const res = await safeFetch(url, { method: "POST", cache: "no-store" });
  const body = await handle<{ result: ProfileDraft }>(res);
  return body.result;
}

export async function completeProfile(
  payload: ProfileConfirmFormPayload
): Promise<UserProfile> {
  const res = await safeFetch(new URL("/profile/complete", API_URL), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
  const body = await handle<{ result: UserProfile }>(res);
  return body.result;
}

export async function simulateCrs(
  profile: UserProfile
): Promise<CrsSimulateResponse> {
  const res = await safeFetch(new URL("/crs/simulate", API_URL), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
    cache: "no-store",
  });
  return handle<CrsSimulateResponse>(res);
}

export async function getEvaluation(): Promise<EvaluateResponse> {
  const res = await safeFetch(new URL("/evaluate", API_URL), {
    // The evaluation run embeds + reranks 84 labelled examples; cache it
    // briefly instead of re-running the whole benchmark on every page view.
    next: { revalidate: 300 },
  });
  return handle<EvaluateResponse>(res);
}
