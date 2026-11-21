---
atom_family: SPEC
atom_id: AN-S-3085
container:
  component: C61
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: '2026-11-20T23:12:09.705525+00:00'
---

## Summary

Resolve imports and derive Module and Package relations

## Claim

### Prose Claim

Use the import relations as a dependency view of the selected Project's Realization Graph. Resolve each occurrence from the Module whose file contains the import. When one statement names distinct import targets, keep an occurrence for each target. Use declared Package boundaries, source roots, and alias mappings. Use the ordered Project-relative Python roots supplied by the selected launch profile in the Import Graph configuration. The default root is `.`. A later frontend parser uses the frontend's declared TypeScript resolution mode. Resolve a name in a Python `from` import as a submodule only when static evidence supports it. Use the selected environment or package declarations to identify external targets. Retain ambiguous and unresolved occurrences with their written specifiers and resolution status.

Publish one local Package per folder whose subtree contains an executable file. Empty and asset-only subtrees do not qualify.

Keep distinct Module identities for files in different locations. Package discovery does not change language-specific import resolution. Identify a Python Module's Package by the top-level Package under its selected source root. Use the nearest package manifest for JavaScript, TypeScript, and Svelte, and the declared identity for external Packages. Leave Package ownership unset when evidence is missing. Attribute each import in a Package initializer to its source file. Use that file's Package for Package-level relations.

| Directed pair | Derivation |
| --- | --- |
| Module → Module | The import resolves to the target Module. |
| Module → Package | The import resolves to the target Package, or the target Module belongs to that Package. |
| Package → Module | The source Module belongs to the source Package, and the import resolves to the target Module. |
| Package → Package | The source Module belongs to the source Package, and the import resolves to the target Package or to a Module in it. |

Emit each applicable pair once per occurrence. Mark edges based on Module ownership as derived. Keep intra-Package imports and cycles visible. A Module with unknown Package ownership stays queryable at Module level. Keep repeated imports on separate source locations. Every edge references an occurrence with its importing Module, Project-relative file, line, column, and written specifier.

## References

[Tier 1 Decision AN-S-3083](AN-S-3083-DES-DECISION--extend-workbench-with-the-import-graph.md), [Spec Proposal CA-A-1467](../../../../../.anechoic_legacy/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft/CA-A-1467@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md).
