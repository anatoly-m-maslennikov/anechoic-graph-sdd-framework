---
atom_family: SPEC
atom_id: AN-S-4144
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define File Format

## Claim scope

Formats applicable to File Carriers.

## Claim

A File Carrier's Format is the rules for encoding and interpreting its represented content. Core Meta-Model permits registered Markdown, TOML, YAML and JSON formats; Extensions and Project Configuration may register additional Carrier Formats.

### Formal claim

```text
Entity/Carrier/File.Format[string]{1}
```

## Details

Source meaning: CA-R-1950, CA-D-262. Scope-specific constraints remain in their governing Rs.
