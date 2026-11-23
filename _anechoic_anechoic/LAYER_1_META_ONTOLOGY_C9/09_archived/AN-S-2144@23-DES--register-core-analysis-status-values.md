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
  version: 23
  updated_at: 2026-11-11 13:45:22 +0400
---
## Summary

Register Core Analysis Status Values

## Claim

### Prose Claim


the default Status value domain of Analysis & Advisory Atoms with Form Analysis Report or Rationale.


the Core Analysis & Advisory Status model **must** inherit the allowed values of Atom.Header.Status and add Done. That Role Status model applies to Analysis & Advisory Atoms with Form Analysis Report or Rationale. An admitted Extension or Project Configuration **may** add values under the applicable complete Role and Form path; it **must not** remove inherited values.

### Formal Claim

```CFEL
# model
Atom/(.Header.Role in ("Analysis & Advisory"))/(.Header.Form in (Analysis Report)).Header.Status :: Done;

Atom/(.Header.Role in ("Analysis & Advisory"))/(.Header.Form in (Rationale)).Header.Status :: Done
```

## Details

this Status belongs to the Analysis & Advisory Atom itself. It does **not** define a Status transition, carrier placement, setting, or a Workflow, Step, or Action Run outcome, receipt, retry state, result, or completion state. CA-R-1727@30 defines the meanings of Draft and Done for Analysis and the meaning of its archival.

