---
atom_family: SPEC
atom_id: AN-S-1932
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Preserve nested Header and Markdown Property distinctions

## Claim scope

Current-model-guided in-memory parsing of governed carriers.

## Claim

### Prose Claim

Parse YAML Header and actual CommonMark headings directly. Private parsed Header/Markdown retain their distinction and complete body; public Mode 1 exposes only model-declared Header/Content paths, while enabled Mode 2 exposes every observed valid Header path and declared Content columns. Names use dotted lowercase snake_case paths, never old `id`/`status`/`role` aliases; do not expose raw Header/Markdown/property/relation buckets or source bytes.

## Details

Verify absence/null/empty/scalar/list/map/false/zero distinctions; LF/CRLF preservation; duplicate-key rejection; nested direct versus subtree Markdown; actual headings versus declared public Content; and Prose Claim/Formal Claim/fenced-heading handling. `Header.Context.Plan` maps to `header.context.plan` without a wrapper; ambiguous flattening fails rather than merging paths. `header.relations` matches native facts once. Mode 2 rebuilds for new/last-removed/type-changed/globally emptied Header paths, keeps observed empty paths and treats false/zero as values; same-schema edits stay incremental and arbitrary headings do not become Content columns.
