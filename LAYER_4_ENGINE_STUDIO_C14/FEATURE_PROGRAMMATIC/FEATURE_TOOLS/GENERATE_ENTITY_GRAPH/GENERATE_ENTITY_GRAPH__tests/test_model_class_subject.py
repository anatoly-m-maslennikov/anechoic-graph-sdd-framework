from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__shared \
    import compose_contract_graph  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import class_bindings  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import model_class_target  # fmt: skip


def carrier(n, subject, entity):
    code = f'from anechoic.formal_claims import declare_entity\nfrom anechoic.model import Node\nclass Element(Node):\n    pass\ndeclare_entity(entity_class=Element, entity_name="{entity}")'
    return {
        "source": {"atom_id": f"CA-R-{n}", "version": 1, "path": f"{n}.md"},
        "subjects": {"governs": subject},
        "body": f"## Claim\n\n### Formal Claim\n\n```python\n{code}\n```\n",
        "read_view": {"content_role": "Requirement", "type": "Declaration"},
    }


def graph_bindings(rows):
    graph = compose_contract_graph(rows)
    return [
        (n["target"], entry["source"]["atom_id"])
        for k in ("entities", "components", "namespaces", "relations")
        for n in graph[k]
        for entry in n["own"]
        for c in entry["clauses"]
        if c["kind"] == "native_class"
    ]


class ModelClassSubjectTests(unittest.TestCase):
    def test_native_node_class_narrowing_keeps_exact_mixed_path(self):
        for local, name in [
            ("Node//Continuant//Actor//AI Agent", "AI Agent"),
            ("Node/Continuant/Actor//AI Agent//Main Agent", "Main Agent"),
            ("Node//Continuant//Actor//AI Agent//Subagent", "Subagent"),
        ]:
            with self.subTest(local=local):
                subject = "ANECHOIC_MODEL <+ " + local
                self.assertEqual(local, model_class_target(subject, name))
                bindings = class_bindings([carrier(1, subject, name)])
                self.assertEqual(local, bindings["Element"][0][0])

    def test_declared_relation_and_format_addresses_keep_their_paths(self):
        for address, name in [
            ("Relation//RUNS", "RUNS"),
            ("Format//markdown", "markdown"),
        ]:
            with self.subTest(address=address):
                self.assertEqual(
                    address,
                    model_class_target(f"ANECHOIC_MODEL <+ {address}", name),
                )

    def test_incomplete_or_mismatched_class_addresses_are_rejected(self):
        for subject, name in [
            ("ANECHOIC_MODEL <+ Node//Continuant//", "Continuant"),
            ("ANECHOIC_MODEL <+ Node//Continuant", "Different"),
            ("ANECHOIC_STRUCTURE <+ Node//Continuant", "Continuant"),
        ]:
            with self.subTest(subject=subject):
                self.assertIsNone(model_class_target(subject, name))

    def test_component_qualified_and_entity_agree(self):
        for subject, target in [
            ("ANECHOIC_MODEL <+ CFEL <+ Element", "Element"),
            ("ANECHOIC_MODEL <+ Element", "Element"),
            ("ANECHOIC_MODEL <+ Node/Element", "Node/Element"),
        ]:
            with self.subTest(subject=subject):
                rows = [carrier(1, subject, "Element")]
                bindings = class_bindings(rows)
                self.assertEqual([(target, "CA-R-1")], graph_bindings(rows))
                self.assertEqual(
                    [(target, "CA-R-1")],
                    [(x, s["atom_id"]) for x, s in bindings["Element"]],
                )

    def test_property_mismatched_name_and_wrong_namespace_rejected(self):
        for subject, name in [
            ("ANECHOIC_MODEL <+ Atom.Content.Foo", "Foo"),
            ("ANECHOIC_MODEL <+ CFEL <+ Element", "Other"),
            ("ANECHOIC_STRUCTURE <+ Element", "Element"),
            ("ANECHOIC_MODEL <+ Atom.Content.Foo", "Element"),
        ]:
            with self.subTest(subject=subject, name=name):
                rows = [carrier(1, subject, name)]
                self.assertEqual({}, class_bindings(rows))
                self.assertEqual([], graph_bindings(rows))

    def test_catalog_keeps_duplicate_sources(self):
        rows = [
            carrier(1, "ANECHOIC_MODEL <+ CFEL <+ Element", "Element"),
            carrier(2, "ANECHOIC_MODEL <+ CFEL <+ Element", "Element"),
        ]
        bindings = class_bindings(rows)
        self.assertEqual(2, len(bindings["Element"]))


if __name__ == "__main__":
    unittest.main()
