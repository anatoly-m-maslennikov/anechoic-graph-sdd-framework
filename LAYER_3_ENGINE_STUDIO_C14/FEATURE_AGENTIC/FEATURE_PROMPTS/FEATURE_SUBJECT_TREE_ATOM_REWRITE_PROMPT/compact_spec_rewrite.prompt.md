**Input** — Use only the Current source Atom. Skip memory, Drafts, other Atoms, and code. Do not scout destinations.
**Task** — Treat all Atoms as one big document. Sort each statement: keep the central Claim for the Main Subject and Role; keep essential in-scope support; drop insignificant in-scope support; put statements that do not support the Claim or do not fit its Role in Offtopic.
- **R · Requirement** — Required outcomes and domain or business logic.
- **M · Method** — How to implement R, E, and D, including architecture and direct policies for writing code.
- **E · Evaluation** — Tests, Evals, linters, and other checks for R, M, and D, including what counts as a pass.
- **D · Delivery** — Which files, filenames, directory structures, CI/CD, and environments R, M, and E require.
**Output** — Return a new Draft with Summary, Claim, and `## Details` in simple ASD-STE100-aligned Markdown. Preserve Role and Form. Match Summary to the Claim. State each point once. End Details with `### Offtopic`; preserve the out-of-scope statements there for possible use as a Claim, part of a Claim, or Detail in another or new Atom.
**Size** — Exempt the entire Offtopic section from all size gates. Elsewhere, count nonblank Claim and Details source lines except headings, and limit each output Markdown source line to 100 characters, including spaces and markup.
**Limits** — Decision and unlisted Forms: up to 3 Claim lines and 5 counted Details lines. Policy: up to 6 and 10.
**Gate** — Check all applicable limits and stop on pass. Otherwise remove the least essential in-scope supporting statement and recheck, up to five removal-and-recheck loops. Never trim Offtopic to meet a limit. If any limit still fails, return Held and name the failing gate.
