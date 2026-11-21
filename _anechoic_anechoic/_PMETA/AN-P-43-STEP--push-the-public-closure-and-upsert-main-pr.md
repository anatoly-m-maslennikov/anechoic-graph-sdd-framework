---
atom_family: PMETA
atom_id: AN-P-43
structure:
  container:
    component: C27
context:
  template: step
state:
  status: active
  version: 12
  updated_at: 2026-11-09 15:54:30 +0400
---

# Summary

Push the public closure and upsert `main` PR

## Step

This Step invokes CA-O-196 once after the content prompt to commit and push the prepared closure on `amm/dev`, then find its one matching open `main` PR or create it as Draft. An existing matching open PR is converted to Draft before its body is edited.

## Details

The Step records the pushed commit and actual Draft PR identity. It cannot merge, retarget, or silently retry an unknown push or PR effect.
