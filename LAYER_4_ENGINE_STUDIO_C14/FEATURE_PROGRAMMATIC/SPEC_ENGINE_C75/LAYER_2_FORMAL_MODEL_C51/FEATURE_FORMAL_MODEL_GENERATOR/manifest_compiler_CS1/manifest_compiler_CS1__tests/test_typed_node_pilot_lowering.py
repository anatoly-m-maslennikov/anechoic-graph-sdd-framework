from importlib import import_module
import unittest

parse_native_model_claim = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
).parse_native_model_claim
lower_typed_node = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
    "LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR."
    "manifest_compiler_CS1.typed_node_lowering"
).lower_typed_node


def test_ssot_carrier_fixed_class_and_validation():
    def record(name, base, path):
        imports = f"from anechoic.model import {base}\n" if base else ""
        signature = f"({base})" if base else ""
        return (
            "source",
            "MODEL//ANECHOIC <+ " + path,
            f"from anechoic.formal_claims import declare_entity\n"
            f"{imports}class {name}{signature}:\n    pass\n"
            f"declare_entity(entity_name={name!r}, "
            f"entity_class={name})\n",
        )

    records = [
        record("Node", "", "Node"),
        record("Carrier", "", "Carrier"),
        record("Markdown", "Carrier", "Carrier//Markdown"),
    ]
    prefix = (
        "from anechoic.formal_claims import value\n"
        "from anechoic.model import Node, Carrier, Markdown\n"
        "class Example(Node):\n    node.ssot_carrier = value("
    )
    for name, path in [
        ("Carrier", "Carrier"),
        ("Markdown", "Carrier//Markdown"),
    ]:
        claim = lower_typed_node(prefix + f"fixed={name})\n", records)[0][1]
        assert (
            parse_native_model_claim(claim)["arguments"]["ssot_carrier_path"]
            == path
        )
    for expression in ("default=Markdown", "fixed=Node", 'fixed="Markdown"'):
        with unittest.TestCase().assertRaisesRegex(
            ValueError, "ssot_carrier requires"
        ):
            lower_typed_node(prefix + expression + ")\n", records)
    with unittest.TestCase().assertRaisesRegex(
        ValueError, "unknown ssot_carrier"
    ):
        lower_typed_node(prefix + "fixed=Markdown)\n", records[:2])
    _check_creation_enabled(lower_typed_node, records)


def test_ticket_subtype_template_uses_inherited_property():
    records = _ticket_records()
    before = records.copy()
    for name, value in (("Task", "task"), ("WorkReport", "work_report")):
        text = (
            "from anechoic.formal_claims import value\n"
            "from anechoic.model import TicketAtom\n"
            f"class {name}(TicketAtom):\n"
            f"    node.template = value(fixed={value!r})\n"
        )
        lowered = lower_typed_node(text, records)
        args = parse_native_model_claim(lowered[1][1])["arguments"]
        assert args["allowed_values"] == (value,)
        assert args["applies_to_entity_classes"] == (f"Atom//Ticket//{name}",)
        assert args["base_path"] == "Atom.Header.Context"
    assert records == before
    assert (
        parse_native_model_claim(records[-1][2])["arguments"][
            "fallback_property_name"
        ]
        == "Form"
    )


def test_ready_nodes_reuse_records_across_dependency_retries(monkeypatch):
    nodes = import_module(
        "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
        "LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR."
        "manifest_compiler_CS1.active_source_nodes"
    )
    record = nodes._model_record
    parsed = []

    def count_record(subject, claim):
        parsed.append(subject)
        return record(subject, claim)

    monkeypatch.setattr(nodes, "_model_record", count_record)
    records = [("seed", *lower_typed_node("node(Node)", [])[0])]
    pending = [
        ("leaf", None, "node(Leaf, Branch)", "manifest_node"),
        ("branch", None, "node(Branch, Node)", "manifest_node"),
    ]

    def append_claim(source, subject, claim):
        records.append((source, subject, claim))

    nodes._lower_ready_nodes(pending, records, append_claim, require_all=True)
    assert pending == []
    assert [source for source, _, _ in records] == ["seed", "branch", "leaf"]
    assert parsed == [subject for _, subject, _ in records[:2]]


def test_node_marker_is_static_and_lowers_to_a_class():
    parse_typed_manifest_node = import_module(
        "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
    ).parse_typed_manifest_node
    InputError = import_module(
        "FEATURE_PROGRAMMATIC.FEATURE_TOOLS."
        "ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared"
    ).InputError
    _validate_c9_typed_manifest = import_module(
        "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_guards"
    )._validate_c9_typed_manifest

    record = (
        "source",
        "MODEL//ANECHOIC <+ Node",
        (
            "from anechoic.formal_claims import declare_entity\n"
            "class Node:\n    pass\n"
            "declare_entity(entity_name='Node', entity_class=Node)\n"
        ),
    )
    assert parse_typed_manifest_node("node(Root)")["bases"] == ()
    claim = lower_typed_node("node(Example, Node)", [record])[0][1]
    assert (
        "from anechoic.model import Node\nclass Example(Node):\n    pass"
        in claim
    )
    header = _node_header()
    body = "## Formal Manifest\n\n```python anechoic-edsl\n{}\n```\n"
    _validate_c9_typed_manifest(header, body.format("node(Example, Node)"))
    _check_node_marker_rejections(
        parse_typed_manifest_node,
        _validate_c9_typed_manifest,
        InputError,
        header,
        body,
    )


def _check_creation_enabled(lower_typed_node, records):
    eligibility = (
        "from anechoic.formal_claims import value\n"
        "from anechoic.model import Node\n"
        "class Example(Node):\n    node.creation_enabled = "
    )
    for expression in ("value(default=False)", "value(fixed='false')"):
        with unittest.TestCase().assertRaisesRegex(
            ValueError, "fixed boolean"
        ):
            lower_typed_node(eligibility + expression + "\n", records)


def _check_node_marker_rejections(
    parse_typed_manifest_node,
    _validate_c9_typed_manifest,
    InputError,
    header,
    body,
):
    for invalid in (
        "node()",
        'node("Example")',
        "node(Example, Node, Node)",
        "node(Example, Property)",
        "node(Example, base=Node)",
        "node(Example)\nprint(1)",
        "node(Example, dangerous())",
    ):
        with unittest.TestCase().assertRaises(ValueError):
            parse_typed_manifest_node(invalid)
        with unittest.TestCase().assertRaises(InputError):
            _validate_c9_typed_manifest(header, body.format(invalid))
    for template in ("manifest_property", "manifest_relation"):
        with unittest.TestCase().assertRaises(InputError):
            _validate_c9_typed_manifest(
                {
                    **header,
                    "context": {"lens": "DOM/CONT", "template": template},
                },
                body.format("node(Example, Node)"),
            )


def _ticket_records():
    return [
        (
            "atom",
            "MODEL//ANECHOIC <+ Atom",
            (
                "from anechoic.formal_claims import declare_entity\nclass "
                "Atom:\n    pass\ndeclare_entity(entity_name='Atom', "
                "entity_class=Atom)\n"
            ),
        ),
        (
            "ticket",
            "MODEL//ANECHOIC <+ Atom//Ticket",
            (
                "from anechoic.formal_claims import declare_entity\nfrom "
                "anechoic.model import Atom\nclass TicketAtom(Atom):\n    "
                "pass\ndeclare_entity(entity_name='Ticket', "
                "entity_class=TicketAtom)\n"
            ),
        ),
        (
            "property",
            "MODEL//ANECHOIC <+ Atom.Header.Context.Template",
            (
                "from anechoic.formal_claims import declare_entity\n"
                "declare_entity(entity_name='Template', "
                "entity_kind='Property', relation_name='IS_PROPERTY_OF', "
                "base_path='Atom.Header.Context', value_format=str, "
                "field_options={'default': None, 'kw_only': True})\n"
            ),
        ),
        (
            "fallback",
            "MODEL//ANECHOIC <+ Atom.Header.Context.Template fallback",
            (
                "from anechoic.formal_claims import declare_entity\n"
                "declare_entity(entity_name='Template', "
                "entity_kind='Property', relation_name='IS_PROPERTY_OF', "
                "base_path='Atom.Header.Context', value_format=str, "
                "applies_to_entity_classes=('Atom//Ticket',), "
                "fallback_property_name='Form')\n"
            ),
        ),
    ]


def _node_header():
    header = {
        "atom_family": "SPEC",
        "atom_id": "AN-S-100",
        "container": {"component": "C9"},
        "tier": 2,
        "state": {
            "status": "draft",
            "version": 1,
            "updated_at": "2026-11-24T00:00:00Z",
        },
        "context": {"lens": "DOM/CONT", "template": "manifest_node"},
        "concern": {
            "subject": "Example",
            "path": "Model/Graph/Node",
            "relation": "is_narrower_than",
        },
    }
    return header


def load_tests(loader, tests, pattern):
    for test in (
        test_ssot_carrier_fixed_class_and_validation,
        test_ticket_subtype_template_uses_inherited_property,
        test_node_marker_is_static_and_lowers_to_a_class,
    ):
        tests.addTest(unittest.FunctionTestCase(test))
    return tests
