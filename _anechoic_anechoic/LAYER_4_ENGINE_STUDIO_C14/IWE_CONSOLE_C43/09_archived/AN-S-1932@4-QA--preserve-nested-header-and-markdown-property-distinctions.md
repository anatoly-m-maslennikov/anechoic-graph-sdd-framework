---
atom_family: SPEC
atom_id: AN-S-1932
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 4
  updated_at: 2026-11-04 15:28:34 +0400
---
## Summary

Preserve nested Header and Markdown Property distinctions

## Claim scope

Current-model-guided in-memory parsing of governed carriers.

## Claim

### Prose Claim

YAML Header and Markdown Content are parsed directly with the safe YAML reader and actual CommonMark heading tree, not a fixed heading list or Declaration-to-schema compiler. `header_json` retains YAML distinctions and `content_markdown` the raw body. Nested Content Properties retain path segments, heading, direct Markdown, and complete subtree Markdown; parent path derives from segments. No `source_bytes` or `header_raw` is projected.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Header absence, null, empty values, scalar/list shape, false, and zero | `header_json` keeps the values distinct. |
| LF, CRLF, or mixed frontmatter delimiter line endings | Parse the Header and preserve the Markdown body’s exact original line endings. |
| Duplicate YAML key | The source is rejected with stderr error and no row. |
| Declared nested Property with direct text and child | Direct and subtree Markdown remain separate; parent derives from segments. |
| New or changed real Markdown heading | Its actual normalized path and direct/complete section values appear after refresh; no Declaration schema compiler is invoked. |
| Claim with Prose Claim, Formal Claim, and fenced heading-like text | Declared nesting and CFEL fence survive without false Properties. |
