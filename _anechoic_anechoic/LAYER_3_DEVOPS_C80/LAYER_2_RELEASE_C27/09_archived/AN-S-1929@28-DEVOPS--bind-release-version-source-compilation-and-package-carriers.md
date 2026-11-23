---
atom_family: SPEC
atom_id: AN-S-1929
container:
  component: C27
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 28
  updated_at: '2026-11-21T21:51:42.719385+00:00'
---

## Summary

Bind Release Version source, compilation, and package carriers

## Scope

The checked-in Methodology sources and package copies used by direct local release, and the shared Methodology export helper.

## Claim

Release Version **must** bind Methodology delivery to its selected checked-in assets without importing ANECHOIC runtime Components. The direct `LAYER_1_FRAMEWORK_METHODOLOGY/` product, runtime package copies and any shared export remain derived deliveries that preserve their original source relations, never replacement authoring authority or Action authorization.

## Details

### Direct local release

1. Select the Active native Specs in the Meta-ontology Component. Exclude Drafts and Archived revisions.
2. Check selected paths and inputs for safety and refuse changes during selection. Do not invoke the native Model or runtime Components.
3. Copy the selected files under `LAYER_1_FRAMEWORK_METHODOLOGY/SUPERLAYER_1_METHODOLOGY_SOURCES/`. Preserve their paths relative to the Project control root.
4. Copy those sources to `METHODOLOGY/sources/` in the runtime package. Verify the prepared bytes before installation. C19 unit checks precede preparation; C19 end-to-end and canary checks precede installation.
5. Preserve source Atom IDs, Versions, Relations and bytes. Replace only the derived delivery and preserve settings and unrelated files.

### Shared Methodology export

The existing `methodology_export.py` and inventory helper remain reusable. Their frozen source/export format is not a required sealed-release package, a standalone installer, a runtime selector or a release admission gate.

1. A Project export receives its exact Project root explicitly. Resolve its control child, Methodology source root and canonical Framework Instance Settings through that Project's declared controls; the resolved source root must equal the requested source root. Never infer the Project by scanning ancestors or copying settings into the source tree.
2. Frozen export schema `anechoic.methodology_export.frozen.v3` retains `project_binding`, `binding_atoms` and `framework_engine_inventory_sha256`. `project_binding` records the resolved Project root, control/source paths and exact Project Settings, Project Structure and Framework Instance Settings carrier paths/digests, or is `null` for detached Core-only input. Record an absent optional Framework Instance Settings carrier explicitly. These are derived input traces, not another settings authority.
3. Each `binding_atoms` member has exactly `atom_id`, positive integer `version`, safe Project-relative `source_path` and lowercase raw-source `sha256`. The complete eligible set is every current Active Delivery Atom in the selected Project/control snapshot whose one closed `tool_binding.entrypoint` names a regular member of the recorded complete Framework Engine inventory. Include every eligible declaration exactly once; refuse missing, duplicate, ambiguous, inactive, stale or additionally discovered eligible sources. Do not hardcode Atom IDs, Tool names or cardinality.
4. `framework_engine_inventory_sha256` is the lowercase SHA-256 of that complete inventory, or `null` only for detached Core-only input, whose binding frontier is empty. Reopen the Project controls, inventory and selected sources before export publication; refuse changed inputs. A detached input cannot select an Extension or Project Configuration or claim Project-specific applicability.
5. Binding source bytes are private compiler input. Reuse the canonical projection metadata formatter and source-preservation validator to emit a derived Carrier under `methodology/bindings/`. Preserve the exact source Atom ID, Version, raw SHA-256, original source path and original Relations digest. Removing the canonical metadata insertion must recover the exact pinned source bytes.
6. Freeze the selected Atom, support and catalog inputs and retain their inventory with the exported bytes. Support remains support; binding projections never become compiler Atom input. Preserve the authoring-source inventory before and after export. Historical frozen schemas v1/v2 remain read-only evidence and cannot authorize a new export or supply invented binding fields.

### Publication boundary

Direct local release uses its verified prepared product and runtime package. It does not require the retired reusable-package promotion, standalone installer, Full Gate, closed release registry or previous Journal records. Keep file/path checks and source-preservation checks at the copying boundary. Release Version does not call Journal.
