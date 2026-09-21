import Link from "next/link";

export default function Home() {
  const stats = [
    { value: "516", label: "NOC 2021 unit groups indexed" },
    { value: "3", label: "Programs assessed: FSW · CEC · FST" },
    { value: "5", label: "Language tests converted to CLB / NCLC" },
    { value: "0", label: "Scores decided by a language model" },
  ];

  const steps = [
    {
      kicker: "Step 01",
      title: "Say it in your own words",
      body: "Free text becomes a validated profile. Fields that cannot be established are listed as missing, never invented.",
    },
    {
      kicker: "Step 02",
      title: "Occupation, matched not guessed",
      body: "Hybrid retrieval over official NOC profiles; the model must choose a unit group from the retrieved candidates.",
    },
    {
      kicker: "Step 03",
      title: "Deterministic scoring",
      body: "CRS and the FSW 67-point grid run as rule engines. Same input, same output, every time.",
    },
    {
      kicker: "Step 04",
      title: "Requirement-level verdicts",
      body: "Each program shows which requirements are met, which are not, and what the shortfall is.",
    },
  ];

  return (
    <div>
      <section
        style={{ maxWidth: 1080, margin: "0 auto", padding: "78px 26px 56px" }}
      >
        <span className="tag tag-outline">Express Entry · NOC 2021 · CRS</span>
        <h1
          style={{
            fontSize: "clamp(38px,5.4vw,62px)",
            margin: "20px 0 0",
            maxWidth: "19ch",
            letterSpacing: "-.03em",
          }}
        >
          Know exactly where you stand - category by category.
        </h1>
        <p
          style={{
            margin: "20px 0 0",
            maxWidth: "56ch",
            fontSize: 17,
            color: "rgba(233,233,237,.72)",
          }}
        >
          MaplePath reads your situation in plain language, classifies your
          occupation against the official NOC 2021 profiles, and computes your
          CRS score and program eligibility with published point tables. Every
          number is inspectable.
        </p>
        <div
          style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 30 }}
        >
          <Link
            href="/intake"
            className="btn btn-primary"
            style={{ fontSize: 15, padding: "10px 18px" }}
          >
            Describe your situation
          </Link>
        </div>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "26px 44px",
            marginTop: 46,
            paddingTop: 26,
            background:
              "linear-gradient(to right,transparent,rgba(233,233,237,.16) 48px,rgba(233,233,237,.16) calc(100% - 48px),transparent) no-repeat top / 100% 1px",
          }}
        >
          {stats.map((s) => (
            <div key={s.label}>
              <div style={{ fontSize: 30, fontWeight: 500 }}>{s.value}</div>
              <div style={{ fontSize: 12, color: "rgba(233,233,237,.55)" }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>
      <section
        style={{
          maxWidth: 1080,
          margin: "0 auto",
          padding: "10px 26px 40px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(255px,1fr))",
          gap: 14,
        }}
      >
        {steps.map((s) => (
          <div className="card elev-sm" key={s.kicker}>
            <div className="card-kicker">{s.kicker}</div>
            <div className="card-title">{s.title}</div>
            <p className="card-body">{s.body}</p>
          </div>
        ))}
      </section>
      <section
        style={{ maxWidth: 1080, margin: "0 auto", padding: "16px 26px 90px" }}
      >
        <p
          style={{
            fontSize: 12,
            color: "rgba(233,233,237,.45)",
            maxWidth: "72ch",
          }}
        >
          MaplePath is an engineering demonstration. It is not legal advice and
          does not replace IRCC tools or a licensed representative.
        </p>
      </section>
    </div>
  );
}
