---
atom_family: SPEC
atom_id: AN-S-3087
structure:
  container:
    component: C61
  tier: 2
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T10:44:30.157383+00:00'
---

## Summary

Verify the Import Graph through public Workbench queries

## Claim

### Prose Claim

Verify that the selected Project's static import facts remain correct from source selection through publication and query.

1. Scan an authored Module without the executable bit, a file with zero imports, an unsupported script, an unreadable file, an invalid file, and a generated copy tracked by Git. Check inventory, exclusions, and distinct scan outcomes. Verify that unreadable and invalid files produce explicit path-specific errors on stderr and publish no import facts for the affected file. Keep unsupported scripts as ordinary inventory statuses.
2. Check absolute, relative, conditional, external, ambiguous, and unresolved imports. Check repeated imports on different lines and absence of edges for comments, exports, and dynamic loads. When frontend parsers are delivered, also check type-only, mixed, and side-effect declarations.
3. Resolve `operation_error_boundary` from the MCP entry point with the Project-relative `FEATURE_TOOLS` source root in the configuration. When frontend parsers are available, verify `App.svelte` resolves local `.svelte` and extensionless imports and distinguishes type-only from mixed declarations.
4. Use a Module in one Package that imports a Module in a second Package. Trace all four directed pairs to the same occurrence. Check a direct Package import, unknown Package ownership, intra-Package edges, and cycles. Compare incoming and outgoing results in Workbench and through its terminal SQL endpoint.
5. Edit, add, move, and delete source outside the Workbench pilot. Verify updates through the existing watcher queue. Add and remove a previously missing target and verify that resolution changes without reparsing the importing file. Verify Atom and generated-file changes cause no import parsing.
6. Query Atom and import edges using `GRAPH_TABLE` before and after an Atom relation-layout change. Force an import publication failure. Verify that it writes an explicit error to stderr and makes no partial publication.

## References

[Tier 1 Decision AN-S-3083](../DES/AN-S-3083-DES-DECISION--extend-workbench-with-the-import-graph.md), [Spec Proposal CA-A-1467](../../../../../.anechoic_legacy/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft/CA-A-1467@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md).
