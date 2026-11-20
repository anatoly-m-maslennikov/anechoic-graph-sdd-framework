---
identity:
  atom_id: AN-S-1315
context:
  container:
    component: C15
  tier: 5
  lens: QA
state:
  status: active
  version: 21
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify machine-contract compatibility

## Claim

### Prose Claim

#### Claim checked

one public machine boundary preserves structural, semantic, version, **and**
adjacent producer-consumer compatibility.

#### Test case

pass valid, missing-field, forbidden-field, wrong-type, **and** unsupported-version
fixtures from one producer **to** its supported adjacent consumer. Include
invalid arguments that must be rejected before effects, and where the boundary
supports shared paged state, delayed or reordered acknowledgements from two
clients and a snapshot larger than one page with null, Unicode and hidden values.
Use paired failures with similar human text but different structured error type,
code or state. When both restart-required and unavailable categories are
declared, include ordinary “restart required” text versus true unavailable
state.

#### Acceptance criteria

pass **only** **when** valid meaning survives, structural **and** semantic failures remain
distinct, unsupported versions are rejected, **and** the declared compatibility
promise is preserved **or** explicitly replaced. Failure classification comes
from structured type, code and state, not an arbitrary message substring; invalid
arguments have no effect before rejection. A shared page boundary keeps rows,
global counts and all value forms on one snapshot, and delayed or reordered
acknowledgements from two clients cannot mix or overwrite it.

#### Failure disposition

reject release **or** the compatibility claim **until** the boundary is restored.

#### Sources

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [CA-M-166 — Preserve declared interface compatibility boundaries](../05_method/CA-M-166-PROGRAMMATIC-CORE-METHOD--preserve-declared-interface-compatibility-boundaries.md)
