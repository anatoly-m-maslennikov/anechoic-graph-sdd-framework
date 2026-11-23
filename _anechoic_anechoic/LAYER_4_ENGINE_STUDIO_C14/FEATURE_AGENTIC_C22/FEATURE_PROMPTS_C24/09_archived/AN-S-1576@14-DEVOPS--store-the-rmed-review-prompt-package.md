---
atom_family: SPEC
atom_id: AN-S-1576
container:
  component: C24
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 14
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Store the RMED review prompt package

## Claim

### Prose Claim

the prompt package **must** occupy `ACTION_PROMPTS/RMED_ATOM_REVIEW/` relative **to** the PROMPTS Implementation Folder derived from the current Scope Unit Declarations, with these canonical Carriers.

## Details

### Scope

the delivered prompt package for RMED Atoms Base Revise within the Implementation Folder of PROMPTS.

| Carrier | Contents |
|---|---|
| `CA-O-108.prompt.md` | gathering instructions bound **to** Step `CA-O-108` **and** Action `CA-O-105` |
| `CA-O-109.prompt.md` | checking instructions bound **to** Step `CA-O-109` **and** Action `CA-O-106` |
| `CA-O-110.prompt.md` | correction instructions bound **to** Step `CA-O-110` **and** Action `CA-O-111` |
| `README.md` | invocation guidance **and** the current three-Step implementation interface |
| `source_bindings.json` | referenced source Atom IDs, paths, Versions, **and** source digests |
| `workflow_progress.py` | report-based progress aggregation |
| `tests/` | implementation tests **and** their mock evidence |

the prompt file header carries its Step, Action, **and** execution-context binding. instruction text realizes those methodology definitions; it is **not** another source of operational authority. optional evaluator **and** legacy helper Carriers remain separate from the default three-Step interface.
