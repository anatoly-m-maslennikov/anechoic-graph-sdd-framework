---
atom_family: SPEC
atom_id: AN-S-1314
container:
  component: C15
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Use Python branch coverage as navigation evidence

# Use Python branch coverage as navigation evidence

## Claim checked

branch coverage locates unobserved alternatives **without** being treated as proof
of correctness.

## Test case

collect branch coverage for one changed decision unit with one intentionally
unobserved failure branch.

## Acceptance criteria

pass **only** **when** the missing branch is reported for review, the target **and**
omissions are stated, **and** acceptance depends on public-outcome assertions rather
than a percentage alone.

## Failure disposition

reject reliance based solely on the coverage percentage.

## Sources

- [Coverage.py: branch coverage](https://coverage.readthedocs.io/en/latest/branch.html)
- [CA-M-285 — Select software Evaluation techniques by failure mode](../05_method/CA-M-285-PROGRAMMATIC--select-software-evaluation-techniques-by-failure-mode.md)
