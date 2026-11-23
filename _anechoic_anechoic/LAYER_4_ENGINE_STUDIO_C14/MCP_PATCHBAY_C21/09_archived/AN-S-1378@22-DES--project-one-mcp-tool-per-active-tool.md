---
atom_family: SPEC
atom_id: AN-S-1378
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Project one MCP tool per active Tool

## Claim

### Prose Claim

MCP must expose exactly one callable endpoint for each enabled public Tool name in the installed registration configuration, backed by its canonical code handler and request/result contract. Source-only providers have no public endpoint. Reject duplicate public identities and preserve canonical operation meaning. No current Atom declaration is required merely to register or list an implemented, configured Tool.

## Details

Expose one stable callable MCP identity for each enabled code-owned provider or selected-route entry in the generated registration asset. Preserve its validated contract without splitting, aliasing, or aggregating it, and reject duplicate public identities or missing configured entries before publication.
