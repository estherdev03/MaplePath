"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useProfile } from "@/lib/profile-context";

const CORE_NAV_ITEMS = [
  { href: "/", label: "Home" },
  { href: "/intake", label: "Intake" },
  { href: "/confirm", label: "Confirm" },
] as const;

// These only have something to show once a profile has been confirmed —
// gated in the nav so they're not offered before that step.
const GATED_NAV_ITEMS = [
  { href: "/results", label: "Results" },
  { href: "/eligibility", label: "Eligibility" },
  { href: "/noc", label: "Occupation" },
  { href: "/advice", label: "Advice" },
  { href: "/simulator", label: "Simulator" },
] as const;

// Not part of the profile flow at all — a standalone retrieval-accuracy
// report. Always last in the nav and styled apart from it, so it doesn't
// read as another step in the user's journey.
const BENCHMARK_ITEM = { href: "/benchmark", label: "Benchmark" } as const;

export default function Header() {
  const pathname = usePathname();
  const { profile } = useProfile();
  const hasProfile = profile != null;
  const navItems = hasProfile
    ? [...CORE_NAV_ITEMS, ...GATED_NAV_ITEMS]
    : CORE_NAV_ITEMS;

  return (
    <header className="sticky top-0 z-20 flex flex-wrap items-center gap-x-[18px] gap-y-2.5 bg-[rgba(15,17,28,.92)] px-[22px] py-3 shadow-[0_1px_0_rgba(233,233,237,.1)] backdrop-blur-[8px]">
      <div className="mr-auto flex items-center gap-[9px]">
        <svg
          viewBox="0 0 24 24"
          width={22}
          height={22}
          fill="none"
          stroke="#9184d9"
          strokeWidth={1.6}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M12 3v18M12 8l5-3M12 13l-5-3M12 13l5-3" />
        </svg>
        <span className="text-[17px] font-medium tracking-[-.01em]">
          MaplePath
        </span>
      </div>
      <nav className="flex flex-wrap items-center gap-1">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`inline-block rounded-lg border-none px-[11px] py-1.5 font-[family-name:var(--font-body)] text-[13px] font-medium ${
                active
                  ? "bg-[rgba(145,132,217,.18)] text-[#b5abfc]"
                  : "bg-transparent text-[rgba(233,233,237,.68)]"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <Link
        href={BENCHMARK_ITEM.href}
        title="Retrieval evaluation report — not part of your profile"
        className="btn btn-secondary text-[12px]"
      >
        {BENCHMARK_ITEM.label}
      </Link>
    </header>
  );
}
