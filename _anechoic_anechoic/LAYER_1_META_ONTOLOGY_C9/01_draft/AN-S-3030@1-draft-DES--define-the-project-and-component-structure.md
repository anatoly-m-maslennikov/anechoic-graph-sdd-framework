---
atom_family: SPEC
atom_id: AN-S-3030
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:02:54.132508+00:00'
---
## Summary

Define the Project and Component structure

## Claim

### Prose Claim

A Project has a root Project Component. A Component has a Component Spec Section and a Component Package in REAL and may contain child Components. Component code may contain ordinary Packages. A Module is one source file; a Unit is a function, class, or method. `child_of` points to the parent Component and its inverse supplies children. Layers order siblings where needed. Within an ordered sibling group, imports may target only upstream siblings with lower layer numbers. Downstream imports are forbidden. Unordered siblings have no layer restriction. Each Atom tier is local to its containing Component.

Measure Spec-to-Realization ratios for each Component from its directly owned
Current Spec Atoms and Realization files. Count child Components separately.
Measure the Spec full file and body in KB. Also measure the Spec body in
physical lines. The body starts after the closing YAML header delimiter.

Compute each Spec measure against five Realization totals of the same unit:

- Implementation code.
- Test code.
- Test assets.
- Test code plus test assets.
- Implementation code plus test code and test assets.

Put Component-wide tests in the direct `<full Component Package folder name>__tests/`
subdirectory of the Component Package. Use the same layout for tests of an
ordinary Package in the Component. Count tests from both locations for the
owning Component. The Realization Graph identifies the Test Packages according
to AN-S-3014. Classify assets separately from test code as specified in AN-S-3013.

Exclude legacy `tests/` trees and legacy Python test modules selected by the
test discovery rule from the implementation totals. Include those tests in the
test totals when they use the declared layout.

Use 1,000 bytes per KB. Count physical lines in UTF-8 text. Binary assets
contribute bytes only. Return a null ratio when the denominator is zero.

## Details

Acceptance: Anechoic has exactly three direct children: Meta-ontology, Meta-methodology, and Engine Studio. Kernel Mixer, Backend Deck, IWE Console, and MCP Patchbay are children of Engine Studio, not direct children of Anechoic.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.
