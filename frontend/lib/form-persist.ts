"use client";

export type FormSnapshot = Record<string, string | boolean>;

/** Reads every named field currently in the form into a plain snapshot —
 * radios collapse to their checked value, checkboxes to a boolean, text
 * inputs/selects/textareas to their string value. */
export function snapshotForm(form: HTMLFormElement): FormSnapshot {
  const snap: FormSnapshot = {};
  const seenRadioGroups = new Set<string>();

  for (const el of Array.from(form.elements)) {
    if (!(el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement || el instanceof HTMLSelectElement)) {
      continue;
    }
    const name = el.name;
    if (!name) continue;

    if (el instanceof HTMLInputElement && el.type === "radio") {
      if (seenRadioGroups.has(name)) continue;
      seenRadioGroups.add(name);
      const checked = form.querySelector<HTMLInputElement>(`input[type="radio"][name="${CSS.escape(name)}"]:checked`);
      if (checked) snap[name] = checked.value;
      continue;
    }
    if (el instanceof HTMLInputElement && el.type === "checkbox") {
      snap[name] = el.checked;
      continue;
    }
    snap[name] = el.value;
  }
  return snap;
}

/** Writes a previously-saved snapshot back onto a form's DOM fields.
 * Uncontrolled fields just take the value; controlled ones (checkboxes/
 * radios wired to React state) get a matching, idempotent write — the
 * corresponding state is expected to be restored separately so React's
 * next render agrees with what's written here. */
export function applySnapshot(form: HTMLFormElement, snap: FormSnapshot): void {
  for (const [name, value] of Object.entries(snap)) {
    const radios = form.querySelectorAll<HTMLInputElement>(`input[type="radio"][name="${CSS.escape(name)}"]`);
    if (radios.length > 0) {
      radios.forEach((r) => {
        r.checked = r.value === value;
      });
      continue;
    }
    const el = form.elements.namedItem(name);
    if (!el || el instanceof RadioNodeList) continue;
    if (el instanceof HTMLInputElement && el.type === "checkbox") {
      el.checked = Boolean(value);
    } else if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement || el instanceof HTMLSelectElement) {
      el.value = String(value);
    }
  }
}
