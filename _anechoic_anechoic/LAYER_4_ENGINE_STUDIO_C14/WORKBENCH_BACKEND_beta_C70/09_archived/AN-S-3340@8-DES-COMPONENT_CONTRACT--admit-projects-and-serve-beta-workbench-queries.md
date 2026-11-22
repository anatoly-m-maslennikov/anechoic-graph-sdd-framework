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
  version: 8
  updated_at: "2026-11-22T15:27:12.309618+00:00"
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

Expose Workspace open, list, and get and View create, duplicate, list,
get, update, focus, rename, and remove. Send changes to the owning Kernel.
Resolve the session and Project from the API request and host binding.
Forward View run, check, and inline fetch to Kernel. Pass Workbench
result lifetime, Journal storage, and the file Journal path from the
admitted settings. Forward grid operations to Kernel. For a projection
rebuild, request generation through Orchestrator before asking Kernel to
refresh retained results. Return replacement IDs from Kernel.

## References

AN-S-3338 and AN-T-2958.
