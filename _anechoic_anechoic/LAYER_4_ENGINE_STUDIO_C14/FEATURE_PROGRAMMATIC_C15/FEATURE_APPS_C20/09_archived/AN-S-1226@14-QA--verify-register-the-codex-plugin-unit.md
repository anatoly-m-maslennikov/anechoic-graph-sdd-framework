---
atom_family: SPEC
atom_id: AN-S-1226
container:
  component: C20
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Verify register the codex_plugin unit

# Verify register the codex_plugin unit

## Claim checked

CA-M-197 registers one CODEX_PLUGIN child under AGENT_HOST_PLUGINS **without** duplicating provider-neutral ANECHOIC Skill, Tool, **or** Methodology behavior.

## Applicable when

Apply whenever CODEX_PLUGIN structure, package boundary, **or** host wiring changes.

## Test case

Examine the current active AGENT_HOST_PLUGINS **and** CODEX_PLUGIN authority, using **any** available derived representation **only** as supporting evidence. Determine CODEX_PLUGIN's immediate typed ownership, identity, path, host-specific contents, **and** **every** reference **to** provider-neutral ANECHOIC behavior.

## Acceptance criteria

Exactly one immediate typed ownership edge connects AGENT_HOST_PLUGINS **to** CODEX_PLUGIN; its address **and** path are valid; its owned content is Codex-specific package **or** host wiring; **and** **every** provider-neutral ANECHOIC Skill, Tool, **or** Methodology behavior appears **only** as a reference **to** its existing owner.

## Failure disposition

Reject the registration **and** preserve the examined authority, **any** supporting derived representation, path evidence, **and** **every** duplicated **or** misowned behavior claim.
