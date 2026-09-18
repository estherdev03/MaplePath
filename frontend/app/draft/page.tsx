import Link from "next/link";

export default function DraftPage() {
  const readTags = [
    "age 29",
    "single",
    "master's + ECA",
    "IELTS 8 / 7.5 / 8.5 / 8",
    "3 yr foreign",
    "1 yr Canada",
    "no PNP",
    "no relatives",
    "CAD 18,500",
  ];

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "34px 26px 70px" }}>
      <h3 style={{ margin: 0 }}>Draft profile — two gaps and one warning</h3>
      <p style={{ margin: "6px 0 24px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
        Returned by <code style={{ fontSize: 12 }}>/profile/parse</code>. Nothing here is scored until you confirm
        it.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 14 }}>
        <div style={{ background: "#161826", borderRadius: 14, padding: 18, boxShadow: "0 0 0 1px #423a6a" }}>
          <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#b5abfc", marginBottom: 10 }}>
            Missing fields · 2
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <div style={{ fontSize: 14 }}>Continuous full-time Canadian experience</div>
              <p style={{ margin: "3px 0 0", fontSize: 12.5, color: "rgba(233,233,237,.55)" }}>
                Required for the FSW continuous-experience test. Your text says &quot;one year in Toronto&quot;
                without confirming it was unbroken.
              </p>
              <button type="button" className="btn btn-ghost" style={{ marginTop: 4, paddingLeft: 0 }}>
                Answer this →
              </button>
            </div>
            <div>
              <div style={{ fontSize: 14 }}>TEF sub-scores (speaking / writing / listening / reading)</div>
              <p style={{ margin: "3px 0 0", fontSize: 12.5, color: "rgba(233,233,237,.55)" }}>
                &quot;Around B2&quot; cannot be converted to NCLC. Without it the French bonus and second-language
                points stay at zero.
              </p>
              <button type="button" className="btn btn-ghost" style={{ marginTop: 4, paddingLeft: 0 }}>
                Enter scores →
              </button>
            </div>
          </div>
        </div>
        <div style={{ background: "#161826", borderRadius: 14, padding: 18, boxShadow: "0 0 0 1px #3f424d" }}>
          <div
            style={{
              fontSize: 10,
              letterSpacing: ".1em",
              textTransform: "uppercase",
              color: "rgba(233,233,237,.6)",
              marginBottom: 10,
            }}
          >
            Warnings · 1
          </div>
          <div style={{ fontSize: 14 }}>Settlement funds below the single-applicant threshold</div>
          <p style={{ margin: "3px 0 0", fontSize: 12.5, color: "rgba(233,233,237,.62)" }}>
            CAD 18,500 stated · CAD 15,263 required for a single applicant — met. Flagged only because a spouse would
            raise the bar to CAD 19,001.
          </p>
          <div style={{ marginTop: 14, height: 1, background: "rgba(233,233,237,.1)" }} />
          <div
            style={{
              marginTop: 14,
              fontSize: 10,
              letterSpacing: ".1em",
              textTransform: "uppercase",
              color: "rgba(233,233,237,.6)",
              marginBottom: 8,
            }}
          >
            Read confidently · 9
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {readTags.map((t) => (
              <span className="tag tag-neutral" key={t}>
                {t}
              </span>
            ))}
          </div>
        </div>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 22 }}>
        <Link href="/confirm" className="btn btn-primary">
          Open the confirm form
        </Link>
        <Link href="/intake" className="btn btn-secondary">
          Back to the conversation
        </Link>
      </div>
    </div>
  );
}
