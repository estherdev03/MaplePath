import type { ReactNode } from "react";

/** The advice model returns section headers as short bare lines (e.g. "Top
 * Recommendations", "What is strong:"), not markdown — so headings are
 * detected by shape (short, title-cased, or colon-terminated) rather than
 * by a "**bold**" marker, though that's supported too if the model varies. */
function looksLikeHeading(line: string): boolean {
  if (/^\*\*[^*]+\*\*:?$/.test(line)) return true;
  const bare = line.replace(/:$/, "");
  if (bare.length === 0 || bare.length > 45) return false;
  if (/[.!?,;]$/.test(bare)) return false;
  if (line.endsWith(":")) return true;
  const words = bare.split(/\s+/);
  return words.length <= 5 && words.every((w) => /^[A-Z0-9]/.test(w));
}

/** Renders the advice LLM's plain text (section headers, **bold**, "- " bullets)
 * as lightweight React blocks, without pulling in a markdown dependency. */
export function renderAdvice(text: string): ReactNode[] {
  const inline = (line: string): ReactNode => {
    const parts = line.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
    return (
      <>
        {parts.map((part, i) =>
          part.startsWith("**") && part.endsWith("**") ? (
            <strong key={i}>{part.slice(2, -2)}</strong>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </>
    );
  };

  const blocks: ReactNode[] = [];
  let list: string[] = [];
  let key = 0;

  const flushList = () => {
    if (list.length === 0) return;
    blocks.push(
      <ul key={`ul-${key++}`} style={{ margin: "0 0 14px", paddingLeft: 20, display: "flex", flexDirection: "column", gap: 6 }}>
        {list.map((item, i) => (
          <li key={i} style={{ fontSize: 14, color: "rgba(233,233,237,.82)" }}>
            {inline(item)}
          </li>
        ))}
      </ul>
    );
    list = [];
  };

  for (const rawLine of text.split("\n")) {
    const line = rawLine.trim();
    if (!line) {
      flushList();
      continue;
    }
    const bullet = line.match(/^[-*]\s+(.*)$/) ?? line.match(/^\d+[.)]\s+(.*)$/);
    if (bullet) {
      list.push(bullet[1]);
      continue;
    }
    flushList();
    if (looksLikeHeading(line)) {
      blocks.push(
        <h6 key={`h-${key++}`} style={{ margin: "18px 0 8px", color: "#9184d9" }}>
          {line.replace(/\*\*/g, "").replace(/:$/, "")}
        </h6>
      );
    } else {
      blocks.push(
        <p key={`p-${key++}`} style={{ margin: "0 0 12px", fontSize: 14, lineHeight: 1.65, color: "rgba(233,233,237,.82)" }}>
          {inline(line)}
        </p>
      );
    }
  }
  flushList();
  return blocks;
}
