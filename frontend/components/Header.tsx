"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_ITEMS } from "@/lib/mock-data";
import { useDevPanel } from "./DevPanelContext";

export default function Header() {
  const pathname = usePathname();
  const { devOpen, toggleDev } = useDevPanel();

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
      <div style={{ display: "flex", alignItems: "center", gap: 9, marginRight: "auto" }}>
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
        <span style={{ fontSize: 17, fontWeight: 500, letterSpacing: "-.01em" }}>MaplePath</span>
        <span className="tag tag-neutral" style={{ marginLeft: 4 }}>
          mockup
        </span>
      </div>
      <nav style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
        {NAV_ITEMS.map((item) => {
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
      <button type="button" className="btn btn-secondary" onClick={toggleDev} style={{ fontSize: 12 }}>
        {devOpen ? "Hide internals" : "Developer panel"}
      </button>
    </header>
  );
}
