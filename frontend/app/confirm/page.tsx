import Link from "next/link";

export default function ConfirmPage() {
  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", alignItems: "baseline", gap: 12 }}>
        <h3 style={{ margin: 0 }}>Confirm your profile</h3>
        <span className="tag tag-outline">POST /profile/complete</span>
      </div>
      <p style={{ margin: "6px 0 26px", fontSize: 14, color: "rgba(233,233,237,.6)" }}>
        Pre-filled from the conversation. Anything you change is re-validated by the same rules the scorer uses.
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 26 }}>
        <div>
          <h6 style={{ color: "#9184d9", marginBottom: 12 }}>Applicant</h6>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: 14 }}>
            <div className="field">
              <label>Age</label>
              <input className="input" defaultValue="29" />
            </div>
            <div className="field">
              <label>Marital status</label>
              <div className="seg" style={{ width: "100%" }}>
                <label className="seg-opt" style={{ flex: 1, justifyContent: "center" }}>
                  <input type="radio" name="ms" defaultChecked />
                  Single
                </label>
                <label className="seg-opt" style={{ flex: 1, justifyContent: "center" }}>
                  <input type="radio" name="ms" />
                  Married
                </label>
              </div>
            </div>
            <div className="field">
              <label>Settlement funds (CAD)</label>
              <input className="input" defaultValue="18500" />
            </div>
          </div>
        </div>
        <div>
          <h6 style={{ color: "#9184d9", marginBottom: 12 }}>Occupation</h6>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: 14 }}>
            <div className="field">
              <label>Job title</label>
              <input className="input" defaultValue="Backend software developer" />
            </div>
            <div className="field" style={{ gridColumn: "span 2" }}>
              <label>Main responsibilities — used for NOC classification</label>
              <textarea className="input" style={{ minHeight: 36 }} defaultValue="Design and maintain REST services, data models and deployment pipelines" />
            </div>
          </div>
          <label className="radio" style={{ marginTop: 12 }}>
            <input type="checkbox" />
            <span className="dot" />
            I have a Canadian job offer of at least one year
          </label>
        </div>
        <div>
          <h6 style={{ color: "#9184d9", marginBottom: 12 }}>Language — English is the first official language</h6>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 14 }}>
            <div className="field">
              <label>Test</label>
              <select className="input">
                <option>IELTS</option>
                <option>CELPIP</option>
                <option>PTE</option>
              </select>
            </div>
            <div className="field">
              <label>Speaking</label>
              <input className="input" defaultValue="8.0" />
            </div>
            <div className="field">
              <label>Writing</label>
              <input className="input" defaultValue="7.5" />
            </div>
            <div className="field">
              <label>Listening</label>
              <input className="input" defaultValue="8.5" />
            </div>
            <div className="field">
              <label>Reading</label>
              <input className="input" defaultValue="8.0" />
            </div>
          </div>
          <div
            style={{
              marginTop: 10,
              padding: "10px 14px",
              borderRadius: 8,
              background: "#1b1e2d",
              fontSize: 13,
              color: "rgba(233,233,237,.72)",
            }}
          >
            Converts to <strong style={{ color: "#e9e9ed" }}>CLB 9 / 8 / 10 / 9</strong> — the scorer uses the
            lowest ability where a minimum applies.
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))",
              gap: 14,
              marginTop: 16,
            }}
          >
            <div className="field">
              <label>Second language test</label>
              <select className="input">
                <option>TEF</option>
                <option>TCF</option>
                <option>None</option>
              </select>
            </div>
            <div className="field">
              <label>Speaking</label>
              <input className="input" placeholder="required" style={{ boxShadow: "0 0 0 1px #796cbf" }} />
            </div>
            <div className="field">
              <label>Writing</label>
              <input className="input" placeholder="required" style={{ boxShadow: "0 0 0 1px #796cbf" }} />
            </div>
            <div className="field">
              <label>Listening</label>
              <input className="input" placeholder="required" style={{ boxShadow: "0 0 0 1px #796cbf" }} />
            </div>
            <div className="field">
              <label>Reading</label>
              <input className="input" placeholder="required" style={{ boxShadow: "0 0 0 1px #796cbf" }} />
            </div>
          </div>
        </div>
        <div>
          <h6 style={{ color: "#9184d9", marginBottom: 12 }}>Work experience — full-time years, within the last ten</h6>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 14 }}>
            <div className="field">
              <label>Foreign</label>
              <input className="input" defaultValue="3" />
            </div>
            <div className="field">
              <label>In Canada</label>
              <input className="input" defaultValue="1" />
            </div>
            <div className="field">
              <label>Continuous full-time, Canada</label>
              <input className="input" placeholder="required" style={{ boxShadow: "0 0 0 1px #796cbf" }} />
            </div>
            <div className="field">
              <label>Canada, within 3 years</label>
              <input className="input" defaultValue="1" />
            </div>
            <div className="field">
              <label>Skilled trade, within 5 years</label>
              <input className="input" defaultValue="0" />
            </div>
          </div>
          <p style={{ margin: "8px 0 0", fontSize: 12, color: "rgba(233,233,237,.5)" }}>
            Validated: continuous years cannot exceed total years, and Canada-within-3 cannot exceed total Canadian
            years.
          </p>
        </div>
        <div>
          <h6 style={{ color: "#9184d9", marginBottom: 12 }}>Education &amp; adaptability</h6>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: 14 }}>
            <div className="field">
              <label>Highest level</label>
              <select className="input">
                <option>Master&apos;s degree</option>
                <option>Bachelor&apos;s degree</option>
                <option>Two or more credentials</option>
                <option>Doctoral degree</option>
              </select>
            </div>
            <div className="field">
              <label>Canadian credential years</label>
              <input className="input" defaultValue="0" />
            </div>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginTop: 12 }}>
            <label className="radio">
              <input type="checkbox" defaultChecked />
              <span className="dot" />
              ECA completed
            </label>
            <label className="radio">
              <input type="checkbox" />
              <span className="dot" />
              Provincial nomination
            </label>
            <label className="radio">
              <input type="checkbox" />
              <span className="dot" />
              Sibling in Canada
            </label>
            <label className="radio">
              <input type="checkbox" />
              <span className="dot" />
              Other relative in Canada
            </label>
            <label className="radio">
              <input type="checkbox" />
              <span className="dot" />
              Certificate of qualification (trades)
            </label>
          </div>
        </div>
      </div>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 10,
          marginTop: 30,
          paddingTop: 20,
          background:
            "linear-gradient(to right,transparent,rgba(233,233,237,.16) 48px,rgba(233,233,237,.16) calc(100% - 48px),transparent) no-repeat top / 100% 1px",
        }}
      >
        <Link href="/results" className="btn btn-primary">
          Confirm and score
        </Link>
        <Link href="/draft" className="btn btn-secondary">
          Back to draft
        </Link>
        <span style={{ marginLeft: "auto", fontSize: 12, color: "rgba(233,233,237,.45)", alignSelf: "center" }}>
          3 fields still required
        </span>
      </div>
    </div>
  );
}
