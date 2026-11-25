---
atom_family: SPEC
atom_id: AN-S-4616
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-10-27 19:59:47 +0400
---
## Summary

Query the stable Journal Event snapshot

# Summary

Query the stable Journal Event snapshot

## Operation

This Step is the query node of CA-O-161 and invokes exactly one Action, CA-O-162, Query Journal Events.

### Inputs and parameters

Before workflow/action-start recording or Action dispatch, the adapter captures the selected Project's canonical Journal byte-prefix and binds one opaque snapshot token containing source-root identity, prefix byte length and hash, ordered member references, member byte hashes and actually supplied string Event IDs without deduplication or a unique-ID requirement. Capture every decoded row, including missing/nonstring IDs, repeated IDs, lists and scalars, without changing the recorded JSON. Query result wrappers use None when a string ID is absent; coverage follows actual rows, not Event-ID uniqueness. The Action consumes exactly that sealed frontier. A standalone Action captures before its own Run evidence. Bind the literal filter expression, requested result mode (`ids`, selected `fields`, or `full_events`), selected fields when applicable, and bounded page request. The token excludes this invocation's later Run/Event records and permits later append only outside the sealed prefix.

## Details

The Step accepts no filename identity, secret-bearing selection, arbitrary SQL/code, mutation parameter, or fallback Journal root. A failed or incomplete Action returns its actual diagnostic and does not fabricate a successful Workflow or Action Run.
