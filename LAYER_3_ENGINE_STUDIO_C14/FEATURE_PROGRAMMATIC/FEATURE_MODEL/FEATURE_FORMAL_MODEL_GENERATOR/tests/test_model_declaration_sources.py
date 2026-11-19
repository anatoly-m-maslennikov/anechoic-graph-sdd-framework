"""Select only complete native Model Declaration Claims."""

from pathlib import Path
import sys
import unittest


PROGRAMMATIC = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS")]

from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import (
    _class_property_aliases, _relation_registry, select_model_claims,
)


CLAIM = "from anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name='Atom')\n"


def carrier(subject="ANECHOIC_MODEL <+ Atom", *, identifier="CA-R-1", status="active", body=None):
    if body is None:
        body = f"## Claim\n\n### Formal Claim\n\n```python\n{CLAIM}```\n"
    return {
        "source": {"path": f"{identifier}.md", "atom_id": identifier},
        "read_view": {"status": status, "content_role": "Requirement"},
        "subjects": {"governs": subject},
        "body": body,
    }


class ModelDeclarationSourceTests(unittest.TestCase):
    def test_claim_language_descriptors_stay_outside_the_generated_model(self):
        language = carrier("ANECHOIC_MODEL <+ CFEL", identifier="CA-R-2", body="")
        operator = carrier("ANECHOIC_MODEL <+ CFEL <+ Operator//Delivery", identifier="CA-R-3", body="")
        self.assertEqual(select_model_claims([language, operator, carrier()]), (CLAIM,))
        value_format = carrier("ANECHOIC_MODEL <+ CFEL <+ Format", identifier="CA-R-4", body="")
        with self.assertRaisesRegex(ValueError, "CA-R-4.md: expected one Formal Claim"):
            select_model_claims([carrier(), value_format])

    def test_selects_model_and_ignores_structure_and_draft(self):
        model = carrier()
        structure = carrier("ANECHOIC_STRUCTURE <+ Scope Unit//ENGINE", identifier="CA-R-2", body="")
        draft = carrier(identifier="CA-R-3", status="draft", body="")
        self.assertEqual(select_model_claims([structure, draft, model]), (CLAIM,))

    def test_duplicate_subject_and_identifier_fail_with_source(self):
        with self.assertRaisesRegex(ValueError, "CA-R-2.md: duplicate Declaration Subject"):
            select_model_claims([carrier(), carrier(identifier="CA-R-2")])
        with self.assertRaisesRegex(ValueError, "CA-R-1.md: duplicate Current Declaration ID"):
            select_model_claims([carrier(), carrier("ANECHOIC_MODEL <+ Node")])

    def test_mixed_missing_unclosed_and_non_native_claims_fail(self):
        formal = "## Claim\n### Formal Claim\n"
        bodies = (
            formal,
            formal + f"```python\n{CLAIM}```\n```CFEL\nNode\n```\n",
            formal + f"```python\n{CLAIM}",
            formal + "```python\nproperty_rule(address='Atom.Name')\n```\n",
        )
        for body in bodies:
            with self.subTest(body=body), self.assertRaisesRegex(ValueError, "CA-R-1.md:"):
                select_model_claims([carrier(body=body)])

    def test_prose_example_is_not_a_formal_claim(self):
        body = f"## Claim\n### Prose Claim\n```python\n{CLAIM}```\n"
        with self.assertRaisesRegex(ValueError, "expected one Formal Claim"):
            select_model_claims([carrier(body=body)])

    def test_class_must_match_its_main_subject(self):
        claim = (
            "from anechoic.formal_claims import declare_entity\n"
            "class Atom:\n    pass\n"
            "declare_entity(entity_name='Atom', entity_class=Atom)\n"
        )
        body = f"## Claim\n### Formal Claim\n```python\n{claim}```\n"
        with self.assertRaisesRegex(ValueError, "declared class does not match its Main Subject"):
            select_model_claims([carrier("ANECHOIC_MODEL <+ Node", body=body)])

    def test_rejects_ambiguous_sibling_order_before_generation(self):
        body = (
            "## Claim\n### Formal Claim\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Header', relation_name='IS_PROPERTY_OF', base_path='Atom', "
            "ordered_dependent_property_pairs=(('A', 'B'), ('C', 'D')))\n"
            "```\n"
        )
        with self.assertRaisesRegex(ValueError, "CA-R-1.md:.*disconnected"):
            select_model_claims([carrier("ANECHOIC_MODEL <+ Atom.Header", body=body)])

    def test_rejects_partial_dataclass_field_contract_before_generation(self):
        claim = ("from dataclasses import dataclass, field\n"
                 "from anechoic.formal_claims import declare_entity\n"
                 "@dataclass\nclass Example:\n"
                 "    id: int = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})\n"
                 "declare_entity(entity_name='Example', entity_class=Example)\n")
        def model(code):
            return carrier('ANECHOIC_MODEL <+ Example', body=f'## Claim\n### Formal Claim\n```python\n{code}```\n')
        self.assertEqual(select_model_claims([model(claim)]), (claim,))
        with self.assertRaisesRegex(ValueError, 'require occurrence and value cardinalities'):
            select_model_claims([model(claim.replace("'value_cardinality': 1", "'other': 1"))])

    def test_relation_endpoints_and_entity_relation_must_be_declared(self):
        def with_claim(subject, identifier, claim):
            return carrier(subject, identifier=identifier,
                           body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n")

        relation = ("from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='LINKS', "
                    "source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)}, "
                    "target_endpoint={'level': 'instances', 'entity_paths': ('Node',)})")
        entity = ("from anechoic.formal_claims import declare_entity\n"
                  "declare_entity(entity_name='Node', instance_relation_constraints="
                  "{'LINKS': {'target_entity_paths': ('Atom',)}})")
        atom = carrier()
        node = with_claim("ANECHOIC_MODEL <+ Node", "CA-R-2", entity)
        link = with_claim("ANECHOIC_MODEL <+ CFEL <+ Relation//LINKS", "CA-R-3", relation)
        self.assertEqual(len(select_model_claims([atom, node, link])), 3)
        with self.assertRaisesRegex(ValueError, "unknown Relation: LINKS"):
            select_model_claims([atom, node])
        with self.assertRaisesRegex(ValueError, "unknown Model address: Node"):
            select_model_claims([atom, link])
        unknown_entity = with_claim("ANECHOIC_MODEL <+ Node", "CA-R-5", entity.replace("LINKS", "MISSING"))
        with self.assertRaisesRegex(ValueError, "CA-R-3.md:.*unknown Model address: Atom"):
            select_model_claims([unknown_entity, link])
        mismatch = with_claim("ANECHOIC_MODEL <+ Relation//OTHER", "CA-R-4", relation)
        with self.assertRaisesRegex(ValueError, "Relation does not match its Main Subject"):
            select_model_claims([atom, node, mismatch])

    def test_derived_inverse_can_be_referenced_without_a_second_declaration(self):
        relation = ("from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='LINKS', inverse_alias='LINKED_BY', "
                    "source_endpoint={'level': 'instances'}, target_endpoint={'level': 'instances'})")
        entity = ("from anechoic.formal_claims import declare_entity\n"
                  "declare_entity(entity_name='Atom', instance_relation_constraints="
                  "{'LINKED_BY': {'target_entity_paths': ('Atom',)}})")
        def body(claim):
            return f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n"
        atom = carrier(body=body(entity))
        link = carrier("ANECHOIC_MODEL <+ Relation//LINKS", identifier="CA-R-2", body=body(relation))
        self.assertEqual(len(select_model_claims([atom, link])), 2)

    def test_relation_constraints_check_levels_inheritance_inverse_and_pairs(self):
        def model(subject, identifier, claim):
            body = f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n"
            return carrier("ANECHOIC_MODEL <+ " + subject, identifier=identifier, body=body)

        def entity(name, base="", constraints=""):
            imports = "from anechoic.model import Animal\n" if base else ""
            return ("from anechoic.formal_claims import declare_entity\n" + imports
                    + f"class {name}{base}:\n    pass\n"
                    + f"declare_entity(entity_name='{name}', entity_class={name}{constraints})")

        animal = model("Animal", "CA-R-10", entity("Animal"))
        cat = model("Cat", "CA-R-11", entity("Cat", "(Animal)",
                    ", instance_relation_constraints={'EATS': {'target_entity_paths': ('Food',)}}"))
        food = model("Food", "CA-R-12", entity("Food"))
        toy = model("Toy", "CA-R-13", entity("Toy"))
        relation = ("from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='EATS', inverse_alias='EATEN_BY', endpoint_pairs=("
                    "{'source_endpoint': {'level': 'instances', 'entity_paths': ('Animal',)}, "
                    "'target_endpoint': {'level': 'instances', 'entity_paths': ('Food',)}}, "
                    "{'source_endpoint': {'level': 'instances', 'entity_paths': ('Food',)}, "
                    "'target_endpoint': {'level': 'instances', 'entity_paths': ('Toy',)}}))")
        link = model("Relation//EATS", "CA-R-14", relation)
        select_model_claims([animal, cat, food, toy, link])
        inverse = model("Food", "CA-R-12", entity("Food", constraints=
                        ", instance_relation_constraints={'EATEN_BY': {'target_entity_paths': ('Cat',)}}"))
        select_model_claims([animal, cat, inverse, toy, link])
        wrong_pair = model("Cat", "CA-R-11", entity("Cat", "(Animal)",
                           ", instance_relation_constraints={'EATS': {'target_entity_paths': ('Toy',)}}"))
        with self.assertRaisesRegex(ValueError, "CA-R-11.md:.*incompatible"):
            select_model_claims([animal, wrong_pair, food, toy, link])
        wrong_level = model("Cat", "CA-R-11", entity("Cat", "(Animal)",
                            ", model_relation_constraints={'EATS': {}}"))
        with self.assertRaisesRegex(ValueError, "CA-R-11.md:.*incompatible"):
            select_model_claims([animal, wrong_level, food, toy, link])
        prohibition = model("Cat", "CA-R-11", entity("Cat", "(Animal)",
                            ", model_relation_constraints={'EATS': {'targets_per_source': 0}}"))
        select_model_claims([animal, prohibition, food, toy, link])

    def test_cfel_wrapped_entity_is_available_by_its_local_name(self):
        relation_entity = carrier("ANECHOIC_MODEL <+ CFEL <+ Relation", body=(
            "## Claim\n### Formal Claim\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Relation')\n```\n"))
        link = carrier("ANECHOIC_MODEL <+ CFEL <+ Relation//LINKS", identifier="CA-R-2", body=(
            "## Claim\n### Formal Claim\n```python\n"
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='LINKS', source_endpoint={'entity_paths': ('Relation',)}, "
            "target_endpoint={'entity_paths': ('Relation',)})\n```\n"))
        self.assertEqual(len(select_model_claims([relation_entity, link])), 2)

    def test_relation_registry_resolves_derived_names_after_assembly(self):
        def relation(name, **args):
            return (name + ".md", "ANECHOIC_MODEL <+ CFEL <+ Relation//" + name,
                    {"kind": "relation", "arguments": {"relation_name": name, **args}})
        base = relation("BASE", inverse_alias="REVERSE")
        derived = relation("DERIVED", derived_from="REVERSE")
        registry = _relation_registry([derived, base])
        self.assertEqual(set(registry), {"BASE", "REVERSE", "DERIVED"})
        self.assertTrue(registry["REVERSE"][1])
        with self.assertRaisesRegex(ValueError, "unknown derived_from Relation"):
            _relation_registry([relation("DERIVED", derived_from="MISSING")])
        with self.assertRaisesRegex(ValueError, "cannot derive from itself"):
            _relation_registry([relation("DERIVED", inverse_alias="ALIAS", derived_from="ALIAS")])
        with self.assertRaisesRegex(ValueError, "duplicate Relation name"):
            _relation_registry([base, relation("OTHER", inverse_alias="REVERSE")])
        def native(name, extra, identifier):
            claim = ("from anechoic.formal_claims import declare_relation\n"
                     f"declare_relation(relation_name='{name}', source_endpoint={{}}, "
                     f"target_endpoint={{}}{extra})")
            return carrier("ANECHOIC_MODEL <+ Relation//" + name, identifier=identifier,
                           body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n")
        first = native("DERIVED", ", derived_from='REVERSE'", "CA-R-20")
        second = native("BASE", ", inverse_alias='REVERSE'", "CA-R-21")
        self.assertEqual(len(select_model_claims([first, second])), 2)
        with self.assertRaisesRegex(ValueError, "unknown derived_from Relation"):
            select_model_claims([first])

    def test_qualified_class_property_short_path_resolves(self):
        root = "Atom/(.Header.Context.Role:=Operations)/Workflow"
        def declaration(subject, identifier, claim):
            return carrier("ANECHOIC_MODEL <+ " + subject, identifier=identifier,
                           body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n")
        workflow = declaration(root, "CA-R-30", "from anechoic.formal_claims import declare_entity\n"
                               "class Workflow:\n    pass\n"
                               "declare_entity(entity_name='Workflow', entity_class=Workflow)")
        content = declaration(root + ".Content", "CA-R-31", "from anechoic.formal_claims import declare_entity\n"
                              f"declare_entity(entity_name='Content', relation_name='IS_PROPERTY_OF', base_path='{root}')")
        relation = declaration("Relation//IS_PROPERTY_OF", "CA-R-32", "from anechoic.formal_claims import declare_relation\n"
                               "declare_relation(relation_name='IS_PROPERTY_OF', source_endpoint={}, target_endpoint={})")
        child = declaration(root + ".Content.Name", "CA-R-33", "from anechoic.formal_claims import declare_entity\n"
                            "declare_entity(entity_name='Name', relation_name='IS_PROPERTY_OF', base_path='Workflow.Content')")
        self.assertEqual(len(select_model_claims([workflow, content, relation, child])), 4)
        with self.assertRaisesRegex(ValueError, "unknown Model address: Workflow.Content"):
            select_model_claims([workflow, relation, child])
        def parsed(subject, args):
            return ("x", "ANECHOIC_MODEL <+ " + subject, {"kind": "entity", "arguments": args, "classes": ()})
        kind = {"entity_name": "Workflow", "entity_class": "Workflow"}
        rows = [parsed(root, kind), parsed(root + ".Content", {}),
                parsed("Other/Workflow", kind), parsed("Other/Workflow.Content", {})]
        self.assertNotIn("Workflow.Content", _class_property_aliases(rows))

    def test_inherited_property_resolves_through_class_hierarchy(self):
        def model(subject, identifier, claim):
            return carrier("ANECHOIC_MODEL <+ " + subject, identifier=identifier,
                           body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n")
        def cls(name, base=None):
            imports = f"from anechoic.model import {base}\n" if base else ""
            return ("from anechoic.formal_claims import declare_entity\n" + imports
                    + f"class {name}{f'({base})' if base else ''}:\n    pass\n"
                    + f"declare_entity(entity_name='{name}', entity_class={name})")
        atom = model("Atom", "CA-R-40", cls("Atom"))
        ops = model("Atom/(.Header.Context.Role:=Operations)", "CA-R-41", cls("Operations", "Atom"))
        flow = model("Atom/(.Header.Context.Role:=Operations)/Workflow", "CA-R-42", cls("Workflow", "Operations"))
        prop = model("Atom.Content", "CA-R-43", "from anechoic.formal_claims import declare_entity\n"
                     "declare_entity(entity_name='Content', relation_name='IS_PROPERTY_OF', base_path='Atom')")
        child = model("Workflow.Content.Claim", "CA-R-44", "from anechoic.formal_claims import declare_entity\n"
                      "declare_entity(entity_name='Claim', relation_name='IS_PROPERTY_OF', base_path='Workflow.Content')")
        rel = model("Relation//IS_PROPERTY_OF", "CA-R-45", "from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='IS_PROPERTY_OF', source_endpoint={}, target_endpoint={})")
        self.assertEqual(len(select_model_claims([atom, ops, flow, prop, child, rel])), 6)
        with self.assertRaisesRegex(ValueError, "unknown Model address: Workflow.Content"):
            select_model_claims([atom, ops, flow, child, rel])
        def row(subject, name=None, bases=()):
            args = {"entity_name": name, "entity_class": name} if name else {}
            classes = ({"name": name, "bases": bases},) if name else ()
            return ("x", "ANECHOIC_MODEL <+ " + subject,
                    {"kind": "entity", "arguments": args, "classes": classes})
        ambiguous = [row("A", "A"), row("B", "B"), row("C", "C", ("A", "B")),
                     row("A.Content"), row("B.Content")]
        self.assertNotIn("C.Content", _class_property_aliases(ambiguous))
        ambiguous.append(row("C.Content"))
        self.assertNotIn("C.Content", _class_property_aliases(ambiguous))  # canonical address wins

    def test_qualified_endpoint_classes_are_checked(self):
        def model(subject, identifier, claim):
            return carrier("ANECHOIC_MODEL <+ " + subject, identifier=identifier,
                           body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n")
        plan_path = "Atom/(.Header.Context.Role:=Plan)"
        step_path = "Atom/(.Header.Context.Role:=Operations)/Step"
        plan = model(plan_path, "CA-R-50", "from anechoic.formal_claims import declare_entity\n"
                     "class Plan:\n    pass\n"
                     "declare_entity(entity_name='Plan', entity_class=Plan)")
        step = model(step_path, "CA-R-51", "from anechoic.formal_claims import declare_entity\n"
                     "class Step:\n    pass\n"
                     "declare_entity(entity_name='Step', entity_class=Step, "
                     "instance_relation_constraints={'LINKS': {'target_entity_paths': ('Atom/(.Header.Context.Role := Plan)',)}})")
        rel = model("Relation//LINKS", "CA-R-52", "from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='LINKS', "
                    "source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Plan)',)}, "
                    "target_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Plan)',)})")
        with self.assertRaisesRegex(ValueError, "CA-R-51.md:.*incompatible"):
            select_model_claims([step, plan, rel])
        inverse = model("Relation//LINKS", "CA-R-52", "from anechoic.formal_claims import declare_relation\n"
                        "declare_relation(relation_name='LINKS', "
                        "source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Operations)/Step',)}, "
                        "target_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Plan)',)})")
        self.assertEqual(len(select_model_claims([step, plan, inverse])), 3)

    def test_unparseable_subject_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "invalid Main Subject"):
            select_model_claims([carrier("ANECHOIC_MODEL <+")])

    def test_empty_model_is_an_error(self):
        structure = carrier("ANECHOIC_STRUCTURE <+ Scope Unit//ENGINE", body="")
        with self.assertRaisesRegex(ValueError, "No Current ANECHOIC_MODEL Declarations"):
            select_model_claims([structure])


if __name__ == "__main__":
    unittest.main()
