---
atom_family: SPEC
atom_id: AN-S-2144
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: 2026-11-11 15:25:07 +0400
---
## Summary

Register Core Analysis Status Values

## Claim

### Prose Claim


the default Status value domain of Analysis and Advisory Atoms with Form Analysis Report or Rationale.


the Core Analysis and Advisory Status model **must** inherit the allowed values of Atom.Header.Status and add Done. That Role Status model applies to Analysis and Advisory Atoms with Form Analysis Report or Rationale. An admitted Extension or Project Configuration **may** add values under the applicable complete Role and Form path; it **must not** remove inherited values.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Analysis Report)).Header.State.Status :: Done;

Atom/(.Header.Context.Role in ("Analysis and Advisory"))/(.Header.Context.Form in (Rationale)).Header.State.Status :: Done
```

## Details

this Status belongs to the Analysis and Advisory Atom itself. It does **not** define a Status transition, carrier placement, setting, or a Workflow, Step, or Action Run outcome, receipt, retry state, result, or completion state. CA-R-1727@30 defines the meanings of Draft and Done for Analysis and the meaning of its archival.

