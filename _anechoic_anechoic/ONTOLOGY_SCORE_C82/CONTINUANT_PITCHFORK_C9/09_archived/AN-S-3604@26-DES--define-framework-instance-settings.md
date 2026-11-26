---
atom_family: SPEC
atom_id: AN-S-3604
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-29 10:03:18 +0400
---
## Summary

Define Framework Instance Settings

## Claim scope

Framework Instance Settings for a ANECHOIC Framework Instance serving a Project.

## Claim

Authority Modes groups the Project mode and default Scope Unit mode, whose admitted values are strict and casual under CA-R-1430; per-Scope overrides remain in Project Structure. Interaction.Reporting Mode selects silent or verbose under CA-R-1628. An optional explicit Implementation Retry Limit preserves default resolution when absent; the logical Property does not introduce another TOML section or duplicate CA-D-447's carrier key.

the Term Framework Instance Settings **means** the authoritative Artifact containing explicit Operator-selected behavior **and** configuration choices for **`=1`** ANECHOIC Framework Instance serving **`=1`** Project.

Framework Settings is a structured configuration group. This declares no direct scalar at the group; its declared children keep their field-specific requirements. It introduces no generic Configuration field.

### Formal claim

```text
Project.Framework Settings{0}
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Authority Modes{0}
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Authority Modes.Project Authority Mode[string]{1}
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Authority Modes.Default Scope Unit Authority Mode[string]{1}
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Interaction.Reporting Mode[string]{1}
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Interaction.Reporting Mode: silent
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Interaction.Reporting Mode: verbose
Entity/Object/Continuant/Structural Unit/Scope Unit/Project.Framework Settings.Implementation Retry Limit[int]{0..1}
```

## Details
