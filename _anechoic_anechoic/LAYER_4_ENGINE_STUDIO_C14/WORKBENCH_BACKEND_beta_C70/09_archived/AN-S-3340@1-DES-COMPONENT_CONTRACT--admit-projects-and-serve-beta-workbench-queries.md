---
atom_family: SPEC
atom_id: AN-S-3340
container:
  component: C70
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T12:16:35.025732+00:00"
---
## Summary

Admit Projects and serve Beta Workbench queries

## Guarantee

Admit an active Project Manifest and bind API requests to that Project.
Expose the admitted read-only SQL Tool and return inline JSON rows.
Send queries to the bound Database Server and Worker status requests to
Orchestrator. Shared requests admit a Project within the configured root
and enforce its Tool blacklist.

## References

AN-S-3338 and AN-T-2958.
