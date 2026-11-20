---
identity:
  atom_id: AN-S-1932
context:
  container:
    component: C45
  tier: 5
  lens: QA
state:
  status: draft
  version: 15
  updated_at: '2026-11-13T23:58:42.491073+00:00'
---
## Summary

Preserve nested Header and Markdown Property distinctions

## Claim

### Prose Claim

Verify that Current-model-guided in-memory parsing of governed carriers
preserves nested Header and Markdown Property distinctions.

## Details

### Private parsing

- Preserve the complete body, including LF and CRLF, and keep parsed Header
  separate from Markdown.
- Distinguish missing, null, empty, scalar, list, map, false, and zero values.
- Reject duplicate YAML keys.
- Keep direct Markdown values separate from nested Properties.
  - Treat undeclared prose headings and headings in code fences as text.
  - Apply the declared parsing rules for Prose Claim and Formal Claim.

### SQL projection

- In Mode 1, check declared Header paths. In Mode 2, check all valid Header
  paths observed at cold start, including empty ones.
- In both modes, verify declared Content paths and values.
- Check full dotted snake_case paths without a wrapper or raw parser data.
  - Use `Header.Context.Plan` → `header.context.plan` as the nested case.
  - Reject ambiguous flattened paths.

### Declaration coverage

- Check valid Current and Draft fixtures across all Roles and applicable Forms.
  Preserve each section at its declared path.
- Check nested, inherited, and multiword paths. Verify that wildcard rules,
  finite name lists, and bracketed constraints only limit declared paths.
- Check Role, Form, and Property changes after refreshing the asset and
  rebuilding the image. Existing behavior must still pass.
  - Verify that the watcher and full reread leave the loaded schema fixed.
  - Verify that value and presentation edits stay incremental.
- Verify that only supported Formal Claim blocks contribute model facts.
