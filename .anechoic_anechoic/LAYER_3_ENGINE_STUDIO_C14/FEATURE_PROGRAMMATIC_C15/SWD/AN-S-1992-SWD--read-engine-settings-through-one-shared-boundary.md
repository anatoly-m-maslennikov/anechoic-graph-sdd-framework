---
identity:
  atom_id: AN-S-1992
context:
  container:
    component: C15
  tier: 4
  lens: SWD
state:
  status: active
  version: 32
  updated_at: '2026-11-12T17:19:27.261834+00:00'
---
## Summary

Read Engine settings through one shared boundary

## Claim



### Prose Claim
use one centralized Settings Reader for **every** applicable Tool, App, **and** MCP
component. the Reader reads the authoritative Project Settings Artifact,
validates the complete input, **and** returns an immutable typed snapshot with
the actual validated values, exact selected Project, physical source path,
raw SHA-256 Digest, **and** declared schema marker. the Reader **must not** query
the Work Journal **or** determine logical Revision **or** currentness. the snapshot
is derived; Project Settings is **not** a Projection.

The Settings Reader and the explicit Settings Doer use one shared carrier adapter. Bind the exact authoritative settings file and keep its schema. The adapter reads that file and writes only when the dedicated write operation supplies a complete, validated document. A validation failure leaves the file unchanged.

## Details

### Scope

apply **when** PROGRAMMATIC behavior depends on Project Settings.

#### Procedure
1. read the authoritative Project Settings Carrier bound by CA-D-364 through
   the shared Reader; do **not** infer a replacement from a legacy filename.
2. validate the complete carrier at the boundary **and** return structured
   diagnostics for invalid input.
3. pass the immutable snapshot explicitly **to** the consuming deterministic core
   **or** application service.
4. do **not** add component-specific parsers, default chains, environment
   fallbacks, semantic overrides, **or** writes **to** the Reader.
5. make the control panel use the same Reader **and** request changes **to** the
   authoritative Project Settings Artifact through its dedicated Doer, **not**
   through the Reader, its immutable snapshot, **or** a Projection.

#### Outcome

**every** component observes one validated settings snapshot **without** duplicating
parsing **or** inventing a second control panel.

#### Failure or stop

stop **when** the authoritative Project Settings Carrier is missing **or** schema-invalid,
mandatory physical source path **or** Digest provenance is absent, **or** a consumer
would bypass **or** mutate the shared snapshot.

#### Sources

- [Python documentation: `tomllib`](https://docs.python.org/3.14/library/tomllib.html)
- [Pydantic: strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
