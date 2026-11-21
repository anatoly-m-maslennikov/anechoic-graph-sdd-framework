---
atom_family: SPEC
atom_id: AN-S-2316
container:
  component: C27
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 14
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary

Package the Release Tool private reader closure

## Scope

The private reader dependency delivery of a content-addressed Tool Package containing the Release suite reference-context reader.

## Claim

### Prose Claim

A Tool Package containing `TOOLS/RELEASE_VERSION/release_suite_reference_context.py` **must** include its two canonical private MCP reader carriers at the sibling paths `204_MCP/release_source_admission.py` and `204_MCP/selected_routes.py`, with their exact source bytes and modes included in the same verified package inventory.

## Details

- the canonical reader sources are the same two paths under `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/`.
- package identity includes these rows, sorted by delivered path with the Tool rows. Copy and installed-package verification use the declared digest and mode; a missing, symlinked, changed or unverified dependency is a package failure.
- the sibling layout preserves the existing private reader import boundary. Packaging these library carriers does not register an MCP server, execute a Workflow, enable hooks, or grant mutation permission.
- Tool Packages without the Release reference-context reader retain their existing inventory contract.
