---
atom_family: SPEC
atom_id: AN-S-1992
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: "archived"
  version: 35
  updated_at: "2026-11-25T23:05:43.372034+00:00"
---

## Summary

Read Engine settings through one shared boundary

## Claim

When PROGRAMMATIC behavior depends on Project settings, every applicable Tool, App and MCP component uses one shared Reader for the authoritative Project Manifest. The Reader validates the complete input and returns an immutable typed snapshot of actual values, the exact selected Project, physical source path, raw SHA-256 Digest and declared schema marker. It does not query the Work Journal or determine logical Revision or currentness. The snapshot is derived and is not a Projection.

The Reader and dedicated write operation use one shared Carrier adapter bound to the exact authoritative Manifest. The adapter writes only a complete validated document supplied by that operation; validation failure leaves the file unchanged. Pass the snapshot explicitly to consumers; do not add component-specific parsers, defaults, environment fallbacks, semantic overrides or Reader writes. The control panel uses the same Reader and requests changes through the dedicated write operation. Stop for a missing or invalid Manifest, absent path or Digest provenance, or a consumer that bypasses or mutates the snapshot.


### Legacy configuration reads

The Applicable Methodology compatibility reader uses the selected Core Meta-Model's `anechoic_framework_default_settings.toml` and the selected control root's `000_ANECHOIC_framework/anechoic_framework_settings.toml`. Bind present files to their actual paths and digests. Apply instance selections over defaults.

The TOML settings use their legacy schema. Preserve authority modes, admission settings, configured roots, and integer confidence percentages when reading or migrating them. A configuration file holds selected settings. Derived values and Atom metadata do not become independently authored settings.

A legacy `scope_path` excludes the ambient Project. Use an empty path for Project scope. Preserve the explicit timezone and numeric offset of legacy Artifact timestamps. Native edits use the native Atom timestamp rule.

Legacy Scope Unit exports can report names and obsolete names from Project settings. The settings own these values.

Legacy Framework Settings read `[interaction].reporting_mode` as `silent` or `verbose`. Treat this field as presentation settings for those readers.

The legacy confidence fields are `confidence.necessary_information_threshold_percent` and `confidence.semantic_resolution_threshold_percent`. Use the compatibility reader for explicit per-Plan `ai_agent_confidence_threshold` and its former alias. Native settings follow the Project Manifest.
