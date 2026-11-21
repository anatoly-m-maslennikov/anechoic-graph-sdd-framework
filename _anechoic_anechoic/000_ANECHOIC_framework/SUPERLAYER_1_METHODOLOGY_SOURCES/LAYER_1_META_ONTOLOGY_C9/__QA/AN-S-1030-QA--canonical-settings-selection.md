---
atom_family: SPEC
atom_id: AN-S-1030
structure:
  container:
    component: C9
  tier: 7
context:
  lens: QA
state:
  status: active
  version: 43
  updated_at: '2026-11-20T11:29:16.571224+00:00'
---

## Summary

Canonical Settings Selection

## Claim

Project settings resolve deterministically from the selected Project Manifest and fail closed on invalid or unknown selections. Validate selected values against their applicable authorities, enabled catalogs and field specifications, including closed structures. Validate applicable Artifact creation strictness and interaction reporting values and their governing defaults without hard-coding this Project's choices. A second parse must yield identical effective settings from the same selected Manifest bytes and revisions. Record a Concern and stop settings-schema readiness when an invalid value is accepted, a valid value is rejected or resolution is nondeterministic.
