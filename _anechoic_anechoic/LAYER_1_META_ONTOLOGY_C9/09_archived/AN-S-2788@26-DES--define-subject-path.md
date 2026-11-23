---
atom_family: SPEC
atom_id: AN-S-2788
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-27 19:59:51 +0400
---
## Summary

Define Subject Path

# Summary

Define Subject Path

## Scope

a Subject Path.

## Claim

A Subject Path means a full canonical Subject Expression used by a Subject Relation to identify exactly one canonical Subject Target through its named Term components and registered qualifications. Bare Subject is a valid umbrella. A more-specific path names its namespace immediately after Subject: `Subject/ANECHOIC/...` for shared framework vocabulary or `Subject/<Project Name>/...` for project-specific concepts.

Within ANECHOIC, Graph contains Node, Relation and Rule as siblings; Node contains Project Model and Aspect; Carrier is outside Graph at `Subject/ANECHOIC/Carrier`. These path branches and namespaces do not create an extra entity or target identity. A qualification retains its registered endpoint constraints; the path identifies the target without becoming the Subject Relation itself.

## Details

The logical canonical path remains complete, including its namespace. A concise display label is not a substitute for that path in target identity, comparison or provenance. Namespaces are not entity kinds or Scope Units, and the Atom's owning Scope Unit does not determine its namespace.

A Subject Path may identify a classification axis without reifying it. Within the shared Atom branch, `Atom/Content Role` identifies that axis; `Atom/Content Role: Plan` identifies a narrower Atom kind that inherits Atom properties. The axis and the narrower kind retain distinct Subject meanings.
