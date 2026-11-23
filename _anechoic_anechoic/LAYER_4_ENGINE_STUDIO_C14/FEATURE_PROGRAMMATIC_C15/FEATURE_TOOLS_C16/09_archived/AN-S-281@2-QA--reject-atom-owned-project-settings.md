---
atom_family: SPEC
atom_id: AN-S-281
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Reject Atom-owned Project Settings

# Reject Atom-owned Project Settings

## Test case

retain valid authoritative Project Settings **and** Project Structure. add a project_settings map **to** an active Atom that attempts **to** select a Project Settings value, including a conflicting value **in** a separate fixture. run the Scope Unit Graph generator **without** granting authority **to** that map.

## Acceptance criteria

- report the attempted second Settings owner **and** do **not** publish Graph **or** Sources outputs from that invalid authority selection.
- do **not** accept the map because its Atom is called Configuration **or** because its value equals the authoritative value.
- Project Settings remains authoritative for its own selected values, **and** Project Structure remains authoritative for accepted declarations **and** bindings. neither Artifact is changed.
- this check does **not** prohibit an Atom from defining a parameter **or** a rule about Settings; it rejects an independent current-value owner.
