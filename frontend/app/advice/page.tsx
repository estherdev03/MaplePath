import { ADVICE } from "@/lib/mock-data";

export default function AdvicePage() {
  return (
    <div style={{ maxWidth: 880, margin: "0 auto", padding: "34px 26px 80px" }}>
      <h3 style={{ margin: 0 }}>What to do next</h3>
      <p style={{ margin: "6px 0 24px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
        Ordered by points gained per unit of effort. Each item names the rule it moves.
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {ADVICE.map((a) => (
          <div
            key={a.title}
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 16,
              alignItems: "flex-start",
              padding: "18px 20px",
              borderRadius: 14,
              background: "#161826",
              boxShadow: "var(--shadow-sm)",
            }}
          >
            <div style={{ flex: "none", width: 66, textAlign: "center" }}>
              <div style={{ fontSize: 26, fontWeight: 500, color: "#b5abfc", fontVariantNumeric: "tabular-nums" }}>
                {a.gain}
              </div>
              <div style={{ fontSize: 10, letterSpacing: ".06em", textTransform: "uppercase", color: "rgba(233,233,237,.45)" }}>
                points
              </div>
            </div>
            <div style={{ flex: 1, minWidth: 220 }}>
              <div style={{ fontSize: 16, fontWeight: 500 }}>{a.title}</div>
              <p style={{ margin: "5px 0 0", fontSize: 13.5, color: "rgba(233,233,237,.68)" }}>{a.body}</p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
                <span className="tag tag-neutral">{a.rule}</span>
                <span className="tag tag-outline">{a.effort}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <p style={{ margin: "22px 0 0", fontSize: 12, color: "rgba(233,233,237,.45)", maxWidth: "70ch" }}>
        Guidance is generated from the rule engines&apos; own shortfalls, not from open-ended model output. It is
        not legal advice.
      </p>
    </div>
  );
}
