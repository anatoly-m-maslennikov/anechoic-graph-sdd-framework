---
atom_family: SPEC
atom_id: AN-S-1309
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Detect weak Python assertions through mutation testing

## Claim

### Prose Claim

#### Claim checked

decision-dense changed Python has assertions strong enough **to** distinguish its
relevant alternative behavior.

#### Test case

run a pinned mutation profile **after** normal cases pass **and** preserve one
surviving relevant mutant **in** a manager **or** validator.

#### Acceptance criteria

pass **only** **when** the mutant is classified as missing assertion, unreachable,
equivalent, **or** intentionally uncovered, **and** the frontier **and** replay command are
preserved.

#### Failure disposition

reject unexplained survivors; keep this expensive campaign outside synchronous
Hooks.

#### Sources

- [Mutmut documentation](https://mutmut.readthedocs.io/en/latest/)
- [CA-M-285 — Select software Evaluation techniques by failure mode](../05_method/CA-M-285-PROGRAMMATIC--select-software-evaluation-techniques-by-failure-mode.md)
