---
atom_family: SPEC
atom_id: AN-S-5176
container:
  component: C16
tier: 2
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-27T17:35:02.224880+00:00'
---

## Summary

Bound COMMIT_CHANGE_SET Git Hook modes

## Claim

The installed script **may** expose read-only Git-hook validation **and** observation modes. Each synchronous `pre-commit` **or** `commit-msg` carrier performs **only** its required fail-closed Evaluation, **and** `post-commit` performs **only** its declared observation. Every carrier has an explicit measured latency threshold **and** timeout, stable exit semantics, **and** structured diagnostics. Broad repository scans, graph traversal, context gathering, Journal append, staging, commit creation, retry, lifecycle control, **and** background processing are prohibited inside these Hook processes; non-gating work is handed **to** changed-target **or** background execution.

No Git-hook mode creates a trigger, writes a Journal record, stages a path, **or** creates a commit. The modes reject staged installation, Runtime, Git-internal, mixed real-change/Journal, stale, **or** unfenced action boundaries. Codex automatic-commit intake remains a separate asynchronous carrier governed by `COMMIT_TRIGGER`.
