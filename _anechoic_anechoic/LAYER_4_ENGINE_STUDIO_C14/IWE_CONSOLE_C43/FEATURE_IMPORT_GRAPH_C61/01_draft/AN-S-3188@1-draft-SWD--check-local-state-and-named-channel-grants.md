---
atom_family: SPEC
atom_id: AN-S-3188
container:
  component: C61
tier: 2
context:
  lens: SWD
relations:
  IS_REFERENCE:
  - AN-S-3187@1-draft
  - AN-S-3159@2
  - AN-T-2921
state:
  status: draft
  version: 1
  updated_at: '2026-11-22T16:44:45.347890+00:00'
---

## Summary

Check local state and named channel grants

## Claim

### Prose Claim

- Use the existing source ownership to identify the Component or Package that owns private state. Follow aliases to the original owner.
- Read the applicable `boundaries.state` declaration. The owning Component Manifest supplies named channel grants.
- `pure` permits immutable constants and explicit inputs and returns. Reject mutable module state, writes to global or nonlocal state, and ambient access.
- `local` is the default. Permit private mutation within its Component or Package boundary. Reject exporting mutable state or accessing another unit's private state.
- Declare `boundaries.state` as `pure`, `local`, or a mapping with `mode: local` and named `channels` with `r`, `w`, or `rw`.
- Use `ENV` for process environment access and `SYS_MODULES` for the Python module registry.
- Use the constructor name for a named ContextVar and `threading.local:<binding>` for recognized thread-local state.
- Reject unlisted channels and access beyond the grant. Mark an intentional no-op with `anechoic: no-op` in a comment directly before the action.
- Report the file, line, owner or channel, and read or write for each finding. Use unresolved for conflicting declarations or missing evidence of ownership or access.
