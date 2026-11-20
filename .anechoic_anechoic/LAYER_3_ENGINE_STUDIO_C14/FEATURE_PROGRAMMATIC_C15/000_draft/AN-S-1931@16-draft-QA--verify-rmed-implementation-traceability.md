---
atom_family: SPEC
atom_id: AN-S-1931
structure:
  container:
    component: C15
  tier: 5
context:
  lens: QA
state:
  status: draft
  version: 16
  updated_at: '2026-11-13T18:17:59.219551+00:00'
---
## Summary

Verify RMED implementation traceability

## Claim scope

The admitted PROGRAMMATIC implementation being reviewed. Use the sidecar rules for the Workbench pilot.

## Claim

### Prose Claim

Verify that each spec-trace pin names an exact Atom revision and that the recorded owner implements or follows its Claim.

- Use a Module with an implemented Decision, a Package whose Modules jointly implement a Solution, and an Engineering Standard the Package follows. Check that each pin appears once at its owner. Keep Applies separate from Implements.
- Use a consumer that calls the Module and an empty package marker. Leave both without direct pins when neither implements a separate Claim. A source comment remains acceptable for an owner whose trace has yet to migrate. Remove the corresponding comment when its pin moves to a sidecar.
- Include malformed and unresolved pins and a valid Archived pin. Reject malformed pins. Report a missing revision only when its absence is known. An unloaded Archive leaves the pin unverified. Check that newer Atom versions do not silently change existing pins.

## Details

Check ownership against the code and the cited Claim. A trace records ownership. Conformance is checked by the applicable Evaluation.