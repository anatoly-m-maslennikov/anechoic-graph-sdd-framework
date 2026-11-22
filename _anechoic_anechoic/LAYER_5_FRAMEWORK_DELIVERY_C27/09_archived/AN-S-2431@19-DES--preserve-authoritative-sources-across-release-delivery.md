---
atom_family: SPEC
atom_id: AN-S-2431
container:
  component: C27
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 19
  updated_at: "2026-11-22T06:18:53.973042+00:00"
---

## Summary

Preserve authoritative sources across release delivery

## Scope

The boundary between canonical release inputs and derived source, runtime, Skill, and image deliveries.

## Claim

### Prose Claim

Release Version **must** copy, package, install, and verify only derived deliveries while preserving canonical authoring sources, Project Structure, Project and Framework Settings, existing Journal evidence, and unrelated Skills byte-for-byte.

## Details

A changed current source/frontier invalidates further direct delivery and requires fresh input and file/path safety checks plus the declared test scope—C19 Test Suite unit, end-to-end and canary checks—not separate Active Atom metadata, placement or relation validation. The release Tool does not repair authority to make delivery pass. Retain exact actual predecessor and effect evidence on failure or uncertainty; a completed-copy predecessor proof binds the exact actual safe copy path, complete file bytes and modes, source/copy identities and expected/actual digests, and the real executing Workflow/Action Run. Unknown, tampered, unsafe, mode-drifted or identity-drifted source-effect evidence is refused; arbitrary old JSON or file presence alone is neither ownership proof nor permission to reuse, replay or promote that copy; preserve protected authoring sources, Settings, Project Structure and Journal bytes and never replay an unknown effect.

Local Release reports actual source, source-copy/product, package/runtime, Skill and image facts and owned Git transitions. It must not require or fabricate the retired D566/D567/D571 candidate/handoff/child formats or archived D574 checkpoints. Preserve all captured historical records unchanged; historical proof does not authorize a new release or prove unobserved old effects. First installation does not invent a prior installed release. Before any destructive replacement, the exact current replacement is ready and verified, protected configuration and Project state remain, and failure/cleanup blockers are reported truthfully.

Default Local release prepares its canonically named image only after the full suite is green. An explicitly focused Local route prepares it only after its selected scope passes. After installed-runtime verification and successful MCP smoke, retain the exact admitted candidate of the current package Version as the sole release-retention image. Remove other unused, positively classified images only when their inspected Project identity, host Project root and control root all match the selected Project. A different digest is not protected merely by the same source fingerprint, Version or tag. Preserve foreign, unowned, incompletely identified and container-referenced images; report blockers and failures without force, global prune or uncertain retries. A container link alone does not establish image ownership.

An explicit Local `--test-module` selection is a declared validation scope: it must be repeatable, repository-relative, and resolved against discovery; empty, duplicate, malformed, foreign, and symlink paths are refused, and any selected failure or required skip blocks downstream Local delivery. Selected scope may include any discovered source module, including Docker modules, with the existing shared image and launcher handling. Without this option the complete discovered suite remains the Local default. Public Release does not run a suite.
