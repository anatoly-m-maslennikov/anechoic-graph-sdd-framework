---
atom_family: SPEC
atom_id: AN-S-1228
container:
  component: C20
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Define the CODEX_PLUGIN unit

# Define the CODEX_PLUGIN unit

`CODEX_PLUGIN` with prefix `CODEX_PLUGIN` **must** be one `unordered_unit` owned immediately by `AGENT_HOST_PLUGINS` at Structural level `5`, addressed by `002_FRAMEWORK_ENGINE/PROGRAMMATIC/APPS/AGENT_HOST_PLUGINS/CODEX_PLUGIN`, **and** realized under `002_FRAMEWORK_ENGINE/PROGRAMMATIC/APPS/AGENT_HOST_PLUGINS/CODEX_PLUGIN/`; it owns the installable Codex-specific plugin package **and** Codex host wiring while referencing rather than redefining provider-neutral ANECHOIC behavior.
