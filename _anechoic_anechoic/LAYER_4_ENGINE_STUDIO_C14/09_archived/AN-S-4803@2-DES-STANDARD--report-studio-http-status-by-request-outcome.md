---
atom_family: SPEC
atom_id: AN-S-4803
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: DES
state:
  status: archived
  version: 2
  updated_at: "2026-11-27T18:17:41.214410+00:00"

---

## Summary

Report Studio HTTP status by request outcome

## Claim

### Prose Claim

A status GET that can report ongoing work returns HTTP 200 with
`state: pending`. Use `state: ready` when the requested data is ready.
An endpoint may return HTTP 202 when it accepts new work for later
processing.

When a known Project input problem prevents readiness or limits service,
return HTTP 200 with `state: degraded` if the status GET can report it.
Report the warning. Return a typed domain rejection when a data operation
requires the affected input. Keep unaffected operations available.

Report independent file warnings in Workbench Issues. Keep `state: ready`
when the Project meets its readiness requirements and service is available.

Use HTTP 5xx only when a genuine server or dependency failure prevents
handling the request. Preserve that failure when classifying the
response at a transport boundary, including while work is pending.
