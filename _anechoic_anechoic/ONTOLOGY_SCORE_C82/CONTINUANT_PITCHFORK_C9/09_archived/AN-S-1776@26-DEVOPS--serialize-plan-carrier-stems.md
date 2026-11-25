---
atom_family: SPEC
atom_id: AN-S-1776
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 26
  updated_at: "2026-11-25T22:07:26.670954+00:00"
---
## Summary

Serialize Plan Carrier stems

## Claim

### Prose Claim

This stem grammar applies to legacy Plan carriers. AN-S-3160 defines the native Ticket carrier.


identified Plan Carrier stems.


**every** identified Plan Carrier stem **must** use `[<WORK_SEQUENCE_NUMBER>-]<ATOM_ID>[-<LABEL>]--<SUMMARY_SLUG>`, with `.md` **only** on its File Carrier.

- the optional Label is a navigation token, **not** an Atom Type token; normalize it under the legacy filename rule AN-S-435@26.
- render the Summary under CA-D-282.
- **by default**, direct Plans decomposing the same Hub use unique leading Work Sequence Numbers **before** their Atom IDs, under CA-D-381 **and** CA-R-997.
- a same-bundle Directory Carrier **and** File Carrier use the same stem; number **or** Label changes preserve Atom identity **and** do **not** declare `BLOCKS`.
