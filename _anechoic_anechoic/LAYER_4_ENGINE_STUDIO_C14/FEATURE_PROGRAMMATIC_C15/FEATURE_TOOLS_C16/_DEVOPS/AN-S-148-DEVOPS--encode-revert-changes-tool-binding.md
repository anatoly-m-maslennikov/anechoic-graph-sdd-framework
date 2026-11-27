---
atom_family: SPEC
atom_id: AN-S-148
container:
  component: C16
tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 19
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
# Summary

Encode REVERT_CHANGES Tool binding

## Scope

The delivery Carrier and minimum MCP request/result contract for the REVERT_CHANGES Tool.

## Claim

The REVERT_CHANGES binding **must** expose strict request and result Carriers at one declared implementation location.

## Details

```toml
[tool_binding]
name = "REVERT_CHANGES"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/WORKFLOW_OPERATIONS/REVERT_CHANGES/revert_changes.py"
action_ids = ["CA-O-131"]
mcp_name = "revert_changes"
```

The strict request has `operation` (`admit` or `execute`), `reversal_request` for admission, and `approved_reversal_manifest` for execution. No Journal-only recovery operation or `pending_recording_event` field is exposed. Unknown fields, mixed modes, missing exact bindings, or a raw inverse instruction are explicit errors. The strict result has `outcome`, `manifest_id`, `effect_account`, `evidence_refs`, and `run_receipt_refs`; an admitted result additionally carries its manifest, while blocked/error results name the exact invalid binding. Existing `run_receipt_refs` retain actual shared Run observations and logging diagnostics, not canonical Journal receipts or a durability, permission or source-effect completion claim. Plain Journal append/read adds no logging retry or recovery, and logging failure does not change an independently observed reversal outcome or authorize effect replay. Actual Run-start failure still blocks before effects; actual Run-terminal failure preserves the effect account and reports `run_error`. The Tool exposes no generic delete/reset parameter and no auto-apply mode.

For Atom reversals, `expected_result_hash` is the hash of the intended target path, properties and exact Markdown content with `updated_at` omitted. The raw Carrier hash is not part of this result comparison because it includes that timestamp. Validate the actual `updated_at` separately. `expected_current_hash`, `current_hashes` and evidence hashes still bind the complete observed bytes and descriptors.

Use exact admission evidence under AN-S-5179.
