---
atom_family: SPEC
atom_id: AN-S-4147
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

Define Main Content Paragraph

## Claim scope

Prose paragraphs within Markdown File Carrier Main Content.

## Claim

A Main Content Paragraph is one prose paragraph in a Markdown File Carrier Main Content; zero or more may occur. Delivery serializes each paragraph on one unwrapped source line with one blank line between adjacent paragraphs.

### Formal claim

```text
Entity/Carrier/File.Main Content.Paragraph[string]{0+}
```

## Details

Source meaning: CA-R-2269, CA-D-279. Scope-specific constraints remain in their governing Rs.
