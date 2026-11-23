---
atom_family: SPEC
atom_id: AN-S-1075
container:
  component: C37
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 25
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Restore direct Project Scope Unit Graph output edits

# Restore direct Project Scope Unit Graph output edits

## Test case

change one value directly **in** a generated Project Scope Unit Graph **or** Sources output **without** changing **any** admitted authoritative input. retain Project Structure, Project Settings, Framework Instance Settings **and** the selected Atom, directory-observation **and** Journal evidence frontier.

## Acceptance criteria

- read-only validation reports the altered output stale **without** writing **any** source **or** generated output.
- a separately authorized rebuild restores the Graph **and** Sources outputs from the admitted current inputs under CA-R-1070 **and** CA-M-149, **not** from the edited output **or** an obsolete Configuration Atom.
- accepted Scope Unit declarations **and** bindings come **only** from Project Structure; observations cannot redefine them.
- authoritative inputs remain byte-identical throughout validation **and** rebuild.
