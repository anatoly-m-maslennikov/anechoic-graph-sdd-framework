---
atom_family: SPEC
atom_id: AN-S-266
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Bind one Tool effect result to its operation

# Bind one Tool effect result to its operation

## Claim checked

one admitted Tool effect **and** its receipt remain bound **to** the canonical
operation through failure **and** retry.

## Test case

apply one admitted file effect, force a partial failure, retry it with the same
operation identity, **and** attempt **to** attach the receipt **to** another operation.

## Acceptance criteria

pass **only** **when** the original identity remains on **every** request, failure, retry,
**and** receipt, **and** the mismatched attachment is rejected.

## Failure disposition

stop the effect path **until** operation identity, sealed target, arguments, **and**
receipt agree.

## Sources

- [CA-M-223 — Bind Tool effect results to the canonical operation](../05_method/CA-M-223-TOOLS-ENG_POLICY--bind-tool-effect-results-to-the-canonical-operation.md)
- [Python documentation: `tempfile`](https://docs.python.org/3.14/library/tempfile.html)
