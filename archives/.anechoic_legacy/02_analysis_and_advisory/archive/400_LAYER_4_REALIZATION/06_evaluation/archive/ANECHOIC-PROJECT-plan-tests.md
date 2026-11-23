# Test case — Make DSET self-hosting and skills thin

Accepted deterministic claims remain owned by the layer plans below. This
Change executes and records their applicable proof; it does not redefine them.

| Owning plan | Applicable Test IDs |
|---|---|
| `plan-tests.md` | `ANECHOIC-TEST-CASE-META-007`, `ANECHOIC-TEST-CASE-META-010..011` |
| `plan-tests.md` | `ANECHOIC-TEST-CASE-GOV-014..032`, `ANECHOIC-TEST-CASE-GOV-035..036`, `ANECHOIC-GOV-EVAL-027--canonical-settings-selections-test-case`, `ANECHOIC-GOV-EVAL-030--all-toml-carrier-migration-test-case..044`, `ANECHOIC-GOV-EVAL-036--control-runtime-and-scratch-boundaries-test-case..050` |
| `plan-tests.md` | `ANECHOIC-TEST-CASE-TOOL-005`, `ANECHOIC-TEST-CASE-TOOL-018..019`, `ANECHOIC-SPEC-TOOLS-EVAL-047--typescript-candidate-test-case..022` |
| `plan-tests.md` | `ANECHOIC-TEST-CASE-SKILL-001..010`, `ANECHOIC-SPEC-SKILLS-EVAL-051--lazy-implementation-preparation..013` |
| `plan-tests.md` | `ANECHOIC-TEST-CASE-OPS-003..007`, `ANECHOIC-FIELD-EVAL-059--delivery-release-role-boundaries` |

Connected accepted IDs are `ANECHOIC-TEST-CASE-META-007`, `ANECHOIC-TEST-CASE-META-010`,
`ANECHOIC-TEST-CASE-META-011`, `ANECHOIC-TEST-CASE-GOV-014`, `ANECHOIC-TEST-CASE-GOV-015`,
`ANECHOIC-TEST-CASE-GOV-016`, `ANECHOIC-TEST-CASE-GOV-017`, `ANECHOIC-TEST-CASE-GOV-018`,
`ANECHOIC-TEST-CASE-GOV-019`, `ANECHOIC-TEST-CASE-GOV-020`, `ANECHOIC-TEST-CASE-GOV-021`,
`ANECHOIC-TEST-CASE-GOV-022`, `ANECHOIC-TEST-CASE-GOV-023`, `ANECHOIC-TEST-CASE-TOOL-005`,
`ANECHOIC-TEST-CASE-GOV-024`, `ANECHOIC-TEST-CASE-GOV-025`, `ANECHOIC-TEST-CASE-GOV-026`,
`ANECHOIC-TEST-CASE-GOV-027`,
`ANECHOIC-TEST-CASE-GOV-028`,
`ANECHOIC-GOV-EVAL-023--delivery-artifact-classification`,
`ANECHOIC-TEST-CASE-GOV-030`, `ANECHOIC-TEST-CASE-GOV-031`, `ANECHOIC-TEST-CASE-GOV-032`,
`ANECHOIC-TEST-CASE-GOV-035`, `ANECHOIC-GOV-EVAL-024--typed-artifact-relations-test-case`,
`ANECHOIC-GOV-EVAL-027--canonical-settings-selections-test-case`, `ANECHOIC-GOV-EVAL-030--all-toml-carrier-migration-test-case`, `ANECHOIC-GOV-EVAL-031--complete-toml-cutover-test-case`,
`ANECHOIC-TEST-CASE-TOOL-018`, `ANECHOIC-TEST-CASE-TOOL-019`,
`ANECHOIC-SPEC-TOOLS-EVAL-047--typescript-candidate-test-case`,
`ANECHOIC-SPEC-TOOLS-EVAL-048--typescript-profile-instantiation-test-case`,
`ANECHOIC-TEST-CASE-SKILL-001`, `ANECHOIC-TEST-CASE-SKILL-002`, `ANECHOIC-TEST-CASE-SKILL-003`,
`ANECHOIC-TEST-CASE-SKILL-004`, `ANECHOIC-TEST-CASE-SKILL-005`,
`ANECHOIC-TEST-CASE-SKILL-006`, `ANECHOIC-TEST-CASE-SKILL-007`, `ANECHOIC-TEST-CASE-SKILL-008`,
`ANECHOIC-TEST-CASE-SKILL-009`, `ANECHOIC-TEST-CASE-SKILL-010`,
	`ANECHOIC-SPEC-SKILLS-EVAL-051--lazy-implementation-preparation`, `ANECHOIC-TEST-CASE-SKILL-013`,
`ANECHOIC-TEST-CASE-OPS-003`, `ANECHOIC-TEST-CASE-OPS-004`,
`ANECHOIC-TEST-CASE-OPS-005`, `ANECHOIC-TEST-CASE-OPS-006`, `ANECHOIC-TEST-CASE-OPS-007`, and
`ANECHOIC-FIELD-EVAL-059--delivery-release-role-boundaries`.

## Change-only deterministic proof

| Test ID | Contract/Requirement | Assertion |
|---|---|---|
| `ANECHOIC-TEST-CASE-SKILL-011` | `ANECHOIC-CONTRACT-SKILL-001` | Install/link every declared host-native skill in a clean host fixture and prove discovery, load, invocation, local resolution, handoff, and stop behavior. |
| `ANECHOIC-TEST-CASE-TOOL-016` | `ANECHOIC-CONTRACT-TOOL-001` | Exercise path, process, shell, encoding, temporary-file, write-safety, and exit behavior on every declared platform or prove honest narrower applicability before execution. |
| `ANECHOIC-TEST-CASE-TOOL-017` | `ANECHOIC-CONTRACT-TOOL-002` | Enforce dependency registry/version/license/provenance, lockfile authority, allow/deny policy, and bounded unexpired exceptions. |
| `ANECHOIC-TEST-CASE-OPS-014` | `ANECHOIC-CONTRACT-OPS-001` | Bind real GitHub workflow/run/check evidence to the actual implementing PR head and protected-target disposition. |
| `ANECHOIC-TEST-CASE-OPS-015` | `ANECHOIC-REQUIREMENT-OPS-012`, `ANECHOIC-CONTRACT-OPS-002` | Require integration-branch default scaffolding, accept explicit worktree isolation, allow shared integration branches/PRs, preserve isolated-branch uniqueness, and require head/candidate equality only at verified or archive-ready states. |

Add a failing deterministic proof before repairing every reproducible defect.
