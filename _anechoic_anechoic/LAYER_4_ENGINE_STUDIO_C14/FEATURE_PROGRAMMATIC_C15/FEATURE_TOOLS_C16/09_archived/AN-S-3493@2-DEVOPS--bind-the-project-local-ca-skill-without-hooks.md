---
atom_family: SPEC
atom_id: AN-S-3493
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 19:37:26 +0400
---
## Summary

Bind the project-local `ca` Skill without hooks

# Summary

Bind the project-local `ca` Skill without hooks

## Scope

The complete canonical `ca` Skill payload, staged candidate copy, and project-local no-hook Codex target.

## Claim

After the full-suite gate, Release Version **must** stage the complete `102_FRAMEWORK_ENGINE/202_AGENTIC/205_SKILLS/ca/` directory at `.anechoic_runtime/framework/releases/<candidateSnapshotManifest.sha256>/SKILLS/ca/`, including `SKILL.md`, `agents/openai.yaml`, and every declared resource, then promote it to the project-local Codex target `.agents/skills/ca/` only with the N+1 selection. The active public Skill remains N until promotion.

## Details

The Skill retains its `anechoic` Project-MCP dependency. Release Version neither registers MCP, changes Codex permissions, writes global configuration, nor changes Codex or Git Hook carriers, hook configuration, unrelated Skills, or user directories. Existing `INSTALL_TOOLS run --without-hooks` suppresses host-hook management only for the Engine Tools runtime and does not substitute for this Skill delivery.
