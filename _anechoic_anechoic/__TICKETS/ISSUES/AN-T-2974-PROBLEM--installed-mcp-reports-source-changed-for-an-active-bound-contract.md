---
atom_family: TKT
atom_id: AN-T-2974
concern:
- component(id=C21)
- component(id=C30)
container:
  component: C21
priority: 2
context:
  template: problem
state:
  status: "in_queue"
  version: 3
  updated_at: "2026-11-22T02:08:54.419181+00:00"
---

## Summary

Installed MCP reports source changed for an Active bound Contract

## Observed

The Operator reported that installed MCP returned `source_changed` after
the guarded filesystem input Contract was bound to its implementation.

The same MCP resolves `AN-S-3303@1` as Active. The checkout binding
`LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__spec_bind.yaml`
lists `AN-S-3303@1`. The original MCP request was unavailable for replay.

## Diagnosis

The installed MCP runtime and its Structure Host are pinned to Project
Manifest `AN-S-3037@7`. The mounted Project has `AN-S-3037@12`. The
runtime log reported `Project Manifest changed. Restart to apply its
settings.` before Workbench indexed the Contract.

A read-only replay with the installed code, running Structure snapshot,
and mounted checkout reproduced both failures. Lifecycle capture reported
`Selected native Project Manifest changed`. The C30 Contract owner guard
raised `SourceChanged` with cause `Project Manifest changed`.

Workbench refreshes its read projection against the newer Manifest. The
lifecycle gateway still uses the startup selection for writes. The Contract
binds to the expected revision. The Project Manifest digest comparison
fails before Contract owner validation can finish.

## Recovery and fix

Restarted the installed container with its existing image. The running
Structure Host now pins `AN-S-3037@12`, and the installed C30 Contract
write preflight accepts the mounted sources. MCP resolves the bound
`AN-S-3303@2` as Active.

The checkout checks the startup Manifest pin before lifecycle dispatch.
If that pin differs, MCP returns `project_manifest_reload_required`
and asks the Operator to restart. The regression covers a working read
projection, a blocked write with no file effects, and a successful write
after a fresh gateway selects the new Manifest. Nine focused tests passed.
The diagnostic awaits Local Release.

## Resolution criteria

- Report the stale Project Manifest pin and restart requirement in
  the MCP response when write validation requires a restart.
- Verify that the operation works with matching current sources. Preserve
  rejection when a required source has changed and report which check failed.
- Cover the matching and changed-source cases through the MCP entry point.

## References

AN-S-3303@1, AN-T-2944.
