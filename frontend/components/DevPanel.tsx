"use client";

import { useDevPanel } from "./DevPanelContext";
import { TRACE, DEV_RESPONSE } from "@/lib/mock-data";

export default function DevPanel() {
  const { devOpen, toggleDev } = useDevPanel();
  if (!devOpen) return null;

  return (
    <aside
      style={{
        position: "fixed",
        right: 0,
        top: 0,
        bottom: 0,
        width: "min(430px,100%)",
        zIndex: 40,
        background: "#0b0d16",
        boxShadow: "-1px 0 0 rgba(233,233,237,.14),-24px 0 60px rgba(0,0,0,.6)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "14px 18px",
          boxShadow: "0 1px 0 rgba(233,233,237,.1)",
        }}
      >
        <span style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#9184d9" }}>
          Current retrieval run
        </span>
        <span className="tag tag-neutral" style={{ marginLeft: "auto" }}>
          graph run · 1f4c8a
        </span>
        <button type="button" className="btn btn-icon btn-secondary" onClick={toggleDev} aria-label="Close">
          ✕
        </button>
      </div>
      <div
        style={{
          padding: "16px 18px",
          overflow: "auto",
          flex: 1,
          minHeight: 0,
          display: "flex",
          flexDirection: "column",
          gap: 18,
        }}
      >
        <div style={{ flex: "none" }}>
          <div
            style={{
              fontSize: 11,
              letterSpacing: ".08em",
              textTransform: "uppercase",
              color: "rgba(233,233,237,.55)",
              marginBottom: 8,
            }}
          >
            LangGraph trace
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 1,
              borderRadius: 8,
              overflow: "hidden",
              background: "rgba(233,233,237,.08)",
            }}
          >
            {TRACE.map((t) => (
              <div
                key={t.node}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "9px 12px",
                  background: "#12141f",
                  fontFamily: "ui-monospace,Menlo,monospace",
                  fontSize: 12,
                }}
              >
                <span style={{ color: t.color, width: 9, flex: "none" }}>{t.mark}</span>
                <span style={{ flex: 1 }}>{t.node}</span>
                <span style={{ color: "rgba(233,233,237,.5)" }}>{t.ms}</span>
              </div>
            ))}
          </div>
        </div>
        <div style={{ flex: "none" }}>
          <div
            style={{
              fontSize: 11,
              letterSpacing: ".08em",
              textTransform: "uppercase",
              color: "rgba(233,233,237,.55)",
              marginBottom: 8,
            }}
          >
            Response · /profile/complete
          </div>
          <pre
            style={{
              margin: 0,
              padding: 13,
              borderRadius: 8,
              background: "#12141f",
              fontFamily: "ui-monospace,Menlo,monospace",
              fontSize: 11.5,
              lineHeight: 1.6,
              color: "rgba(233,233,237,.82)",
              overflow: "auto",
              boxShadow: "inset 0 0 0 1px rgba(233,233,237,.08)",
            }}
          >
            {JSON.stringify(DEV_RESPONSE, null, 2)}
          </pre>
        </div>
      </div>
    </aside>
  );
}
