---
identity:
  atom_id: AN-S-66
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 24
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reject a custom Git Hooks path conflict without mutation

# Reject a custom Git Hooks path conflict without mutation

## Claim checked

Installing the managed Git Hooks fails safely **when** the repository already declares another local `core.hooksPath`.

## Test case

Prepare a repository with a custom local `core.hooksPath`, executable Hook carriers **and** recorded bytes **and** modes, but no managed ANECHOIC Git Hook registration; invoke `INSTALL_TOOLS run --apply`.

## Acceptance criteria

Installation returns one stable conflict diagnostic. The configured path, **every** referenced Hook byte **and** mode, adapter registry, Git configuration, index, refs, `.anechoic_runtime/tools`, **and** `.anechoic_runtime` remain unchanged, **and** no backup carrier is created.

## Failure disposition

Reject the delivery **if** installation replaces, merges, copies, backs up, **or** partially registers over the custom Hook configuration, **or** **if** the failure is **not** deterministic.
