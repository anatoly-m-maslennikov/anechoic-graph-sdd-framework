---
atom_family: SPEC
atom_id: AN-S-3848
container:
  component: C20
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 11:29:41 +0400
---
## Summary

Define the AGENT_HOST_PLUGINS unit

# Define the AGENT_HOST_PLUGINS unit

`AGENT_HOST_PLUGINS` with prefix `AGENT_HOST_PLUGINS` **must** be one `unordered_unit` owned immediately by `APPS` at Structural level `4`, addressed by `002_FRAMEWORK_ENGINE/PROGRAMMATIC/APPS/AGENT_HOST_PLUGINS`, **and** realized under `002_FRAMEWORK_ENGINE/PROGRAMMATIC/APPS/AGENT_HOST_PLUGINS/`; it owns installable agent-host-specific plugin packages **and** their host wiring **without** duplicating provider-neutral ANECHOIC Skill, Tool, **or** Methodology behavior.
