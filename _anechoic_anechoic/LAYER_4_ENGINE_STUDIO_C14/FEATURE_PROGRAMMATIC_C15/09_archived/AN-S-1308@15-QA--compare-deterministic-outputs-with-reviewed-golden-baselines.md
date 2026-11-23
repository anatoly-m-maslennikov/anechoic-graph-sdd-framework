---
atom_family: SPEC
atom_id: AN-S-1308
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 10:48:25 +0400
---
## Summary

Compare deterministic outputs with reviewed golden baselines

# Compare deterministic outputs with reviewed golden baselines

## Claim checked

a large deterministic output changes **only** through a reviewed semantic diff.

## Test case

change one deterministic Markdown **or** machine-envelope output **and** invoke its
golden comparison with **only** declared volatile fields normalized.

## Acceptance criteria

pass **only** **when** the unexplained difference fails, critical invariants remain
focused assertions, **and** a replacement baseline requires explicit diff review.

## Failure disposition

reject automatic baseline refresh **and** return the semantic difference for
review.

## Sources

- [Syrupy snapshot testing](https://github.com/syrupy-project/syrupy)
- [CA-M-285 — Select software Evaluation techniques by failure mode](../05_method/CA-M-285-PROGRAMMATIC--select-software-evaluation-techniques-by-failure-mode.md)

### Golden-corpus cases

- require mock inputs **and** controlled external boundaries paired with reviewed expectations derived from governing RED. execute the real implementation **and** compare its actual output **and** declared effects against those expectations.
- test good, malformed, rejected, boundary, **and** combined inputs. reject a missing expected case, a false positive on a good case, **or** an unexplained difference on a bad case.
- a golden corpus **may** include small outputs; its use is **not** limited **to** large snapshots. normalize **only** explicitly admitted volatile representation, never behavior under test.
- retain discovered failures as regression cases. an automatic overwrite of expected outputs **or** an oracle copied from the defective implementation fails this Evaluation.
