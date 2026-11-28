---
atom_family: SPEC
atom_id: AN-S-5180
container:
  component: C16
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---

## Summary

Verify the delivered VALIDATE_ATOMS command and coverage

## Claim

Apply this matrix to the delivered command and its test assets.

- store the end-to-end command tests **in** `VALIDATE_ATOMS/tests/test_validate_atoms_e2e.py` relative **to** the delivered TOOLS directory.
- store mock Markdown Atoms **and** supporting mock context **in** `VALIDATE_ATOMS/tests/fixtures/`, with `good/`, `bad/`, `mixed/`, **and** `context/` groups. fixture files are test inputs, **not** active governing Project Atoms.
- store the case/coverage manifest **in** `VALIDATE_ATOMS/tests/cases.json` **and** independently reviewed expected reports **in** `VALIDATE_ATOMS/tests/expected/<case_id>.json`. **every** manifest case identifies its fixture inputs, request, governing rule identities/Revisions, expected report, **and** expected exit code.

- `cases.json` is a closed object with `schema_version: 1` **and** `cases`: a nonempty array. each case has a unique nonempty `case_id`, `request` path, nonempty `fixture_paths` list, nonempty `authority` list of exact Atom Bindings under CA-D-492-TOOLS-DELIVERY--serialize-atom-validator-requests, nonempty `check_codes` list, `expected_report` path, **and** integer `expected_exit_code` **in** (0, 1, 2, 3). all case paths are relative **to** `tests/`, remain inside it, **and** cannot escape through symlinks. expected reports follow CA-D-493-TOOLS-DELIVERY--serialize-atom-validator-results.
- include positive/negative/exception/boundary coverage for every supported check **and** declared failure class; reusable fixture cases may cover multiple rules. the harness verifies the matrix against the independently resolved obligation inventory, **not** just the list of implemented checks.
