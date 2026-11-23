---
atom_family: TKT
atom_id: AN-T-3328
container:
  component: C16
priority: 2
context:
  template: code_spec_mismatch
state:
  status: archived
  version: 2
  updated_at: 2026-09-02 01:12:00 +0400
---
## Summary

Implement Report-Only Candidate Detection

# Implement Report-Only Candidate Detection

the `DETECT_CLAIM_VALUE_SET_CANDIDATES` Tool Implementation **must** deterministically derive Governed Subject Sets, Claim Scopes, **and** allowed-value evidence from the supplied Source frontier **and** Entity Graph Projection, emit a report, **and must not** rewrite, merge, archive, replace, compile, **or** change Source Atoms by another operation.
