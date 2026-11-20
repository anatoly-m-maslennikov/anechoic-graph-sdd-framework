---
identity:
  atom_id: AN-T-2922
context:
  container:
    component: C43
  tier: 3
  template: epic
state:
  status: done
  version: 1
  updated_at: '2026-11-20T16:34:57.901983+00:00'
relations:
  REFERENCES:
  - AN-T-2915
  - AN-S-3117@1
  - AN-S-2181@7
  - AN-S-3116@1
  - AN-S-1362@18
  - AN-S-2536@32
  - AN-S-1363@11
  - AN-S-1366@19
  - AN-S-3156@1
  - AN-S-3157@1
  - AN-S-3083@2
  - AN-S-3086@2
  - AN-S-3087@2
  - AN-S-3159@1
  - AN-S-3014@2
  - AN-T-2928@1-draft
---

## Summary

Move native Workbench DuckDB data to disk

## Objective

Store the native Workbench projection, parsed imports, and temporary query result tables in a Project-local DuckDB file. Let the Operator rebuild any table or all tables on demand.
Extend the Import Graph into the Realization Graph. Reuse its Module and
Package nodes for folder-derived test Relations.

## Work

### Stage 1. Prepare the Spec

1. Admit REFERENCES in AN-S-3117@1 and its Header target forms in AN-S-2181@7.
2. Create the Tier 1 Solution Decision AN-S-3116@1.
3. Update AN-S-1362@18, AN-S-2536@32, AN-S-1363@11, and AN-S-1366@19.
4. Create the rebuild and Operator Policies AN-S-3156@1 and AN-S-3157@1.
5. Update the Realization Graph Specs AN-S-3083@2, AN-S-3086@2, and AN-S-3087@2.
6. Define Package identity and Test Package in AN-S-3159@1.

## Definition of Done

The Spec covers both objectives. Verify disk-backed projections and results,
a rebuild from each Operator surface, and folder-derived test Relations
for Packages without a Spec Binding.

## Status

The Workbench and Realization Graph Specs are Current.
The review fixes passed verification in a disposable Workbench image.
