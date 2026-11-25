---
atom_family: TKT
atom_id: AN-T-3474
container:
  atom: AN-T-3468
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-23T23:07:47.000000+00:00'
---
## Summary

Record pilot dependency effects and version pin

## Work

Review the few dependencies used by the two pilot functions. Record their
import-time and call-time effects, including the library-private regular
expression cache, Project state, ambient state, and I/O. Record the runtime
version pin and the explicit unsupported behavior for effects that the pilot
does not model.

## Acceptance

The review separates import-time from call-time effects, names the private
regex-cache behavior, distinguishes Project and ambient state from I/O, and
records the version pin and unsupported behavior. Do not promote an unsupported
effect to a resolved guarantee.
