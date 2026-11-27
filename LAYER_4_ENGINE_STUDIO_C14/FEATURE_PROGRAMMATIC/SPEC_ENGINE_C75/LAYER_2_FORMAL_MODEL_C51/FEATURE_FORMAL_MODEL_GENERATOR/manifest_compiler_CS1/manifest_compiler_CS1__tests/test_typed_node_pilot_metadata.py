from importlib import import_module
import unittest


parse_typed_manifest_node = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
).parse_typed_manifest_node
_collect_node_metadata = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75."
    "LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR."
    "manifest_compiler_CS1.active_model_sources"
)._collect_node_metadata


def test_node_parts_and_alternatives_are_static_and_checked():

    records = [
        _part_record("Root", "Root"),
        _part_record("Child", "Root//Child"),
        _part_record("Other", "Other"),
    ]
    source = (
        "from anechoic.model import Child, Other\nclass Root:\n"
        "    node.parts = {'CH': Child, '=>OT': Other}\n"
        "    node.alternatives = (('CH',), ('=>OT',))\n"
    )
    addresses = {"Root": "Root", "Child": "Root//Child", "Other": "Other"}
    locations = {"MODEL//ANECHOIC <+ Root//Child": ("Root", "/", "Child")}
    output = {}
    _collect_node_metadata(
        records,
        [("source", "MODEL//ANECHOIC <+ Root", source, "manifest_node")],
        addresses,
        locations,
        output,
    )
    assert output == {
        "node_parts": {
            "MODEL//ANECHOIC <+ Root": [
                ["CH", "Root//Child"],
                ["=>OT", "Other"],
            ]
        },
        "node_alternatives": {"MODEL//ANECHOIC <+ Root": [["CH"], ["=>OT"]]},
        "node_aliases": {},
    }
    _check_invalid_parts(
        source,
        records,
        addresses,
        locations,
        _collect_node_metadata,
        parse_typed_manifest_node,
    )


def test_node_aliases_are_static_and_unique_among_admitted_siblings():

    def record(name):
        return (
            "source",
            "MODEL//ANECHOIC <+ Root//" + name,
            f"from anechoic.formal_claims import declare_entity\n"
            f"class {name}:\n    pass\n"
            f"declare_entity(entity_name={name!r}, "
            f"entity_class={name}, entity_kind='Primary')\n",
        )

    records = [record("First"), record("Second")]
    addresses = {name: "Root//" + name for name in ("First", "Second")}
    locations = {
        subject: ("Root", "//", subject.rsplit("/", 1)[-1])
        for _, subject, _ in records
    }

    def source(name, aliases):
        return f"class {name}:\n    node.aliases = {aliases}\n"

    first = source("First", "('Alternate', 'Another')")
    typed = [("first", records[0][1], first, "manifest_node")]
    output = {}
    _collect_node_metadata(records, typed, addresses, locations, output)
    assert output["node_aliases"] == {records[0][1]: ["Alternate", "Another"]}
    _check_invalid_aliases(
        source,
        records,
        addresses,
        locations,
        typed,
        _collect_node_metadata,
        parse_typed_manifest_node,
    )


def _check_invalid_parts(
    source,
    records,
    addresses,
    locations,
    _collect_node_metadata,
    parse_typed_manifest_node,
):
    for invalid in (
        source.replace("'=>OT': Other", "'OT': Other"),
        source.replace("('=>OT',)", "('missing',)"),
        source.replace("'=>OT': Other", "'=>OT': Child, '=>OT': Other"),
        source.replace("'=>OT': Other", "'CH2': Child, '=>OT': Other"),
        source.replace("'=>OT': Other", "'=>OT': Missing"),
        source.replace("('=>OT',)", "('CH',)"),
    ):
        with unittest.TestCase().assertRaises(ValueError):
            _collect_node_metadata(
                records,
                [
                    (
                        "source",
                        "MODEL//ANECHOIC <+ Root",
                        invalid,
                        "manifest_node",
                    )
                ],
                addresses,
                locations,
                {},
            )
    with unittest.TestCase().assertRaises(ValueError):
        parse_typed_manifest_node(
            source.replace("'=>OT': Other", "'=>OT': Missing")
        )


def _check_invalid_aliases(
    source,
    records,
    addresses,
    locations,
    typed,
    _collect_node_metadata,
    parse_typed_manifest_node,
):
    for invalid in (
        "()",
        "('',)",
        "(' A',)",
        "('A/B',)",
        "('=>A',)",
        "('A', 'A')",
        "(A,)",
    ):
        with unittest.TestCase().assertRaises(ValueError):
            parse_typed_manifest_node(source("First", invalid))
    _check_alias_collisions(
        source, records, addresses, locations, typed, _collect_node_metadata
    )


def _part_record(name, path):
    return (
        "source",
        "MODEL//ANECHOIC <+ " + path,
        f"from anechoic.formal_claims import declare_entity\n"
        f"class {name}:\n    pass\n"
        f"declare_entity(entity_name={path.rsplit('/', 1)[-1]!r}, "
        f"entity_class={name}, entity_kind='Primary')\n",
    )


def _check_alias_collisions(
    source, records, addresses, locations, typed, _collect_node_metadata
):
    for name in ("First", "Second"):
        with unittest.TestCase().assertRaises(ValueError):
            _collect_node_metadata(
                records,
                [
                    (
                        "first",
                        records[0][1],
                        source("First", repr((name,))),
                        "manifest_node",
                    )
                ],
                addresses,
                locations,
                {},
            )
    with unittest.TestCase().assertRaises(ValueError):
        _collect_node_metadata(
            records,
            typed
            + [
                (
                    "second",
                    records[1][1],
                    source("Second", "('Alternate',)"),
                    "manifest_node",
                )
            ],
            addresses,
            locations,
            {},
        )
    with unittest.TestCase().assertRaises(ValueError):
        _collect_node_metadata(records, typed, addresses, {}, {})


def load_tests(loader, tests, pattern):
    for test in (
        test_node_parts_and_alternatives_are_static_and_checked,
        test_node_aliases_are_static_and_unique_among_admitted_siblings,
    ):
        tests.addTest(unittest.FunctionTestCase(test))
    return tests
