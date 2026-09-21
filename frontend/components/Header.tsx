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
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 20,
        display: "flex",
        flexWrap: "wrap",
        alignItems: "center",
        gap: "10px 18px",
        padding: "12px 22px",
        background: "rgba(15,17,28,.92)",
        backdropFilter: "blur(8px)",
        boxShadow: "0 1px 0 rgba(233,233,237,.1)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 9,
          marginRight: "auto",
        }}
      >
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
        <span
          style={{ fontSize: 17, fontWeight: 500, letterSpacing: "-.01em" }}
        >
          MaplePath
        </span>
        <span className="tag tag-neutral" style={{ marginLeft: 4 }}>
          demo
        </span>
      </div>
      <nav
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: 4,
        }}
      >
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                border: "none",
                background: active ? "rgba(145,132,217,.18)" : "transparent",
                color: active ? "#b5abfc" : "rgba(233,233,237,.68)",
                fontFamily: "'Inter',system-ui,sans-serif",
                fontWeight: 500,
                fontSize: 13,
                padding: "6px 11px",
                borderRadius: 8,
                display: "inline-block",
              }}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <Link
        href={BENCHMARK_ITEM.href}
        title="Retrieval evaluation report — not part of your profile"
        className="btn btn-secondary"
        style={{ fontSize: 12 }}
      >
        {BENCHMARK_ITEM.label}
      </Link>
    </header>
  );
}
