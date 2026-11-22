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
  version: 5
  updated_at: "2026-11-22T13:37:29.536799+00:00"
---
## Summary

Admit Projects and serve Beta Workbench queries

## Guarantee

Admit an active Project Manifest and bind API requests to that Project.
Expose the read-only SQL run, page, check, and schema Tools. Return
typed inline pages from the Project's Kernel. Check SQL without
retaining a result. Expose admitted Realization Graph tables through the
SQL schema. Send Worker status requests to Orchestrator.

On a shared host, admit only Projects within the configured root and
enforce each Project's Tool blacklist. Reuse its Kernel and Orchestrator
within the configured capacity. Evict the least recently used idle
Project to admit another when capacity is full.

Pass the Project's Workbench storage choice or the host default to its
Kernel. With disk storage, continue serving a reopened compatible
generation if the replacement build fails.

## References

AN-S-3338 and AN-T-2958.
