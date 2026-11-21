---
atom_family: SPEC
atom_id: AN-S-2544
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 16
  updated_at: '2026-11-13T22:35:59.035179+00:00'
---
## Summary

Rebuild the Workbench schema from source Atoms.

## Claim scope

The schema asset and source tables used by WORKBENCH_BACKEND.

## Claim

### Prose Claim

The Workbench schema is a rebuildable asset. The asset, SQL interface, MCP results and `query_schema` use the same dotted lowercase snake_case paths, such as `header.identity.atom_id`, `header.context.container` and `content.claim.formal_claim`.

#### Schema asset

- Refresh mode generates and validates `workbench_schema.json` and the query model from Current Declarations selected under CA-M-1011, including first-refresh bootstrap.
- Existing mode uses the checkout asset unchanged. Startup loads the delivered asset. A missing or invalid asset is reported; live Declarations are not a fallback compiler.
- Declared Header and Content schemas remain fixed. Declaration changes take effect after asset refresh and image rebuild. Ordinary data changes and rereads update data under the loaded schema without reloading or compiling it.

#### Header

- Mode 1 derives canonical names and formats from Current Declarations and the grouped Header carrier adapter. Accepted aliases are read-only; conflicts are rejected. `Header.ID` binds to `identity.atom_id`. Offset-bearing timestamps retain the existing `TIMESTAMPTZ` rules.
- Enabled Mode 2 observes every raw Header path in valid files at cold start, including empty paths and distinct source spellings. `header.context.container` JSON is its sole grouping-node exception. `header.relations` is one native direct/derived JSON projection.
- Neither mode rewrites source Headers or adds a full Form validator.

#### Content

Workbench can query Content for all Roles. Current Declarations determine which sections are queryable.

- Use each Role’s declared sections. Keep empty declared columns.
- Apply Role and Form rules, inheritance, and the most specific Content rules.
  - Only explicit property declarations name columns. Formats, conditions, wildcards, and observed headings constrain or supply data as applicable.
  - Select eligible Declarations separately from resolving conflicts. Keep exact provenance.

#### Source parsing

- The Current-model parser reads complete YAML and actual Markdown heading paths. It preserves complete mapped Content and distinguishes missing, null, empty, scalar, list, map, false, and zero values.
- A Scope Unit’s Current Declaration defines its structure. The Project Scope Unit is predetermined. Folders and paths represent the declared structure.
- Each readable file has its own Atom row, including Draft structural files. Audit tables report schema violations and duplicate logical revisions. Keep only mapped data.

#### Model facts

Declaration-derived facts come only from code blocks in `Content.Claim.Formal Claim` accepted by the build-time compiler. Comments outside strings do not supply facts or decide whether a block is a declaration. Prose Claim, Semantics, Details, examples and Header Topics supply no model facts. Source identity, lifecycle and provenance can select and bind inputs. Mode 2 observations are factual Header data, not declaration-derived facts.
