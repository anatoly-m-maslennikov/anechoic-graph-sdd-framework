---
atom_family: SPEC
atom_id: AN-S-3018
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:24.338602+00:00'
---
## Summary

Resolve io_allowance shorthand and directions

## Claim

### Prose Claim

Resolve one `io_allowance` as an allowlist or a directional object. `io_allowance: [db, api]` applies to both directions. `input` covers reads and receives; `output` covers writes and sends. An omitted direction inherits that direction from the nearest ancestor. `[]` or `false` denies all direct I/O, while an omitted allowance with no ancestor defaults to `all`.

## Details

Acceptance: `[db, api]` permits both input and output for those channels; `{input: [db], output: []}` permits db input and denies output; a child that overrides only `input` keeps the nearest inherited `output`; no ancestor plus an omitted allowance resolves to `all`. Reject treating an omitted direction as `all` when an ancestor supplies it, or treating `false` as inheritance.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
