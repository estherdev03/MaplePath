import type { InputHTMLAttributes } from "react";

type HintProps = {
  id: string;
  text: string;
  // Which edge the popup lines up with - "right" grows leftward (for badges at
  // the right edge of something), "left" grows rightward.
  align?: "left" | "right";
};

// A "?" badge. Hovering or focusing it shows the text in a popup.
export function Hint({ id, text, align = "right" }: HintProps) {
  return (
    <span className="group/hint relative inline-flex">
      <button
        type="button"
        aria-label="More info"
        aria-describedby={id}
        className="flex h-[18px] w-[18px] cursor-help items-center justify-center rounded-full border border-[rgba(233,233,237,.35)] text-[11px] leading-none text-[rgba(233,233,237,.7)] hover:border-[#9184d9] hover:text-[#9184d9] focus-visible:border-[#9184d9] focus-visible:text-[#9184d9]"
      >
        ?
      </button>
      <span
        id={id}
        role="tooltip"
        className={`invisible absolute bottom-[calc(100%+8px)] ${align === "right" ? "right-0" : "left-0"} z-20 w-[260px] rounded-md border border-[rgba(233,233,237,.16)] bg-[#232532] px-3 py-2 text-[12px] leading-snug font-normal tracking-normal normal-case text-[rgba(233,233,237,.85)] opacity-0 shadow-lg transition-opacity group-focus-within/hint:visible group-focus-within/hint:opacity-100 group-hover/hint:visible group-hover/hint:opacity-100`}
      >
        {text}
      </span>
    </span>
  );
}

type HintInputProps = InputHTMLAttributes<HTMLInputElement> & {
  id: string;
  hint: string;
};

// An input with a Hint badge on its right edge. The hint is also wired to the
// input via aria-describedby so screen readers announce it without the popup.
export default function HintInput({ id, hint, className = "", ...props }: HintInputProps) {
  const hintId = `${id}_hint`;
  return (
    <div className="relative">
      <input id={id} className={`${className} pr-9`} aria-describedby={hintId} {...props} />
      <span className="absolute top-1/2 right-2 flex -translate-y-1/2">
        <Hint id={hintId} text={hint} />
      </span>
    </div>
  );
}
