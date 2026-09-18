import Link from "next/link";
import { INTAKE_FIELDS } from "@/lib/mock-data";

export default function IntakePage() {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit,minmax(340px,1fr))",
        gap: 1,
        background: "rgba(233,233,237,.1)",
        minHeight: "calc(100vh - 57px)",
      }}
    >
      <div style={{ background: "#0f111c", padding: 26, display: "flex", flexDirection: "column", gap: 16 }}>
        <div>
          <h4 style={{ margin: 0 }}>Intake conversation</h4>
          <p style={{ margin: "4px 0 0", fontSize: 13, color: "rgba(233,233,237,.55)" }}>
            POST /profile/parse · structured extraction
          </p>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 14, flex: 1 }}>
          <div style={{ display: "flex", gap: 10 }}>
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: "50%",
                flex: "none",
                background: "#2b2741",
                display: "grid",
                placeItems: "center",
                fontSize: 11,
                color: "#b5abfc",
              }}
            >
              MP
            </div>
            <div
              style={{
                background: "#232532",
                borderRadius: "4px 12px 12px 12px",
                padding: "11px 14px",
                fontSize: 14,
                maxWidth: "46ch",
                boxShadow: "var(--shadow-sm)",
              }}
            >
              Tell me about your age, your work, your language test results, your education, and whether you have
              family in Canada. Plain sentences are fine.
            </div>
          </div>
          <div style={{ display: "flex", gap: 10, flexDirection: "row-reverse" }}>
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: "50%",
                flex: "none",
                background: "#3f424d",
                display: "grid",
                placeItems: "center",
                fontSize: 11,
              }}
            >
              YOU
            </div>
            <div
              style={{
                background: "#1b1e2d",
                borderRadius: "12px 4px 12px 12px",
                padding: "11px 14px",
                fontSize: 14,
                maxWidth: "46ch",
                boxShadow: "inset 0 0 0 1px rgba(233,233,237,.1)",
              }}
            >
              I&apos;m 29. I&apos;ve been a backend software developer for four years — three in Vietnam, one in
              Toronto on a work permit. Master&apos;s in computer science from Hanoi, ECA done. IELTS 8/7.5/8.5/8 and
              TEF around B2. Single, no relatives in Canada, about CAD 18,500 saved.
            </div>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: "50%",
                flex: "none",
                background: "#2b2741",
                display: "grid",
                placeItems: "center",
                fontSize: 11,
                color: "#b5abfc",
              }}
            >
              MP
            </div>
            <div
              style={{
                background: "#232532",
                borderRadius: "4px 12px 12px 12px",
                padding: "11px 14px",
                fontSize: 14,
                maxWidth: "46ch",
                boxShadow: "var(--shadow-sm)",
              }}
            >
              I have most of it. Two things I cannot infer and will not guess: whether your Canadian year was
              continuous full-time, and your TEF sub-scores. I have flagged both on the right.
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "rgba(233,233,237,.5)" }}>
            <span style={{ display: "flex", gap: 3 }}>
              <i style={{ width: 5, height: 5, borderRadius: "50%", background: "#9184d9", display: "block" }} />
              <i style={{ width: 5, height: 5, borderRadius: "50%", background: "#796cbf", display: "block" }} />
              <i style={{ width: 5, height: 5, borderRadius: "50%", background: "#5d5294", display: "block" }} />
            </span>
            classifying occupation against NOC 2021…
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
          <textarea className="input" placeholder="Answer, or paste more detail…" style={{ minHeight: 64 }} />
          <button type="button" className="btn btn-primary" style={{ height: 36 }}>
            Send
          </button>
        </div>
      </div>
      <div style={{ background: "#13151f", padding: 26, display: "flex", flexDirection: "column", gap: 14 }}>
        <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 }}>
          <h4 style={{ margin: 0 }}>Profile forming</h4>
          <span className="tag tag-accent">9 of 11 fields</span>
        </div>
        <div style={{ background: "#161826", borderRadius: 14, padding: 18, boxShadow: "var(--shadow-sm)" }}>
          <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#9184d9" }}>
            CRS so far · provisional
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginTop: 6 }}>
            <span style={{ fontSize: 44, fontWeight: 500, lineHeight: 1, letterSpacing: "-.03em" }}>571</span>
            <span style={{ fontSize: 13, color: "rgba(233,233,237,.5)" }}>/ 1200</span>
          </div>
          <div
            style={{
              marginTop: 14,
              height: 8,
              borderRadius: 4,
              background: "rgba(233,233,237,.08)",
              overflow: "hidden",
              display: "flex",
            }}
          >
            <div style={{ width: "47.6%", background: "#9184d9" }} />
          </div>
          <div style={{ marginTop: 8, fontSize: 12, color: "rgba(233,233,237,.55)" }}>
            Recomputes as fields resolve. Missing fields are scored as zero, not estimated.
          </div>
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 1,
            borderRadius: 12,
            overflow: "hidden",
            background: "rgba(233,233,237,.08)",
          }}
        >
          {INTAKE_FIELDS.map((row) => (
            <div
              key={row.label}
              style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 14px", background: "#161826" }}
            >
              <span style={{ fontSize: 13, color: "rgba(233,233,237,.62)", width: "44%" }}>{row.label}</span>
              <span style={{ fontSize: 13.5, flex: 1, color: row.color }}>{row.value}</span>
              <span
                style={{
                  fontSize: 10.5,
                  letterSpacing: ".04em",
                  textTransform: "uppercase",
                  color: row.stateColor,
                }}
              >
                {row.state}
              </span>
            </div>
          ))}
        </div>
        <Link href="/draft" className="btn btn-primary btn-block" style={{ textAlign: "center" }}>
          Review the draft
        </Link>
      </div>
    </div>
  );
}
