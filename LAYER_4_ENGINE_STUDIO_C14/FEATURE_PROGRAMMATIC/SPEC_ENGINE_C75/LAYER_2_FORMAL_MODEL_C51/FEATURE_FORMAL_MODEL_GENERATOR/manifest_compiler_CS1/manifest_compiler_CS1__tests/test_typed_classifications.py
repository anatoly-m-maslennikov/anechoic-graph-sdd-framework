"""Static typed Node classification domains and membership."""

import unittest

from ......FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_native_model_claim,
)
from ..typed_node_lowering import lower_typed_node
from ..typed_property_relation_lowering import lower_typed_fields
from ...model_declaration_sources import _check_node_axes


class TypedClassificationsTests(unittest.TestCase):
    def test_axis_and_node_membership(self):
        axis = (
            "from anechoic.model import Property, Axis\n"
            "class ArtifactKind(Property):\n"
            "    name = 'Artifact Kind'\n"
            "    bearer = Axis\n"
            "    property.axis = True\n"
            "    allowed_values = ('Artifact', 'Ephemeral')\n"
        )
        scope = "MODEL//ANECHOIC <+ Graph/Axis >| Artifact Kind"
        claim = lower_typed_fields(
            "manifest_property", axis, scope, {"Axis": "Graph/Axis"}
        )
        domain = parse_native_model_claim(claim)
        self.assertEqual(
            domain["arguments"]["allowed_axis_values"],
            {"Artifact Kind": ("Artifact", "Ephemeral")},
        )
        text = "class Artifact:\n    axes = {'Artifact Kind': 'Artifact'}\n"
        subject, lowered = lower_typed_node(
            text, [], "MODEL//ANECHOIC <+ Graph/Node//Artifact"
        )[0]
        node = parse_native_model_claim(lowered)
        self.assertEqual(
            node["arguments"]["axes"], {"Artifact Kind": "Artifact"}
        )
        rows = [("axis", scope, domain), ("node", subject, node)]
        _check_node_axes(rows, {"node"})
        for value in ("Unknown",):
            bad = {
                **node,
                "arguments": {
                    **node["arguments"],
                    "axes": {"Artifact Kind": value},
                },
            }
            with self.assertRaisesRegex(ValueError, "unadmitted Entity axis"):
                _check_node_axes([rows[0], ("node", subject, bad)], {"node"})
        with self.assertRaisesRegex(ValueError, "ambiguous or invalid"):
            _check_node_axes([rows[0], rows[0], rows[1]], {"node"})
        with self.assertRaisesRegex(ValueError, "unadmitted Entity axis"):
            _check_node_axes([rows[1]], {"node"})
        _check_node_axes([rows[1]], set())
        self._assert_invalid_values(axis, scope, text, subject)

    def _assert_invalid_values(self, axis, scope, text, subject):
        for replacement in (
            "('Artifact', 'Artifact')",
            "('Artifact', compute())",
            "()",
        ):
            with self.assertRaises(ValueError):
                lower_typed_fields(
                    "manifest_property",
                    axis.replace("('Artifact', 'Ephemeral')", replacement),
                    scope,
                    {"Axis": "Graph/Axis"},
                )
        for mapping in (
            "{'Artifact Kind': 'Artifact', 'Artifact Kind': 'Ephemeral'}",
            "{'Artifact Kind': compute()}",
        ):
            with self.assertRaises(ValueError):
                lower_typed_node(
                    text.replace("{'Artifact Kind': 'Artifact'}", mapping),
                    [],
                    subject,
                )
