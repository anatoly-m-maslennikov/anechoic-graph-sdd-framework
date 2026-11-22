"""Both Workbench schema modes and their deterministic generated asset."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (ContentRule, DeclarationSource, _schema_from_rules, compile_content_schema, content_schema_from_statements)  # noqa: E402
from KERNEL_MIXER_C59.declared_header_rules import compile_header_rules, header_rules_from_statements  # noqa: E402
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.generate_workbench_schema import (  # noqa: E402
    compile_project_schema,
    write_schema,
)
from KERNEL_MIXER_C59.header_columns import (  # noqa: E402
    declared_header_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workbench_schema_asset import (  # noqa: E402
    compile_schema,
    load_image_schema,
    schema_asset,
)


from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.workbench_schema_fixture import WorkbenchSchemaFixture, atom


class WorkbenchSchemaAssetTests(WorkbenchSchemaFixture):
    def test_asset_is_deterministic_pinned_and_rejected_when_stale(self) -> None:
        declaration = atom(
            "CA-R-DECL", form="Declaration",
            body="## Claim\n\n### Formal Claim\n\n```CFEL\nAtom.Content.Summary{::1}:: {::1};\n```\n",
        )
        content = compile_content_schema([declaration])
        header = declared_header_schema(compile_header_rules([declaration]))
        compilation = compile_schema([declaration], content, header)
        first = schema_asset([declaration], compilation)
        self.assertEqual(first, schema_asset([declaration], compilation))
        payload = json.loads(first)
        self.assertEqual(2, payload["schema_version"])
        self.assertEqual({"1", "2"}, set(payload["modes"]))
        self.assertEqual(["content.summary"], [item["name"] for item in payload["modes"]["2"]["content"]["content_columns"]])
        self.assertEqual(64, len(payload["input_digest"]))

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workbench_schema.json"
            write_schema(path, first)
            loaded = load_image_schema(path)
            self.assertEqual(compilation, loaded)
            stale = dict(declaration, _content_bytes=b"## Claim\n\nChanged.\n")
            self.assertNotEqual(first, schema_asset([stale], compile_schema([stale], content, header)))
            self.assertEqual(compilation, load_image_schema(path))


    def test_inherited_header_format_preserves_both_declaration_sources(self) -> None:
        parent = atom("CA-R-2716", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Carrier Destination.File.*:: [string];
```
""")
        name = atom("CA-R-2717", form="Declaration", body="""## Claim

### Formal Claim

```CFEL
Atom.Header.Carrier Destination.File.Name:: {::1};
```
""")
        path_atom = atom("CA-R-2718", form="Declaration", body=name["content_markdown"].replace("File.Name", "File.Path"))
        compilation = compile_schema([parent, name, path_atom], compile_content_schema([]))
        columns = {column.path[-1]: column for column in compilation.mode_one.columns}
        for field, reference in (("name", "CA-R-2717"), ("path", "CA-R-2718")):
            rule = columns[field].rules[0]
            self.assertEqual(reference, rule.source.reference)
            self.assertEqual("CA-R-2716", rule.format_source.reference)
        asset_path = Path(self.temporary.name) / "schema.json"
        asset_path.write_bytes(schema_asset([parent, name, path_atom], compilation))
        self.assertEqual(compilation, load_image_schema(asset_path))


    def test_image_asset_round_trips_all_content_rules_without_source_reads(self) -> None:
        source = DeclarationSource("CA-R-DECL", 7, "source/declaration.md")
        content = _schema_from_rules([
            ContentRule(("container",), frozenset({"Requirement"}), frozenset({"Declaration"}), False, source),
            ContentRule(("container", "value"), None, None, True, source),
            ContentRule(("container", "*"), None, None, False, source, prohibited=True),
            ContentRule(("container", "**"), None, None, True, source),
        ])
        compilation = compile_schema([], content, declared_header_schema(()))
        path = Path(self.temporary.name) / "schema.json"
        path.write_bytes(schema_asset([], compilation))
        with patch("IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workbench_schema_asset.compile_schema", side_effect=AssertionError("source reread")):
            loaded = load_image_schema(path)
        self.assertEqual(compilation, loaded)
        self.assertEqual(content.rules, loaded.content.rules)
        self.assertEqual(content.sources, loaded.content.sources)
        payload = json.loads(path.read_bytes())
        payload["modes"]["1"]["content"]["rules"][0]["prohibited"] = True
        path.write_text(json.dumps(payload))
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            load_image_schema(path)
        payload.pop("input_digest")
        payload["input_digest"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
        path.write_text(json.dumps(payload))
        with self.assertRaises(ValueError):
            load_image_schema(path)


    def test_header_ancestry_and_wildcard_provenance_round_trip(self) -> None:
        ancestor = DeclarationSource("CA-R-PARENT", 1, "parent.md")
        binding = DeclarationSource("CA-R-FORM", 2, "form.md")
        occurrence = DeclarationSource("CA-R-CHILD", 3, "child.md")
        wildcard = DeclarationSource("CA-R-FORMAT", 4, "format.md")
        wildcard_ancestor = DeclarationSource("CA-R-OTHER-PARENT", 5, "other-parent.md")
        wildcard_binding = DeclarationSource("CA-R-OTHER-FORM", 6, "other-form.md")
        rules = header_rules_from_statements([
            ("Atom/Workflow", ancestor),
            ("Workflow.Header.Form:: [in (Workflow)]", binding),
            ("Workflow.Header.Context.Label:: {::1}", occurrence),
            ("Atom/FormatOwner", wildcard_ancestor),
            ("FormatOwner.Header.Form:: [in (Workflow)]", wildcard_binding),
            ("FormatOwner.Header.Context.*:: [string]", wildcard),
        ])
        child = next(rule for rule in rules if rule.path == ("context", "label"))
        self.assertEqual(occurrence, child.source)
        self.assertEqual(wildcard, child.format_source)
        self.assertEqual((ancestor, binding, wildcard_ancestor, wildcard_binding), child.provenance)
        declared = declared_header_schema(rules)
        compilation = compile_schema([], _schema_from_rules([]), declared)
        path = Path(self.temporary.name) / "header-provenance.json"
        path.write_bytes(schema_asset([], compilation))
        loaded = load_image_schema(path)
        self.assertEqual(declared, loaded.mode_one)
        self.assertEqual(declared.shape, loaded.mode_one.shape)
        payload = json.loads(path.read_bytes())
        rule = next(c for c in payload["modes"]["1"]["header"]["header_columns"]
                    if c["name"] == "header.context.label")["rules"][0]
        rule["provenance"].append(rule["provenance"][0])
        payload.pop("input_digest")
        payload["input_digest"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
        path.write_text(json.dumps(payload))
        with self.assertRaises(ValueError):
            load_image_schema(path)


    def test_content_ancestry_provenance_round_trips_separately_from_occurrence(self) -> None:
        ancestry = DeclarationSource("CA-R-ANCESTRY", 1, "ancestry.md")
        binding = DeclarationSource("CA-R-BINDING", 2, "binding.md")
        occurrence = DeclarationSource("CA-R-PROPERTY", 3, "property.md")
        content = content_schema_from_statements([
            ("Atom/(.Header.Role: Operations)/Workflow", ancestry),
            ("Workflow.Header.Form:: [in (Workflow)]", binding),
            ("Workflow.Content.Steps[string]", occurrence),
        ])
        rule = next(rule for rule in content.rules if rule.path == ("steps",))
        self.assertEqual(occurrence, rule.source)
        self.assertEqual((ancestry, binding), rule.provenance)
        self.assertEqual({ancestry, binding, occurrence}, set(content.sources))
        shared = content_schema_from_statements([
            ("Atom/Workflow", ancestry), ("Atom/Workflow", ancestry),
            ("Workflow.Header.Form:: [in (Workflow)]", occurrence),
            ("Workflow.Header.Form:: [in (Workflow)]", occurrence),
            ("Workflow.Content.Steps[string]", occurrence),
        ])
        shared_rule = next(rule for rule in shared.rules if rule.path == ("steps",))
        self.assertEqual((ancestry, occurrence), shared_rule.provenance)
        self.assertEqual(occurrence, shared_rule.source)
        compilation = compile_schema([], content, declared_header_schema(()))
        path = Path(self.temporary.name) / "provenance.json"
        path.write_bytes(schema_asset([], compilation))
        loaded = load_image_schema(path)
        self.assertEqual(content.rules, loaded.content.rules)
        self.assertEqual(content.shape, loaded.content.shape)
        self.assertEqual(content.columns[0].applies({"role": "Operations", "form": "Workflow"}),
                         loaded.content.columns[0].applies({"role": "Operations", "form": "Workflow"}))
        payload = json.loads(path.read_bytes())
        contributors = payload["modes"]["1"]["content"]["rules"][0]["provenance"]
        contributors.append(contributors[0])
        payload.pop("input_digest")
        payload["input_digest"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
        path.write_text(json.dumps(payload))
        with self.assertRaises(ValueError):
            load_image_schema(path)


    def test_image_asset_rejects_missing_and_incomplete_payload(self) -> None:
        path = Path(self.temporary.name) / "missing.json"
        with self.assertRaises(ValueError):
            load_image_schema(path)
        path.write_text('{}')
        with self.assertRaises(ValueError):
            load_image_schema(path)


    def test_project_generator_uses_one_reader_capture_and_writes_exact_bytes(self) -> None:
        row = atom(header={"atom_id": "CA-R-1"})
        draft = atom("CA-R-2", header={"atom_id": "CA-R-2"}, body="## Summary\n\nEdited Draft.\n")
        draft["status_group"] = "Draft"
        reader = Mock(capture=Mock(side_effect=[([row], []), ([row, draft], [])]), model_rows=Mock(return_value=[]))
        with patch(
            "IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.generate_workbench_schema.SourceReader",
            return_value=reader,
        ):
            first = compile_project_schema(Path("/project"))
            second = compile_project_schema(Path("/project"))
        self.assertEqual(first, second)
        self.assertEqual(2, reader.capture.call_count)
        self.assertEqual([], json.loads(first)["sources"])


    def test_project_generator_emits_declared_status_groups(self) -> None:
        row = atom(form="Declaration", body="""## Claim

### Formal Claim

```python
from anechoic.model import Plan
from anechoic.formal_claims import declare_entity
declare_entity(
    entity_name="Status", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.State",
    applies_to_entity_classes=(Plan,), allowed_values=("Backlog", "Done"),
    status_groups={"Backlog": "Backlog"},
)
```
""")
        ordinary = atom("CA-R-2", body="## Claim\n\n### Formal Claim\n\n```python\nvalue = 1\n```\n")
        rows = [row, ordinary]
        reader = Mock(capture=Mock(return_value=(rows, [])), model_rows=Mock(return_value=rows))
        with patch(
            "IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.generate_workbench_schema.SourceReader",
            return_value=reader,
        ):
            asset = json.loads(compile_project_schema(Path("/project")))
        self.assertEqual([["Plan", "Backlog", "Backlog"]], asset["status_groups"])

if __name__ == "__main__":
    unittest.main()
