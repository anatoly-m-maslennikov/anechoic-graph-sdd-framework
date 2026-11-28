---
atom_family: SPEC
atom_id: AN-S-2259
container:
  component: C15
tier: 2
context:
  lens: SWD
state:
  status: "active"
  version: 5
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---
## Summary

Trace RMED obligations to their implementation owners

## Claim scope

The admitted PROGRAMMATIC implementation boundary, including descendant Tools, Apps, MCP components, workflows and their owning Modules or Units. Vendor code, generated output, frozen fixtures and legacy history are outside automatic editing unless explicitly admitted.

## Claim

### Prose Claim

Record implementation ownership under AN-S-3014. Use the exact revision pins and Module or Package placement defined by AN-S-2256.

An owner materially implements the cited Claim in the existing implementation. Calling, importing, re-exporting, or following guidance alone confers no implementation ownership. A test Module owns an Evaluation when it implements the check or its verification behavior.

Record each pin once per owner. Distinct owners may each cite the Atom when each materially implements it.

Follow AN-S-2256 for directly implemented Solutions and Engineering Standard applicability. For other Claims that several Modules jointly implement, record one pin in their smallest common owning Package.

## Details

Resolve the actual Atom version and owner before recording a pin. Report missing or ambiguous ownership and unresolved pins. Use trace links to find the implementation and assess conformance separately.

During migration, a source header pin remains valid until its owning sidecar replaces it. Keep each migrated pin in one place.

In the Workbench pilot, review Requirement-to-Module links for one-to-one, many-to-one and one-to-many ownership. Flag many-to-many groups for discussion.
