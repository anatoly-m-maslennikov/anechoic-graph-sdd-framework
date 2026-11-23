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
  version: 5
  updated_at: 2026-11-04 21:06:25 +0400
---
## Summary

Preserve nested Header and Markdown Property distinctions

## Claim scope

Current-model-guided in-memory parsing of governed carriers.

## Claim

### Prose Claim

YAML Header and Markdown Content are parsed directly with the safe YAML reader and actual CommonMark heading tree, not a fixed heading list or Declaration-to-schema compiler. Private parsed Header and Markdown data retain their distinctions and complete body. The public `atoms` table exposes only declared `content.*` columns, using quoted lowercase business-language paths such as `content.claim.prose claim` and `content.claim.formal claim`; it does not expose raw `header_json`, `content_markdown`, `content_properties_json` or `relation_edges_json` buckets. Nested Content Properties retain path segments, heading, direct Markdown, and complete subtree Markdown; parent path derives from segments. No `source_bytes` or `header_raw` is projected.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Header absence, null, empty values, scalar/list shape, false, and zero | Private parsed Header data keeps the values distinct; no raw `header_json` column is exposed publicly. |
| LF, CRLF, or mixed frontmatter delimiter line endings | Parse the Header and preserve the Markdown body’s exact original line endings. |
| Duplicate YAML key | The source is rejected with stderr error and no row. |
| Declared nested Property with direct text and child | Direct and subtree Markdown remain separate; parent derives from segments. |
| New or changed real Markdown heading | Its actual normalized path and direct/complete section values remain available to the parser; only declared Content Properties become public columns after refresh. No Declaration schema compiler is invoked. |
| Claim with Prose Claim, Formal Claim, and fenced heading-like text | Declared nesting and CFEL fence survive without false Properties; public values use quoted full paths such as `"content.claim.prose claim"`. |
