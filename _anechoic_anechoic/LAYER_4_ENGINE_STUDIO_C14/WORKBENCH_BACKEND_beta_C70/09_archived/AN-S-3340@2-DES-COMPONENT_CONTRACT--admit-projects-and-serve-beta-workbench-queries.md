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
  version: 2
  updated_at: "2026-11-22T12:39:08.717629+00:00"
---
## Summary

Admit Projects and serve Beta Workbench queries

## Guarantee

Admit an active Project Manifest and bind API requests to that Project.
Expose the admitted read-only SQL Tools. Return inline JSON results and
the public schema from the bound Database Server. Send Worker status
requests to Orchestrator.

On a shared host, admit only Projects within the configured root and
enforce each Project's Tool blacklist. Reuse its Kernel and Orchestrator
within the configured capacity. Evict the least recently used idle
Project to admit another when capacity is full.

## References

AN-S-3338 and AN-T-2958.
