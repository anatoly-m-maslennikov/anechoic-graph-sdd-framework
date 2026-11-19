# Evaluation case — Make DSET self-hosting and skills thin

Accepted qualitative criteria remain owned by their layer plans. This Change
runs them independently from deterministic tests and records disagreements by
case and criterion.

| Owning plan | Applicable Eval IDs |
|---|---|
| `plan-evaluations.md` | `ANECHOIC-EVALUATION-CASE-META-008..009` |
| `plan-evaluations.md` | `ANECHOIC-EVALUATION-CASE-GOV-007..022`, `ANECHOIC-EVALUATION-CASE-GOV-025`, `ANECHOIC-GOV-EVAL-012--typed-artifact-relations-evaluation-case`, `ANECHOIC-GOV-EVAL-014--verbose-project-settings-evaluation-case..029`, `ANECHOIC-GOV-EVAL-018--runtime-boundary-interpretability..034` |
| `plan-evaluations.md` | `ANECHOIC-SPEC-TOOLS-EVAL-044--typescript-candidate-evaluation-case..004` |
| `plan-evaluations.md` | `ANECHOIC-EVALUATION-CASE-SKILL-002..008`, `ANECHOIC-SPEC-SKILLS-EVAL-049--implementation-preparation-modes..011` |
| `plan-evaluations.md` | `ANECHOIC-EVALUATION-CASE-OPS-002..003`, `ANECHOIC-FIELD-EVAL-058--delivery-artifact-boundaries` |

Connected accepted IDs are `ANECHOIC-EVALUATION-CASE-META-008`, `ANECHOIC-EVALUATION-CASE-META-009`,
`ANECHOIC-EVALUATION-CASE-GOV-007`, `ANECHOIC-EVALUATION-CASE-GOV-008`, `ANECHOIC-EVALUATION-CASE-GOV-009`,
`ANECHOIC-EVALUATION-CASE-GOV-010`, `ANECHOIC-EVALUATION-CASE-GOV-011`, `ANECHOIC-EVALUATION-CASE-GOV-012`,
`ANECHOIC-EVALUATION-CASE-GOV-013`,
`ANECHOIC-EVALUATION-CASE-GOV-014`, `ANECHOIC-EVALUATION-CASE-GOV-015`, `ANECHOIC-EVALUATION-CASE-GOV-016`,
`ANECHOIC-EVALUATION-CASE-GOV-017`,
`ANECHOIC-EVALUATION-CASE-GOV-018`,
`ANECHOIC-GOV-EVAL-011--mece-artifact-classification`,
`ANECHOIC-EVALUATION-CASE-GOV-020`, `ANECHOIC-EVALUATION-CASE-GOV-021`, `ANECHOIC-EVALUATION-CASE-GOV-022`,
`ANECHOIC-EVALUATION-CASE-GOV-025`, `ANECHOIC-GOV-EVAL-012--typed-artifact-relations-evaluation-case`,
`ANECHOIC-SPEC-TOOLS-EVAL-044--typescript-candidate-evaluation-case`,
`ANECHOIC-SPEC-TOOLS-EVAL-045--typescript-profile-instantiation-evaluation-case`,
`ANECHOIC-EVALUATION-CASE-SKILL-002`,
`ANECHOIC-EVALUATION-CASE-SKILL-003`, `ANECHOIC-EVALUATION-CASE-SKILL-004`, `ANECHOIC-EVALUATION-CASE-SKILL-005`,
`ANECHOIC-EVALUATION-CASE-SKILL-006`, `ANECHOIC-EVALUATION-CASE-SKILL-007`, `ANECHOIC-EVALUATION-CASE-SKILL-008`,
	`ANECHOIC-SPEC-SKILLS-EVAL-049--implementation-preparation-modes`, `ANECHOIC-EVALUATION-CASE-SKILL-011`,
`ANECHOIC-EVALUATION-CASE-OPS-002`, `ANECHOIC-EVALUATION-CASE-OPS-003`, and `ANECHOIC-FIELD-EVAL-058--delivery-artifact-boundaries`.

## Change-only qualitative proof

| Eval ID | Scenario | Threshold |
|---|---|---|
| `ANECHOIC-EVALUATION-CASE-SKILL-009` | Clean declared Claude, Codex, and other-host fixtures use the published installation path. | Every operator installs or links the real skill, confirms discovery, invokes its trigger, reaches local rules, and identifies the stop boundary. |
| `ANECHOIC-EVALUATION-CASE-TOOL-005` | Operators run the utility workflow on every declared platform, including spaces, Unicode, failures, and interrupted writes. | Outcomes are equivalent and safe; any narrower applicability is visible before execution. |
| `ANECHOIC-EVALUATION-CASE-TOOL-006` | Reviewers assess allowed, denied, unknown-registry, incompatible-license, provenance-drift, and expired-exception dependencies. | Every reviewer reaches the same accept/stop result from the authoritative rule and does not invent approval. |
| `ANECHOIC-EVALUATION-CASE-OPS-008` | A cold operator investigates the implementing PR's live GitHub workflow/run/check and protected-target state. | Every operator binds evidence to the actual PR SHA and selects a safe merge, block, or retry action without bypassing protection. |
| `ANECHOIC-EVALUATION-CASE-OPS-009` | Projects use shared integration branches and optional isolated worktrees across concurrent Changes and one protected PR. | Every reviewer identifies branch roles, actual workspace mode, and proof owner without requiring a worktree by default, merging Change identities, or creating permanent layer branches. |

Use at least two independent reviewers where interpretation matters. Correct the
earliest ambiguous owner and rerun the failed case; do not average a blocker
into a pass.
