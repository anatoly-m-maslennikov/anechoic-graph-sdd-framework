---
atom_family: SPEC
atom_id: AN-S-2384
container:
  component: C16
tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 16
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver the VALIDATE_ATOMS command

## Scope

the `VALIDATE_ATOMS` command Carrier and its delivered test assets in TOOLS.

## Claim

### Prose Claim

the `VALIDATE_ATOMS` executable Carrier **must** be delivered as `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/validate_atoms.py`, with its automated tests **in** the adjacent `tests/` directory.

- expose `validate_atoms.py --input <request.json>` **and** `--input -` for standard input.
- emit **=1** JSON result on standard output under CA-D-493-TOOLS-ENG_DECISION--serialize-atom-validator-results; human execution diagnostics belong on standard error.
- the path identifies an Implementation Artifact inside TOOLS, **not** a newly declared Scope Unit. it carries the implementation bound under CA-R-1622-TOOLS-RULE--implement-atom-carrier-validation-in-validate-atoms, **not** another Workflow authority.
- Verify the delivered command and its obligation coverage under AN-S-5180.

## Details
