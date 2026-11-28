"""Native contract graph test cases."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.contracts__shared"
)
compose_contract_graph = _graph.compose_contract_graph
render_contract_graph = _graph.render_contract_graph
extract_claim_constraints = _graph.extract_claim_constraints
compose_narrowing_graph = _graph.compose_narrowing_graph
build_subject_projection_data = _graph.build_subject_projection_data
carrier, body = _support.carrier, _support.body


class NativeContractCases1:
    def test_ambiguous_native_inverse_does_not_create_a_derived_view(self):
        def direct(atom_id, name):
            return carrier(
                atom_id,
                "Relation//" + name,
                body(
                    "### Formal Claim",
                    "```python",
                    "from anechoic.formal_claims import declare_relation",
                    f"declare_relation(relation_name='{name}', "
                    "source_endpoint={'level':'instances'},",
                    (
                        "  target_endpoint={'level':'instances'},"
                        " inverse_alias='SHARED')"
                    ),
                    "```",
                    semantics="Direct meaning.",
                ),
            )

        graph = compose_contract_graph(
            [direct("CA-R-1", "FIRST"), direct("CA-R-2", "SECOND")]
        )
        self.assertTrue(
            all("derived_aliases" not in row for row in graph["relations"])
        )
        declared = carrier(
            "CA-R-3",
            "Relation//SHARED",
            body("### Prose Claim", "Other meaning."),
        )
        graph = compose_contract_graph([direct("CA-R-1", "FIRST"), declared])
        self.assertTrue(
            all("derived_aliases" not in row for row in graph["relations"])
        )

    def test_native_forms_with_same_local_class_name_keep_distinct_parents(
        self,
    ):
        carriers = self.form_carriers()
        tree, _ = compose_narrowing_graph(carriers)
        identities = {node["id"]: node["identity"] for node in tree["nodes"]}
        edges = {
            (
                identities[edge["relation_source"]],
                identities[edge["relation_target"]],
            )
            for edge in tree["edges"]
        }
        for role in ("Method", "Evaluation"):
            parent = f"Atom/(.Header.Context.Role:={role})"
            self.assertIn(
                (parent + "/(.Header.Context.Form:=Decision)", parent), edges
            )

    def form_carriers(self):
        root = carrier("CA-R-1", "Atom", body())
        carriers = [root]
        for index, role in enumerate(("Method", "Evaluation"), 2):
            parent = f"Atom/(.Header.Context.Role := {role})"
            carriers.append(
                carrier(
                    f"CA-R-{index}",
                    parent,
                    body(
                        "### Formal Claim",
                        "```python",
                        "from anechoic.formal_claims import declare_entity",
                        "from anechoic.model import Atom",
                        f"class {role}(Atom):",
                        "    pass",
                        f"declare_entity(entity_class={role}, "
                        f"entity_name='{role}')",
                        "```",
                    ),
                )
            )
            carriers.append(
                carrier(
                    f"CA-R-{index + 10}",
                    parent + "/(.Header.Context.Form := Decision)",
                    body(
                        "### Formal Claim",
                        "```python",
                        "from anechoic.formal_claims import declare_entity",
                        f"from anechoic.model import {role}",
                        f"class Decision({role}):",
                        "    pass",
                        (
                            "declare_entity(entity_class=Decision, en"
                            "tity_name='Decision')"
                        ),
                        "```",
                    ),
                )
            )
        return carriers

    def test_native_namespace_classification_keeps_source(self):
        row = carrier(
            "CA-R-1",
            "ANECHOIC_MODEL",
            body(
                "### Formal Claim",
                "```python",
                "from anechoic.formal_claims import declare_entity",
                "from anechoic.model import Node",
                "class Model(Node):",
                "    pass",
                (
                    "declare_entity(entity_class=Model, entit"
                    'y_name="MODEL", axes={"Container": "yes"'
                    "})"
                ),
                "```",
            ),
        )
        graph = compose_contract_graph([row])
        (namespace,) = graph["namespaces"]
        (entry,) = namespace["own"]
        (condition,) = [
            clause
            for clause in entry["clauses"]
            if clause["kind"] == "axis_condition"
        ]
        self.assertEqual(
            ("MODEL", "Container", "==", "yes"),
            tuple(
                condition[key]
                for key in ("subject_selector", "axis", "operator", "value")
            ),
        )
        self.assertEqual(row["source"], condition["source"])
        self.assertIn(
            "MODEL >| Container == yes", render_contract_graph(graph)
        )
