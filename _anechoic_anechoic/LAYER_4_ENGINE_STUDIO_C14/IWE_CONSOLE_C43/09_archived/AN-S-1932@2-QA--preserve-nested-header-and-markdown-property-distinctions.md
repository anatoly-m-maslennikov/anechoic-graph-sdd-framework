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
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---
## Summary

Preserve nested Header and Markdown Property distinctions

## Claim scope

Current-model-guided in-memory parsing of governed carriers.

## Claim

### Prose Claim

YAML Header and Markdown Content are parsed according to the Current model and applicable Current declarations through an in-memory Reader Schema Projection, not fixed headings. `header_json` retains YAML distinctions and `content_markdown` the raw body. Nested Content Properties retain path segments, heading, direct Markdown, and complete subtree Markdown; parent path derives from segments. No `source_bytes` or `header_raw` is projected.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Header absence, null, empty values, scalar/list shape, false, and zero | `header_json` keeps the values distinct. |
| Duplicate YAML key | The source is rejected with stderr error and no row. |
| Declared nested Property with direct text and child | Direct and subtree Markdown remain separate; parent derives from segments. |
| Current declaration mapping edit | A refresh re-parses affected sources under the new mapping; fixed headings are not invented. |
| Claim with Prose Claim, Formal Claim, and fenced heading-like text | Declared nesting and CFEL fence survive without false Properties. |
