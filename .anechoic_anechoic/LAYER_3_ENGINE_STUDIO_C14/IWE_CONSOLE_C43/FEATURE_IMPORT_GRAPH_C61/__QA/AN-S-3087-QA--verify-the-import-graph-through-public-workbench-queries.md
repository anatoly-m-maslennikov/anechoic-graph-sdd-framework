---
atom_family: SPEC
atom_id: AN-S-3087
structure:
  container:
    component: C61
  tier: 2
context:
  lens: QA
relations:
  REFERENCES:
  - AN-S-3083
  - AN-T-2928@1-draft
state:
  status: "active"
  version: 4
  updated_at: "2026-11-20T22:44:56.273982+00:00"
---

## Summary

Verify the Import Graph through public Workbench queries

## Claim

### Prose Claim

- Verify selected Project imports from source selection through SQL publication.
- Scan an authored Module without the executable bit and a file with zero imports.
- Include an unsupported script, unreadable source, invalid source, and generated Git copy.
- Verify the inventory, exclusions, and distinct scan statuses.
- Keep unsupported scripts as ordinary inventory statuses.
- Verify stderr reports unreadable or invalid files with their paths.
- Verify unreadable and invalid files supply no import facts.
- Query `import_read_issues` for the current path and error message.
- Verify the next ordinary scan reads a failed file with an unchanged fingerprint.
- Verify that a successful read or file removal clears its issue.
- Verify the scan does not retry or recover within the same attempt.

- Check absolute, relative, conditional, external, ambiguous, and unresolved imports.
- Keep repeated imports on different lines.
- Verify comments, exports, and dynamic loads supply no import edges.
- When frontend parsers exist, check type-only, mixed, and side-effect imports.
- Resolve `operation_error_boundary` from MCP with `FEATURE_TOOLS` as a source root.
- With frontend parsing, test `App.svelte` imports of local `.svelte` and extensionless paths.
- Check all four directed Module and Package pairs against one import occurrence.
- Check direct Package imports, unknown ownership, intra-Package edges, and cycles.
- Compare incoming and outgoing results in Workbench and through its terminal endpoint.

- Add, edit, move, and delete source outside the Workbench pilot.
- Verify updates use the existing watcher queue.
- Add and remove an import target. Verify it resolves again without reparsing its importer.
- Verify changes to Atoms and generated files cause no import parsing.
- Query Atom and import edges with `GRAPH_TABLE` before and after a graph layout change.
- Force an import publication failure. Verify stderr and no partial publication.

- Use a direct `<full package folder name>__tests/` folder.
- Verify its Relations when the parent has no Spec or Spec Binding.
- Query both `TESTS` and `IS_TESTED_BY` and check `package_type` is `Test Package`.
- Check that imports and test Relations use the same Package keys.
- Check that one folder with several source languages has one Package node.
- Check that an executable in an unsupported language qualifies each ancestor. Skip dot, empty, and asset-only folders.
- Add and remove the last executable in a subtree. Verify the Package and audit rows update.
- Move the test directory beside the Package, restore it, and delete it.
- Verify the test Relation follows the direct test directory.
- Check a test file with zero imports.

## Package audit acceptance

- Query every local Package node. Verify both visibility flags and that a nested marked Module does not affect its ancestor Package.
- Check valid, missing, empty, malformed, and legacy-only bindings. Distinguish archived and missing exact pins.
- Compare the Package Contract's current exact `implements` pin with an `applies` pin or an older revision. Verify Packages without a Spec have unknown Contract coverage.
- Remove a Contract from the Package Spec and verify the audit remains queryable with unknown coverage and a stderr diagnostic.
- Change a visibility marker, Spec Binding, and Spec version. Verify the SQL rows refresh and a targeted rebuild preserves the results.
