---
atom_family: SPEC
atom_id: AN-S-1276
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 25
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify structured diagnostic schema

## Claim



### Prose Claim
#### Claim checked

one PROGRAMMATIC operational diagnostic uses an admitted severity **and** provides
the actionable contextual fields required by its declared schema.

#### Applicable conditions

apply **when** a component emits a diagnostic for normal operation, degraded
operation, failure, recovery, **or** diagnostic detail.

#### Test case

evaluate one emitted diagnostic record for a declared component event. Also run a bounded scan that isolates a schema-invalid Atom and continues with a warning.

#### Acceptance criteria

pass **only** **when** the record uses ERROR, WARNING, INFO, **or** DEBUG, includes its
declared actionable contextual fields, **and** does **not** repurpose Journal history
as an operational diagnostic. For the bounded scan, require a structured warning with the validated Project prefix, repository-relative path and reason, and an operation response with `complete: false`; verify that no business action, Run or Journal record is fabricated and no historical Journal carrier is rewritten.

#### Failure disposition

reject the diagnostic path **until** its schema **and** severity are corrected.

#### Sources

- [CA-M-414 — Emit structured operational diagnostics](../05_method/CA-M-414-PROGRAMMATIC-ENG_POLICY--emit-structured-operational-diagnostics.md)
