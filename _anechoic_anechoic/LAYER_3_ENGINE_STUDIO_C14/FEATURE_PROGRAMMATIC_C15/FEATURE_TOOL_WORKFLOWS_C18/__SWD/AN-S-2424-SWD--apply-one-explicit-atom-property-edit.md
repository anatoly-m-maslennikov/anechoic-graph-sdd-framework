---
atom_family: SPEC
atom_id: AN-S-2424
container:
  component: C18
tier: 3
context:
  lens: SWD
state:
  status: active
  version: 12
  updated_at: 2026-11-11 09:03:52 +0400
---
## Summary

Apply one explicit Atom Property edit

## Scope

Explicit Property and list-entry edits within one Atom Action.

## Claim

### Prose Claim

For the Project Configuration Atom Lifecycle Workflows, identity, Version, Updated At and history follow those Workflows and CA-R-1432 and CA-R-1788. CA-E-521 checks those effects. Differing statements in this Atom on those matters apply only to other operations.

**To** edit Atom Properties, the Action **must**:

1. Bind the explicit Atom identity and expected Version or source pin, declared Property edits and proposed values where required; read the complete current source through its connector.
2. Resolve each declared Property under its applicable schema. For an entry replacement or removal selected by current value, require exactly one existing equal value. Reject absent or ambiguous current values and caller-supplied replacement indexes.
3. Derive only explicit add, replace or remove deltas. For list Properties, support entry add/remove, replacement by unique current value or whole-set replacement; preserve unrelated entries and governed order and validate the complete proposed list and Atom.
4. Reject any same-ID Summary or Type value change and require replacement with a new Atom ID and predecessor archival. A verified unchanged requested state is a no-op without edit, Version, timestamp or history effects.
5. Every actual changed same-ID Atom update advances Version by **`=1`** and uses actual Updated At; retain its exact before-Revision evidence. Reuse admitted change-class, preview and permission checks, then recheck current source before the authorized effect. Verify the actual resulting source and report its exact outcome.

Preserve one-Atom storage-effect safeguards. A failed or uncertain Action stops the containing several-Atom Workflow, retains earlier completed Actions and leaves the remainder untouched.

## Details

Historical scalar-index fixtures do not validate this required current-value contract. Resume and retry policy is deferred; no implementation or live publication is established here.
