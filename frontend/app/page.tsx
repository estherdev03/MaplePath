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
      body: "Hybrid retrieval over official NOC profiles. The model must choose a unit group from the retrieved candidates.",
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
      <section className="mx-auto max-w-[1080px] px-[26px] pt-[78px] pb-14">
        <span className="tag tag-outline">Express Entry · NOC 2021 · CRS</span>
        <h1 className="mt-5 mb-0 max-w-[19ch] text-[clamp(38px,5.4vw,62px)] tracking-[-.03em]">
          Know exactly where you stand - category by category.
        </h1>
        <p className="mt-5 mb-0 max-w-[56ch] text-[17px] text-[rgba(233,233,237,.72)]">
          MaplePath reads your situation in plain language, classifies your
          occupation against the official NOC 2021 profiles, and computes your
          CRS score and program eligibility with published point tables. Every
          number is inspectable.
        </p>
        <div className="mt-[30px] flex flex-wrap gap-2.5">
          <Link
            href="/intake"
            className="btn btn-primary px-[18px] py-2.5 text-[15px]"
          >
            Describe your situation
          </Link>
        </div>
        <div className="mt-[46px] flex flex-wrap gap-x-11 gap-y-[26px] pt-[26px] [background:linear-gradient(to_right,transparent,rgba(233,233,237,.16)_48px,rgba(233,233,237,.16)_calc(100%_-_48px),transparent)_no-repeat_top_/_100%_1px]">
          {stats.map((s) => (
            <div key={s.label}>
              <div className="text-[30px] font-medium">{s.value}</div>
              <div className="text-[12px] text-[rgba(233,233,237,.55)]">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </section>
      <section className="mx-auto grid max-w-[1080px] grid-cols-[repeat(auto-fit,minmax(255px,1fr))] gap-3.5 px-[26px] pt-2.5 pb-10">
        {steps.map((s) => (
          <div className="card elev-sm" key={s.kicker}>
            <div className="card-kicker">{s.kicker}</div>
            <div className="card-title">{s.title}</div>
            <p className="card-body">{s.body}</p>
          </div>
        ))}
      </section>
      <section className="mx-auto max-w-[1080px] px-[26px] pt-4 pb-[90px]">
        <p className="max-w-[72ch] text-[12px] text-[rgba(233,233,237,.45)]">
          MaplePath is an engineering demonstration. It is not legal advice and
          does not replace IRCC tools or a licensed representative.
        </p>
      </section>
    </div>
  );
}
