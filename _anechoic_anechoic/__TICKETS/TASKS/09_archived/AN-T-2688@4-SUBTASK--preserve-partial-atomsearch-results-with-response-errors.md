---
atom_family: TKT
atom_id: AN-T-2688
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 06:04:46 +0400
---
## Summary

Preserve partial AtomSearch results with response errors

# Summary

Preserve partial AtomSearch results with response errors

## Objective

Integrate the shared owner with AtomSearch: retain verified valid matches when a selected Atom is invalid, expose explicit response errors as well as incomplete status, and emit WARNING technical logs. Preserve safety/binding refusals and avoid duplicate diagnostic emission.

## Details

One Task per file. After completion, review and update dependant Tasks before their execution. Actual business Workflow lifecycle recording remains with its declared executor; this Task does not invent it in an error decorator.

### Definition of Done

Golden/disposable functional and MCP protocol checks verify partial data plus attributable errors, all-invalid input, unchanged source/Journal bytes, service survival, and unchanged unsafe-effect refusals. At most 15 minutes own work.

### Execution checkpoint

AtomSearch retains valid matches and per-carrier warnings, with complete:false and explicit schema_invalid response errors when invalid carriers are skipped. All-invalid scans remain attributable incomplete results. Unsafe source/identity/frontier failures still refuse the affected lookup rather than returning unsafe partial data. Other provider refusals emit WARNING, and logger absence is visible in the response without a guessed Project prefix. The Tools portfolio initially ran 64 cases in 21.657 seconds and found one stale errors=[] assertion; only that test expectation changed. Its related 10-case provider module then passed in 1.175 seconds, retaining the other passing cases. Final related 32-case rerun and independent review pass. No source/Journal mutation or deployment is claimed.
