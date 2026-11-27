---
atom_family: SPEC
atom_id: AN-S-132
container:
  component: C16
tier: 2
context:
  lens: DevOps
state:
  status: active
  version: 39
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver the commit-change-set script

# Deliver the commit-change-set script

Realize `COMMIT_CHANGE_SET` through the canonical source script `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/COMMIT_CHANGE_SET/commit_change_set.py` **and** its content-identical carrier **in** the selected `.anechoic_runtime/tools` release. It exposes the common Doer CLI **in** dry-run **and** authorized-MCP apply modes. It consumes **only** sealed peer results **and** **must not** import, invoke, schedule, **or** **otherwise** orchestrate `COMMIT_TRIGGER`, `COMMIT_CONTEXT`, **or** `APPEND_CHANGE_RECORDS`.

Apply AN-S-83 to durable outbox selection, the repository-scoped lease and fence, and exact real-change and Journal-only target sets. Revalidate the sealed Initiative, expected Git base, subject frontier, and complete target set immediately before staging, Git mutation, and result recording. Stage no Journal Carrier in a real-change commit. Journal append is a peer operation. Use AN-S-273 for both commit message forms.

Dry run is mutation-free. Recovery reconciles **any** uncertain Git effect against the outbox **and** reachable Git history **before** retry. Apply AN-S-5176 to installed Git Hook modes.
