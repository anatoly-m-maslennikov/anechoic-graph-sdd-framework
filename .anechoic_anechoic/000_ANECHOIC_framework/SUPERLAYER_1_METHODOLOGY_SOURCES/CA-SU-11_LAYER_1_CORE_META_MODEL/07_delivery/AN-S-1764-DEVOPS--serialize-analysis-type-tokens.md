---
identity:
  atom_id: AN-S-1764
context:
  container:
    component: C9
  tier: 3
  lens: DevOps
state:
  status: active
  version: 27
  updated_at: 2026-11-02 19:33:47 +0400
---
## Summary

Serialize Analysis Type Tokens

## Claim

### Prose Claim


the serialization of Analysis and Advisory Form tokens in an Analysis and Advisory Atom File Carrier filename.


an Analysis and Advisory Atom File Carrier **must** serialize the following Form components within the Atom filename grammar governed by CA-D-283 **and** CA-D-284:

- Rationale: `RATIONALE`.
- External Analysis Report: `EXTERNAL_ANALYSIS_REPORT`.

these mappings govern filename representation; they do **not** rename a Form, admit a new Form, **or** prescribe a YAML Form value.

