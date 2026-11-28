---
atom_family: SPEC
atom_id: AN-S-2259
container:
  component: C15
tier: 2
context:
  lens: SWD
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---
## Summary

Trace RMED obligations to their implementation owners

## Claim scope

The admitted PROGRAMMATIC implementation boundary, including descendant Tools, Apps, MCP components, workflows and their owning modules or units. Vendor code, generated output, frozen fixtures and legacy history are outside automatic editing unless explicitly admitted.

## Claim

### Prose Claim

Record implementation ownership with exact native revision references under AN-S-3014 and AN-S-2256. An owner materially implements the cited Claim in the existing implementation. Calling, importing, re-exporting, or applying a Claim as guidance does not make a module its implementation owner. A test module owns an Evaluation when it implements the check or its verification behavior.

Use one record per owner:

- Put Decisions, individual Requirements, and Test or Evaluation Cases in the spec reference of the Module that implements them.
- Record a directly implemented Solution in its owning Package’s spec reference. For other Claims that several Modules jointly implement, record the pin once in their smallest common owning Package. Distinct owners may each cite an Atom when each materially implements it. In the Workbench pilot, review Requirement-to-Module links for one-to-one, many-to-one and one-to-many ownership. Flag many-to-many groups for discussion.
- Record an Engineering Standard once at the Package where it is in use as a package-wide practice. Keep applicability separate from implementation ownership.

## Details

Resolve the actual Atom version and owner before recording a pin. Use native pins such as `AN-S-123@4` for Specs with verified implementation owners. Report missing or ambiguous ownership and unresolved pins without guessing. Trace links identify where to inspect and do not establish conformance.

Use the Markdown spec reference format defined by the PROGRAMMATIC trace policy. During migration, a source header pin remains valid until its owning sidecar replaces it. Keep each migrated pin in one place.
