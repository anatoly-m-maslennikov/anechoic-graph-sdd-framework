---
atom_family: SPEC
atom_id: AN-S-1227
container:
  component: C20
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 9
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Register the CODEX_PLUGIN unit

# Register the CODEX_PLUGIN unit

## Applicable when

Use this Method **when** adding the Codex-specific plugin boundary under AGENT_HOST_PLUGINS.

## Procedure

1. Register CODEX_PLUGIN as one immediate child Scope Unit of AGENT_HOST_PLUGINS with its stable address, scope token, source path, **and** structural level.
2. Place **only** Codex package metadata, supported host wiring, **and** Codex-specific adapters inside the unit.
3. Reference GRAPH_UI **and** **every** provider-neutral ANECHOIC Skill, Tool, **and** Methodology behavior from its existing owner instead of copying **or** redefining it.
4. Rebuild the Project Scope Unit Graph **and** verify the immediate typed ownership edge from AGENT_HOST_PLUGINS **to** CODEX_PLUGIN.

## Outcome

the Codex integration has one explicit host-specific structural owner **without** duplicated provider-neutral behavior.

## Failure or stop

Stop on a duplicate CODEX_PLUGIN unit, an invalid address **or** source path, a non-immediate parent, **or** copied provider-neutral ANECHOIC behavior.
