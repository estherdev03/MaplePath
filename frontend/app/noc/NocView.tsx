"use client";

import Link from "next/link";
import type { Occupation } from "@/lib/types";

export default function NocView({ occupation }: { occupation: Occupation }) {
  const confidence = occupation.noc_confidence ?? 0;
  const groupTags = [
    occupation.teer != null ? `TEER ${occupation.teer}` : null,
    occupation.major_group_code ? `Major group ${occupation.major_group_code}` : null,
    occupation.submajor_group_code ? `Sub-major ${occupation.submajor_group_code}` : null,
    occupation.minor_group_code ? `Minor group ${occupation.minor_group_code}` : null,
  ].filter((t): t is string => Boolean(t));

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "34px 26px 80px" }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 20, alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: ".1em", textTransform: "uppercase", color: "#9184d9", marginBottom: 8 }}>
            Occupation match
          </div>
          <h3 style={{ margin: 0 }}>
            {occupation.noc_code ? `${occupation.noc_code} · ${occupation.title}` : "No confident match"}
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 }}>
            {groupTags.length > 0 ? (
              groupTags.map((t) => (
                <span key={t} className="tag tag-outline">
                  {t}
                </span>
              ))
            ) : (
              <span className="tag tag-neutral">No classification group</span>
            )}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(233,233,237,.6)" }}>
            Confidence
          </div>
          <div style={{ fontSize: 34, fontWeight: 500 }}>{confidence.toFixed(2)}</div>
          <div style={{ width: 130, height: 5, borderRadius: 3, background: "rgba(233,233,237,.1)", marginTop: 4 }}>
            <div style={{ width: `${confidence * 100}%`, height: 5, borderRadius: 3, background: "#9184d9" }} />
          </div>
        </div>
      </div>
      {occupation.reasoning && (
        <p style={{ margin: "18px 0 0", fontSize: 14, color: "rgba(233,233,237,.75)", maxWidth: "74ch" }}>
          {occupation.reasoning}
        </p>
      )}
      <div style={{ margin: "26px 0 12px", display: "flex", alignItems: "baseline", gap: 10 }}>
        <h5 style={{ margin: 0 }}>Retrieved candidates</h5>
        <span style={{ fontSize: 12, color: "rgba(233,233,237,.5)" }}>
          BM25 + pgvector, fused by RRF — the model could only choose a NOC code from this list
        </span>
      </div>
      {occupation.candidates.length > 0 ? (
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: 74 }}>NOC</th>
              <th>Title</th>
              <th style={{ width: 100 }}>Outcome</th>
            </tr>
          </thead>
          <tbody>
            {occupation.candidates.map((c) => {
              const chosen = c.noc_code === occupation.noc_code;
              return (
                <tr key={c.noc_code}>
                  <td style={{ fontVariantNumeric: "tabular-nums", color: chosen ? "#e9e9ed" : "rgba(233,233,237,.62)" }}>
                    {c.noc_code}
                  </td>
                  <td style={{ color: chosen ? "#e9e9ed" : "rgba(233,233,237,.62)" }}>{c.title}</td>
                  <td>
                    <span className={`tag ${chosen ? "tag-accent" : "tag-neutral"}`}>{chosen ? "Chosen" : "Candidate"}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      ) : (
        <p style={{ fontSize: 13.5, color: "rgba(233,233,237,.5)" }}>No candidates were retrieved for this profile.</p>
      )}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 22 }}>
        <Link href="/benchmark" className="btn btn-ghost">
          How accurate is this search? ↗
        </Link>
      </div>
    </div>
  );
}
