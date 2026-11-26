---
atom_family: SPEC
atom_id: AN-S-3028
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:06:59.447140+00:00'
---
## Summary

Record the exact Workflow revision for each Run

## Claim

### Prose Claim

Each Workflow Run must record the Workflow Atom ID and exact revision from which it started.

## Details

Acceptance: A Run started from Workflow W revision 2 records W and revision 2 even after W revision 3 becomes Active.

Source: CA-A-1464@1-draft. Task: CA-P-3086.
