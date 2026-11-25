---
atom_family: SPEC
atom_id: AN-S-3017
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:21.679730+00:00'
---
## Summary

Define one inherited io_allowance per Component Manifest

## Claim

### Prose Claim

A Component Manifest has one `io_allowance` field. It applies to the Component's own modules and ordinary Packages; it is not split into separate own and children allowances. A child Component uses the nearest ancestor's allowance by default and may declare one explicit override in its own Manifest. An ordinary Package may further narrow the allowance it inherits.

## Details

Acceptance: a child with no declaration resolves the nearest ancestor's value; a child with an explicit declaration resolves that value while the parent's authored value stays unchanged. Reject a model that uses a farther ancestor when a nearer declaration exists, or introduces separate own/children allowance fields.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
