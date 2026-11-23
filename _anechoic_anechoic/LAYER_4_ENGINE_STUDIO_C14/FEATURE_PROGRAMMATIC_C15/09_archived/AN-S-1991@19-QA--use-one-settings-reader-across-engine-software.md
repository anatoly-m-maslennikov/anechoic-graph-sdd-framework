---
atom_family: SPEC
atom_id: AN-S-1991
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Use one Settings Reader across Engine software

# Use one Settings Reader across Engine software

## Claim checked

representative Tool, App, **and** MCP consumers use one immutable, validated,
versioned settings snapshot.

## Test case

replace the shared Reader with a recording fake **and** execute one representative
consumer from **every** PROGRAMMATIC child feature.

## Acceptance criteria

pass **only** **when** the shared Reader validates the input at its boundary **and** **every** consumer receives the immutable snapshot explicitly, preserves the same Carrier **and** digest provenance, **and** performs no direct read, fallback, private default selection, **or** mutation. a consumer **may** reuse an already validated snapshot **without** calling the Reader; this Evaluation does **not** impose a per-consumer read count.

## Failure disposition

reject the bypassing consumer **until** it accepts the shared snapshot explicitly.

## Sources

- [Python documentation: `unittest.mock`](https://docs.python.org/3.14/library/unittest.mock.html)
- [CA-M-284 — Read Engine settings through one shared boundary](../05_method/CA-M-284-PROGRAMMATIC-ENG_POLICY--read-engine-settings-through-one-shared-boundary.md)
