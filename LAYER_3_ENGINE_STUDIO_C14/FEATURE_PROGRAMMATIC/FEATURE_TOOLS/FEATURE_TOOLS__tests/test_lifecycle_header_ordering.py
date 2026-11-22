from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carrier import render_carrier  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.header_ordering import load_header_ordering, validate_header_order  # noqa: E402


class IdentityCodec:
    def encode(self, field, value):
        return value


RULES = [
    {"bearer": "Atom.Header", "roles": [], "pairs": [["Identity", "Context"], ["Context", "Relations"], ["Relations", "State"]]},
    {"bearer": "Atom.Header.Context", "roles": [], "pairs": [["Container", "Role"], ["Role", "Form"], ["Form", "Label"], ["Label", "Topics"], ["Topics", "Tier"]]},
]


class HeaderOrderingTests(unittest.TestCase):
    def test_written_carrier_skips_absent_label_and_orders_siblings(self):
        schema = SimpleNamespace(role_form=IdentityCodec(), header_ordering=load_header_ordering(RULES))
        model = SimpleNamespace(candidate_schema=schema)
        for label in (None, "Decision"):
            with self.subTest(label=label):
                fields = {"tier": 0, "topics": {"main_subject": "X"}, "form": "decision",
                          "role": "method", "container": {"scope_unit": "CA-SU-1"},
                          "atom_id": "CA-M-1", "status": "active"}
                if label:
                    fields["label"] = label
                raw = render_carrier(None, fields, body="## Summary\n\nText\n", model=model)
                header = yaml.safe_load(raw.decode().split("---", 2)[1])
                self.assertLess(list(header).index("identity"), list(header).index("context"))
                keys = list(header["context"])
                self.assertLess(keys.index("form"), keys.index("topics"))
                if label:
                    self.assertLess(keys.index("form"), keys.index("label"))
                    self.assertLess(keys.index("label"), keys.index("topics"))
                validate_header_order(header, schema)

    def test_flat_legacy_carrier_does_not_acquire_groups(self):
        schema = SimpleNamespace(role_form=IdentityCodec(), header_ordering=RULES)
        raw = b"---\natom_id: CA-M-1\nrole: method\nform: decision\nstatus: active\n---\n## Summary\n\nText\n"
        written = render_carrier(raw, {"status": "done"}, model=SimpleNamespace(candidate_schema=schema))
        header = yaml.safe_load(written.decode().split("---", 2)[1])
        self.assertNotIn("identity", header)
        self.assertNotIn("context", header)
        self.assertEqual(header["status"], "done")


if __name__ == "__main__":
    unittest.main()
