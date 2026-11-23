---
atom_family: SPEC
atom_id: AN-S-1769
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 25
  updated_at: 2026-10-30 03:11:58 +0400
---
## Summary

Serialize Delivery Type Tokens

## Claim scope

the serialization of Delivery Type tokens in a Delivery Atom File Carrier filename.

## Claim

a Delivery Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283-CORE_META_MODEL-ENG_DECISION--serialize-project-owned-markdown-atom-filenames **and** CA-D-284-CORE_META_MODEL-ENG_DECISION--serialize-filename-token-case:

- Eng Policy: `ENG_POLICY`.
- Eng Decision: `ENG_DECISION`.
- Release Definition: `RELEASE_DEFINITION`.
- Environment Definition: `ENVIRONMENT_DEFINITION`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.

## Details

The YAML `type` field remains the single admitted Type value under CA-D-657; a filename Type token is only its carrier encoding, not a second Type or a Label. An explicit `label` field is the effective Label when present; when absent, the effective Label is derived from the Atom Type name under CA-R-1594. Do not infer Type from a filename token or from that derived Label.

Release Definition and Environment Definition remain outside PROGRAMMATIC and its declared descendants under CA-R-1665; CA-R-2123 governs the Method and Delivery Type restriction in that scope.
