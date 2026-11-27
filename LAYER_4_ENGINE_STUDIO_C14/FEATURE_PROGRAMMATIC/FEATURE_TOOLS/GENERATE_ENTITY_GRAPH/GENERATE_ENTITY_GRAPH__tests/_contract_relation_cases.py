"""Direct and scoped contract relation cases."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support"
)
compose_contract_graph = _graph.compose_contract_graph
render_contract_graph = _graph.render_contract_graph
extract_claim_constraints = _graph.extract_claim_constraints
build_subject_projection_data = _graph.build_subject_projection_data
carrier, body = _support.carrier, _support.body


class ContractRelationCases1:
    def _minimal_inverse(
        self,
    ):
        direct, inverse = self.inverse_carriers()
        graph = compose_contract_graph([direct, inverse])
        row = next(
            row for row in graph["relations"] if row["target"] == "INVERSE"
        )
        self.assertEqual("Derived", row["derived_view"]["classification"])
        self.assertEqual("Direct meaning.", row["derived_view"]["meaning"])
        self.assertEqual(
            [{"host": "$right", "target": "$left"}],
            row["derived_view"]["endpoints"],
        )
        self.assertEqual([], row["host_target"])
        self.assertEqual(0, graph["coverage"]["missing_relation_semantics"])
        self.assertIn("not new permissions", render_contract_graph(graph))

        self.check_ambiguous_inverse(direct, inverse)

    locals()[
        (
            "test_minimal_inverse_uses_corroborated_d"
            "irect_meaning_and_reversed_endpoint_view"
        )
    ] = _minimal_inverse

    def inverse_carriers(self):
        direct = carrier(
            "CA-R-1",
            "CFEL <+ Relation//DIRECT",
            body(
                "### Formal Claim",
                "```python",
                "relation(source='$left', name='DIRECT', target='$right')",
                (
                    "relation(source='Relation//DIRECT', name"
                    "='HAS_INVERSE', target='Relation//INVERS"
                    "E')"
                ),
                (
                    "classify(address='Relation//DIRECT', axi"
                    "s='Derivation', value='Direct', notation"
                    "='relation')"
                ),
                "```",
                "### Prose Claim",
                "Direct meaning.",
            ),
        )
        inverse = carrier(
            "CA-R-2",
            "CFEL <+ Relation//INVERSE",
            body(
                "### Formal Claim",
                "```python",
                (
                    "relation(source='Relation//INVERSE', nam"
                    "e='HAS_INVERSE', target='Relation//DIREC"
                    "T', reverse=True)"
                ),
                "```",
            ),
        )
        return direct, inverse

    def check_ambiguous_inverse(self, direct, inverse):
        missing = compose_contract_graph([inverse])
        self.assertEqual(1, missing["coverage"]["missing_relation_semantics"])
        self.assertNotIn("derived_view", missing["relations"][0])
        conflicting = carrier(
            "CA-R-3",
            "CFEL <+ Relation//OTHER",
            body(
                "### Formal Claim",
                "```python",
                (
                    "relation(source='Relation//OTHER', name="
                    "'HAS_INVERSE', target='Relation//INVERSE"
                    "')"
                ),
                (
                    "classify(address='Relation//OTHER', axis"
                    "='Derivation', value='Direct', notation="
                    "'relation')"
                ),
                "```",
                "### Prose Claim",
                "Other meaning.",
            ),
        )
        ambiguous = compose_contract_graph([direct, inverse, conflicting])
        inverse_row = next(
            row for row in ambiguous["relations"] if row["target"] == "INVERSE"
        )
        self.assertNotIn("derived_view", inverse_row)

    def test_relation_declaration_and_scoped_property_projection(self):
        rows = self.scoped_rows()
        data = build_subject_projection_data(rows)
        entities = {row["identity"]: row for row in data["entities"]}
        method = entities["Atom/(.Header.Context.Role:=Method)"]
        plan = entities["Atom/(.Header.Context.Role:=Plan)"]
        self.assertIn(
            "Content.Semantics",
            [row["relative_name"] for row in method["inherited_properties"]],
        )
        semantics = next(
            row
            for row in method["inherited_properties"]
            if row["relative_name"] == "Content.Semantics"
        )
        self.assertEqual("markdown", semantics["effective_value_format"])
        self.assertEqual(
            "CA-R-6", semantics["effective_value_format_sources"][0]["atom_id"]
        )
        self.assertNotIn(
            "Content.Semantics",
            [row["relative_name"] for row in plan["inherited_properties"]],
        )
        self.assertIn("CARRIES", data["declarations"]["relations"])

    def scoped_rows(self):
        rows = [carrier("CA-R-1", "Atom", body())]
        for index, role in enumerate(("Method", "Plan"), 2):
            rows.append(
                carrier(
                    f"CA-R-{index}",
                    f"Atom/(.Header.Context.Role := {role})",
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
        rows.append(
            carrier(
                "CA-R-6",
                "Atom.Content",
                body(
                    "### Formal Claim",
                    "```python",
                    "from anechoic.formal_claims import declare_entity",
                    (
                        "declare_entity(entity_name='Content', re"
                        "lation_name='IS_PROPERTY_OF', base_path="
                        "'Atom',"
                    ),
                    "  recursive_dependent_property_value_format='markdown')",
                    "```",
                ),
            )
        )
        self.add_scoped_rows(rows)
        return rows

    def add_scoped_rows(self, rows):
        rows.append(
            carrier(
                "CA-R-4",
                "Atom.Content.Semantics",
                body(
                    "### Formal Claim",
                    "```python",
                    "from anechoic.formal_claims import declare_entity",
                    "from anechoic.model import Method",
                    (
                        "declare_entity(entity_name='Semantics', "
                        "relation_name='IS_PROPERTY_OF', base_pat"
                        "h='Atom.Content', applies_to_entity_clas"
                        "ses=(Method,), value_cardinality=1)"
                    ),
                    "```",
                ),
            )
        )
        rows.append(
            carrier(
                "CA-R-5",
                "Relation//CARRIES",
                body(
                    "### Formal Claim",
                    "```python",
                    "from anechoic.formal_claims import declare_relation",
                    (
                        "declare_relation(relation_name='CARRIES'"
                        ", source_endpoint={'level':'instances'},"
                        " target_endpoint={'level':'instances'})"
                    ),
                    "```",
                ),
                form="Relation Declaration",
            )
        )
