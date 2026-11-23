---
atom_family: SPEC
atom_id: AN-S-3476
container:
  component: C19
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-11 16:46:21 +0000
---
## Summary

Seal the Release Version request and candidate boundary

# Summary

Seal the Release Version request and candidate boundary

## Scope

One requested release promotion from executing Version N to separately pinned candidate Version N+1 through one candidateSnapshotManifest.

## Claim

The Release Version Tool **must** derive one sealed `candidateSnapshotManifest` internally from the Operator's local-release command and the current registered definitions and active-source snapshot captured at Run start. It identifies executing N, candidate N+1, exact captured source revisions and digests, Project Structure and Framework Settings bindings, expected compiler frontier, complete package rows, declared full-suite environment, Skill target, and candidate image reference; the Operator supplies no manifest or manual revision bindings.

## Details

The Tool rejects absent, ambiguous, caller-substituted, tampered, or unsealed captured bindings before any delivery effect. It automatically derives the registered Workflow/Step/Action and Action-to-Tool bindings for the Run without a separate revision-refresh command. All candidate phases use the same captured bytes rather than replacing them with later authoring revisions. The manifest may reference canonical authority through its sealed source snapshot; it does not rewrite or replace that authority. A request does not authorize a source edit, a definition switch during an executing Run, an unbounded image deletion, or a recursive release invocation.
