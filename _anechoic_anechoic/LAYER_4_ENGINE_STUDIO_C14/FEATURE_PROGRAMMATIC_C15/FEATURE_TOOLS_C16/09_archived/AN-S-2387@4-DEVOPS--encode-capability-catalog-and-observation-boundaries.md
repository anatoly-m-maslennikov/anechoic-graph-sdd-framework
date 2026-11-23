---
atom_family: SPEC
atom_id: AN-S-2387
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-10-23 23:34:06 +0400
---
## Summary

Encode capability catalog and observation boundaries

# Summary

Encode capability catalog and observation boundaries

## Scope

the TOOLS capability for Capability Catalog/Carrier.

## Claim

the Capability Catalog **must** use the following source, binding **and** result Carrier contract.

## Details

- the Project control root is declared by paths.control_root **in** the Project's settings. its project_structure.toml provides Scope Unit ancestry **and** native bindings.
- source Atoms are explicit active Markdown Carriers under that control root, excluding the delivered APPLICABLE_METHODOLOGY files while retaining its METHODOLOGY_SOURCES descendants.
- a Tool Binding is a fenced TOML table **in** a D Atom's Details containing name, entrypoint, action_ids, optional workflow_ids **and** optional mcp_name. paths are repository-relative.
- compact discovery results contain identity, Summary, Kind, Scope Unit, source binding, implementation availability **and** match evidence. context responses contain exact content **and** incompleteness diagnostics.
- default bounds: 10 search results, **`<=50`** per page, 10,000 source candidates, 8 MiB per file, 256 MiB per scan, 60 seconds per scan, 256 KiB per context, **`<=8`** MiB per context, **`<=30`** seconds per wait. exhausted bounds return incomplete coverage.
- shared Run evidence **and** full reports keep their existing locations. status, result, continuation **and** wait calls create no new Journal **or** second event store.
- the initial observation backend is RMED Atoms Base Revise. its gather, check **and** fix Action results retain their existing Run ID **and** selection ordinal; independent Action Run identity is not invented.
