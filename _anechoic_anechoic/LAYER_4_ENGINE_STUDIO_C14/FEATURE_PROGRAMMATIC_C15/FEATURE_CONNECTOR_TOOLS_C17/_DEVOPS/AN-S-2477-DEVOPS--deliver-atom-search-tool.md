---
atom_family: SPEC
atom_id: AN-S-2477
container:
  component: C17
tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 28
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver ATOM_SEARCH Tool

## Scope

Apply the shared connector boundary in AN-S-2478.

This Delivery carrier records `CONNECTOR_TOOLS` ownership of the rebuilt flat RMEDO contracts and binds the canonical `ATOM_SEARCH` wrapper. Its rebuilt source authority uses the FEATURE's role folders, not an `ATOM_SEARCH` child folder. The existing executable collection remains at `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_SEARCH/`, explicitly bound to `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_SEARCH/atom_search.py`; it is not an independently registered Scope Unit. The new FEATURE Delivery root is future/unmaterialized and does not relocate that collection. It binds the current file adapter and the required logical Find contract; future logical behavior does not establish current implementation readiness. It does not define Core semantics, grammar adoption, migration decisions, source repair, graph publication, or completed live MCP acceptance.

## Claim

### Prose Claim

the `ATOM_SEARCH` Tool **must** deliver its canonical executable Carrier at `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_SEARCH/atom_search.py`; that Carrier realizes `CA-R-863` through the Action `CA-O-046`.

Use AN-S-5184 for local CLI Subject lookup, filter behavior and occurrence output.

## Details

### Required logical Find serialization

The query connector contract under CA-D-625 carries the selected logical kind, scope filters and a Subject criterion with field `governs`, `depends_on` or `both`, exact requested value and match mode `exact`, `prefix`, `suffix` or `contains`. It returns matching logical descriptors with IDs, Versions, exact occurrence values and source-state evidence, not complete Atom content. Apply AN-S-2478 to separate Read and Modify calls. The direct Subject subset below requires suffix/contains support; this does not assert that the historical CLI already implements those modes. Unknown fields or modes fail rather than widening a request.


The request resolves the configured Project control root and an optional declared subtree before traversal. Existing path, filename, frontmatter, content, exact-selector, output-view, and lifecycle behavior remains available. Subject lookup reads only valid current Atom files with a canonical flat `subjects` block; invalid source paths, symlink targets, projections, malformed carriers, duplicate fields/values, and owner/path disagreements are rejected or diagnosed without widening selection. Prefix matching ends only at a declared Subject delimiter, so a value such as `Artifact/Atom` does not match `Artifact/Atomology`.

The output carries one source pin per occurrence and no inferred target or native graph edge. The local CLI remains mutation-free: it performs no write, rename, repair, migration, Projection rebuild or history/Journal effect. The direct MCP delivery below is a required realization, not a claim of completed registration or live acceptance. CA-R-863 and CA-O-046 remain the governing Requirement and Action; CA-M-370 supplies the focused authoring method when that Method carrier is delivered.

### Direct read-only Subject MCP delivery

The canonical provider must declare this existing Tool binding and expose strict closed request/result models through the descriptor-driven MCP registry. Root is bound by the registry, never supplied by a caller. Descriptor hints do not replace canonical source validation.

```toml
[tool_binding]
name = "ATOM_SEARCH"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_SEARCH/atom_search.py"
action_ids = ["CA-O-046"]
mcp_name = "atom_search"
```

The public `SubjectLookupRequest` requires exactly `subject`, `subject_field`, `subject_match`, `subject_profile`, `scope_unit`, `content_roles` and `lifecycle`, with optional `atom_ids`. Required fields have no defaults. All models reject unknown fields and coercion. `subject` is nonempty text; fields are governs/depends_on/both, modes exact/prefix/suffix/contains and profiles legacy/approved. Exact/prefix criteria are valid complete expressions under the selected profile; suffix/contains criteria may be nonempty literal fragments. Complete selected source Subjects remain profile-validated.

`scope_unit` is one registered owning Scope Unit name, not a new stable-ID or physical-path scheme. `content_roles` is an explicit nonempty unique array from Concern/Analysis & Advisory/Plan/Requirement/Method/Evaluation/Delivery/Operations. `lifecycle` explicitly selects active/draft/archived/done/resolved/canceled/all using the existing private lookup inclusion rules; all intentionally includes the wider lifecycle set rather than silently choosing current-only. Optional `atom_ids` contains unique complete logical Atom IDs; omission or an empty array imposes no extra ID restriction. No caller root, under, path, filename, index, body query, context/authorization reference, approval flag, Session ID or preview/execute option is accepted. Unsupported Type, target Scope Unit, arbitrary projection and other generic Find filters fail rather than widen the request.

The public `SubjectLookupResult` has exactly `data`, `current_state`, `effects` and `errors`. On complete success, data is exactly `{matches, complete: true, subject_profile, subject_profile_evidence}`. Each match is exactly `{atom_id, version, status, current_scope_unit, updated_at, field, value}`; field is governs or depends_on, and separate matching fields remain separate rows. Sort by Atom ID, Version, field and exact value. No full Atom content, private path or dependency index is returned.

Current state is an array of unique `{identity, version, source_token, source_view}` records per matched carrier, preserving historical Versions; source_token is the complete-byte SHA-256 and source_view is exactly `{scope_unit, content_roles, lifecycle}`. Profile evidence is exactly `{grammar_pins, native_admission: not_performed}`, with each public pin exactly `{atom_id, version, sha256}`; physical pin paths remain private. Effects are always an empty array. Errors follow D625's exact code/message/field schema. A complete empty match returns empty matches/state/errors. A selected-source diagnostic, ambiguity, stale or incomplete frontier, unsupported input or exceeded read budget returns null data/current_state and nonempty errors; partial results are not successful complete coverage.

Validate current Delivery/Action and applicable Requirement/Method/shared definition pins, the selected grammar pins, Project settings/structure and selected-source evidence. Use bounded no-follow reads, preserve possible selected-current-ID collision checks without full admission of unrelated excluded C/A, and recheck source bytes and inventory before returning. Static reported hashes alone are insufficient. Do not require absent Type on otherwise eligible selected R/M/D sources.

Apply the named direct read-only Subject lookup exception in AN-S-2478. This realization creates no scratch staging artifact. Existing CLI and Session-based behavior, and all preview/staging/publication admission, remain unchanged. Installed binding/code refresh and actual registered/connected-MCP acceptance are separate from this source declaration.
