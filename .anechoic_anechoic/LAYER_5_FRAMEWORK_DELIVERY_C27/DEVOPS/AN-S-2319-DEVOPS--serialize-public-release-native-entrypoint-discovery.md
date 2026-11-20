---
identity:
  atom_id: AN-S-2319
context:
  container:
    component: C27
  tier: 3
  lens: DevOps
state:
  status: active
  version: 17
  updated_at: 2026-11-11 00:17:19 +0400
---

## Summary

Serialize public-release native entrypoint discovery

## Scope

The native description surface of the public-release Tool.

## Claim

### Prose Claim

The public-release source **must** expose its stable `PUBLIC_RELEASE` identity and `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/public_release.py` entrypoint. The direct `public.release` command uses this Project-bound implementation without a closed release-admission record or whole-registry validation gate.

## Details

Discovery describes the capability; it does not authorize Git or remote effects. Execute only on the Operator's public-release command for the selected Project and remote. Preserve the direct implementation's input, branch, URL and failure checks and its required full test suite, including integration tests.

This Delivery creates no alternate registry, caller-selected executor or standalone MCP adapter. The ordinary selected Workflows keep their own admission rules; removing obsolete release admission does not weaken them.
