from pathlib import Path
import sys
from unittest.mock import NonCallableMock
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (  # noqa: E402
    render_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (  # noqa: E402
    load_header_ordering,
    validate_header_order,
)


class IdentityCodec:
    def encode(self, field, value):
        return value


RULES = [
    {
        "bearer": "Atom.Header",
        "roles": [],
        "pairs": [
            ["Identity", "Context"],
            ["Context", "Relations"],
            ["Relations", "State"],
        ],
    },
    {
        "bearer": "Atom.Header.Context",
        "roles": [],
        "pairs": [
            ["Container", "Role"],
            ["Role", "Form"],
            ["Form", "Label"],
            ["Label", "Topics"],
            ["Topics", "Tier"],
        ],
    },
]


class HeaderOrderingTests(unittest.TestCase):
    def test_written_carrier_skips_absent_label_and_orders_siblings(self):
        schema = NonCallableMock(
            spec_set=["role_form", "header_ordering"],
            role_form=IdentityCodec(),
            header_ordering=load_header_ordering(RULES),
        )
        model = NonCallableMock(
            spec_set=["candidate_schema"], candidate_schema=schema
        )
        for label in (None, "Decision"):
            with self.subTest(label=label):
                fields = {
                    "tier": 0,
                    "topics": {"main_subject": "X"},
                    "form": "decision",
                    "role": "method",
                    "container": {"scope_unit": "CA-SU-1"},
                    "atom_id": "CA-M-1",
                    "status": "active",
                }
                if label:
                    fields["label"] = label
                raw = render_carrier(
                    None, fields, body="## Summary\n\nText\n", model=model
                )
                header = yaml.safe_load(raw.decode().split("---", 2)[1])
                self.assertLess(
                    list(header).index("identity"),
                    list(header).index("context"),
                )
                keys = list(header["context"])
                self.assertLess(keys.index("form"), keys.index("topics"))
                if label:
                    self.assertLess(keys.index("form"), keys.index("label"))
                    self.assertLess(keys.index("label"), keys.index("topics"))
                validate_header_order(header, schema)

    def test_flat_legacy_carrier_does_not_acquire_groups(self):
        schema = NonCallableMock(
            spec_set=["role_form", "header_ordering"],
            role_form=IdentityCodec(),
            header_ordering=RULES,
        )
        raw = b"---\natom_id: CA-M-1\nrole: method\nform: decision\nstatus: active\n---\n## Summary\n\nText\n"
        written = render_carrier(
            raw,
            {"status": "done"},
            model=NonCallableMock(
                spec_set=["candidate_schema"], candidate_schema=schema
            ),
        )
        header = yaml.safe_load(written.decode().split("---", 2)[1])
        self.assertNotIn("identity", header)
        self.assertNotIn("context", header)
        self.assertEqual(header["status"], "done")


if __name__ == "__main__":
    unittest.main()
