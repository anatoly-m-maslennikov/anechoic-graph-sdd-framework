---
atom_family: SPEC
atom_id: AN-S-3701
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 40
  updated_at: 2026-10-30 16:27:46 +0400
---
## Summary

Define Project Settings

## Claim scope

The Project.Settings Property group and its selected initialization inputs.

## Claim

Project.Settings is the authoritative Property group containing Operator-selected
initialization inputs for one Project, including its Name and Prefix. It has
no direct values; the declared Name and Prefix children each have one string
value. These initialization inputs are needed before the first Project Atom
or Implementation is created. They are not a Projection of existing Atoms or
Project structure.

### Formal claim

```text
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Settings{0}
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Settings.Name[string]{1}
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Settings.Prefix[string]{1}
```

## Semantics

This Requirement defines the structure of the qualified Properties, not a
lexical Term named Project Settings. Name and Prefix identify the same
Project-owned settings with corrected canonical child names; no second
selected value, Settings entity or identity is created. The zero count on
the parent means no direct values, not that its children are optional.

The Operator's example `Project//anechoic.Settings.Prefix = CA` states the
Prefix value of the named Project instance. It does not restrict the Prefix
Property of every Project to CA, define where Prefix is used, or request a
write to a settings Carrier. Its kind-level declaration remains string-valued.

Concrete serialization remains governed by Delivery: Name uses `project.name`
and Prefix uses `artifacts.identity.project_prefix`. Neither the logical name
correction nor the example renames those TOML keys, changes their encodings,
or introduces a new assignment/parser implementation.

## Details

The Operator selects `Project.Settings.Name` and `Project.Settings.Prefix`.
The earlier Atom-specific Prefix name is superseded. Prefix usage policies
are outside this correction; no Artifact-use enumeration is introduced.
The existing initialization timing and selected-value ownership are preserved.

### Pending field Definitions

- [Name](CA-R-draft-CORE_META_MODEL-ENTITY_DEFINITION--define-project-settings-name.md).
- [Prefix](CA-R-draft-CORE_META_MODEL-ENTITY_DEFINITION--define-project-settings-prefix.md).

### Draft source pin

Proposed N+1 successor of `.anechoic_anechoic/101_LAYER_1_FRAMEWORK_METHODOLOGY/METHODOLOGY_SOURCES/001_CORE_META_MODEL/04_requirement/CA-R-1738-CORE_META_MODEL--define-project-settings.md`, Version 39, SHA-256 `37d16be11fabbaa88259c8af45b87a0f614b823aeccc47465b38c4a10ac9b709`. Summary, Role and Entity Definition Type are preserved. No Current source, setting value or initialization operation is changed.
