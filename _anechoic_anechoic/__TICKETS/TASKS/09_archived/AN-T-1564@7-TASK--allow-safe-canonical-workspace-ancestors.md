---
atom_family: TKT
atom_id: AN-T-1564
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 23:49:54 +0400
---
## Summary

Allow safe canonical workspace ancestors

# Summary

Allow safe canonical workspace ancestors

## Objective

Accept legitimate absolute workspace ancestor aliases while preserving leaf-symlink and protected-authority overlap rejection.

## Details

restart_recovery_finish exclusively owns IMPLEMENTATION_WORKFLOW/implementation_actions.py and its focused test file. Estimated slice <=10 minutes. Reproduce the macOS /var versus /private/var failure using a platform-independent symlinked ancestor. No runtime dispatch, LLM calls, commits or index changes.

## Definition of Done

The two blocked W09 fixtures and native route proof pass; a leaf-symlink workspace and protected overlap still fail before execution.

## Pre-execution review

Root accepts canonicalizing an admitted absolute workspace, not weakening its authority boundary. Actual Docker/queue proof remains a separate gate.

## Recorded verification

cb4bba3e2 retains canonical ancestor admission and mock transport agreement. Twenty-nine focused W09/native cases pass; leaf-symlink and protected-overlap refusal remain. Actual Docker/MCP queue proof is separate.
