from __future__ import annotations

from pathlib import Path
import hashlib
import sys
import unittest


TOOL = Path(__file__).resolve().parents[1]
TOOLS = TOOL.parent
sys.path[:0] = [str(TOOLS), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import get_profile  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import compose_declaration_catalog  # noqa: E402

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.declaration_source_fixtures import graph_rule_carrier, refresh_raw, relation_carrier, support_carriers


class GraphRuleSourceTests(unittest.TestCase):
    def test_current_support_sources_admit_valid_rule_and_input_order_is_irrelevant(self):
        supports = support_carriers()
        carriers = [*supports, graph_rule_carrier()]
        catalog = compose_declaration_catalog(carriers)
        reversed_catalog = compose_declaration_catalog(list(reversed(carriers)))

        self.assertEqual(catalog, reversed_catalog)
        self.assertEqual(len(catalog["graph_rules"]), 1)
        rule = catalog["graph_rules"][0]
        self.assertEqual(rule["source"]["atom_id"], "CA-R-901021")
        self.assertEqual(rule["subject"], "Entity/Node/Continuant/Atom.Relations")
        self.assertTrue(rule["yaml_block"].startswith("```yaml\n"))
        self.assertEqual(catalog["unresolved"], [])

    def test_actual_support_manifest_admits_current_approved_evaluation(self):
        pin, = (pin for pin in get_profile("approved").grammar_pins if pin.atom_id == "CA-E-833")
        source_path = Path(pin.path)
        self.assertEqual(".anechoic_anechoic", source_path.parts[0])
        raw = (Path(__file__).parent / "assets" / source_path.name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual("bcd3e7d0cf8c35e220c55ca4f52362547de5851aab8ac97c03d67592eab277f1", digest)
        supports = support_carriers()
        evaluation = next(row for row in supports if row["source"]["atom_id"] == pin.atom_id)
        evaluation["source"].update(version=3, path=pin.path, sha256=digest)
        evaluation["metadata"]["version"] = 3
        evaluation["raw"] = raw
        catalog = compose_declaration_catalog([*supports, graph_rule_carrier()])
        rule, = catalog["graph_rules"]
        self.assertEqual([row["source"] for row in supports], rule["authority"])
        self.assertEqual(catalog["unresolved"], [])

    def test_cardinality_rule_catalog_preserves_selection_yaml_and_source_evidence(self):
        supports = support_carriers()
        carrier = graph_rule_carrier("CA-R-901061", yaml_type="cardinality")
        carrier["body"] = carrier["body"].replace("\n", "\r\n")
        refresh_raw(carrier)
        body = carrier["raw_body"]
        block_start = body.index("```yaml")
        block_end = body.index("```", block_start + len("```yaml")) + 3
        expected_block = body[block_start : block_end + len("\r\n")]

        catalog = compose_declaration_catalog([*supports, carrier])

        self.assertEqual(len(catalog["graph_rules"]), 1)
        self.assertEqual(catalog["unresolved"], [])
        rule = catalog["graph_rules"][0]
        self.assertEqual(
            {"source", "subject", "summary", "yaml_block", "evidence", "authority"},
            set(rule),
        )
        self.assertEqual(carrier["source"], rule["source"])
        self.assertEqual("Entity/Node/Continuant/Atom.Relations", rule["subject"])
        self.assertEqual("Cardinality fixture.", rule["summary"])
        self.assertEqual(expected_block, rule["yaml_block"])
        self.assertEqual(body, rule["evidence"])
        self.assertIn("Selection//Dependent Entity Occurrences", rule["yaml_block"])
        self.assertIn("minimum: 0\r\n", rule["yaml_block"])
        self.assertIn("maximum: null\r\n", rule["yaml_block"])

    def test_rule_admission_preserves_crlf_and_requires_source_bound_raw_body(self):
        supports = support_carriers()
        crlf = graph_rule_carrier("CA-R-901041")
        crlf["raw_body"] = crlf["raw_body"].replace("\n", "\r\n")
        prefix = crlf["raw"].split(b"# Summary", 1)[0]
        crlf["raw"] = prefix + crlf["raw_body"].encode("utf-8")
        crlf["source"]["sha256"] = hashlib.sha256(crlf["raw"]).hexdigest()
        missing_body = graph_rule_carrier("CA-R-901042")
        del missing_body["raw_body"]
        mismatched_body = graph_rule_carrier("CA-R-901043")
        mismatched_body["raw_body"] = mismatched_body["raw_body"].replace("Permit", "Alter")
        carriers = [*supports, crlf, missing_body, mismatched_body]

        catalog = compose_declaration_catalog(carriers)

        self.assertEqual(len(catalog["graph_rules"]), 1)
        self.assertIn("\r\n", catalog["graph_rules"][0]["yaml_block"])
        block_start = crlf["raw_body"].index("```yaml")
        block_end = crlf["raw_body"].index("```", block_start + len("```yaml")) + 3
        expected_block = crlf["raw_body"][block_start : block_end + len("\r\n")]
        self.assertEqual(catalog["graph_rules"][0]["yaml_block"], expected_block)
        self.assertEqual(len(catalog["unresolved"]), 2)
        self.assertTrue(all("source" in row["reason"].lower() or "raw_body" in row["reason"] for row in catalog["unresolved"]))

    def test_optional_rule_docs_do_not_change_catalog_summary_or_operative_yaml(self):
        supports = support_carriers()
        carrier = graph_rule_carrier("CA-R-901044")
        carrier["body"] = carrier["body"].replace("\n", "\r\n") + (
            "## Details\r\n\r\n"
            "Illustrative only; graph_rule_type: blacklist is not operative here.\r\n\r\n"
            "```yaml\r\n"
            "graph_rule_type: blacklist\r\n"
            "condition: {example: true}\r\n"
            "```\r\n\r\n"
            "## Semantics\r\n\r\n"
            "A readable explanation of the admitted whitelist.\r\n"
        )
        refresh_raw(carrier)
        body = carrier["raw_body"]
        block_start = body.index("```yaml")
        block_end = body.index("```", block_start + len("```yaml")) + 3
        expected_block = body[block_start : block_end + len("\r\n")]

        catalog = compose_declaration_catalog([*supports, carrier])

        self.assertEqual(len(catalog["graph_rules"]), 1)
        rule = catalog["graph_rules"][0]
        self.assertEqual(rule["summary"], "Permit evaluation links.")
        self.assertEqual(rule["yaml_block"], expected_block)
        self.assertIn("\r\n", rule["yaml_block"])
        self.assertEqual(rule["evidence"], body)
        self.assertEqual(catalog["unresolved"], [])

    def test_malformed_and_unsupported_rules_remain_unresolved_examples_are_ignored(self):
        supports = support_carriers()
        malformed = graph_rule_carrier("CA-R-901031")
        malformed["body"] = "# Summary\n\nBroken payload.\n\n```yaml\nnot: [valid\n```\n"
        refresh_raw(malformed)
        unsupported = graph_rule_carrier("CA-R-901032", yaml_type="blacklist")
        example = {
            **relation_carrier("CA-D-901033", "Entity/Node/Continuant/Atom", "Entities Graph"),
            "body": "## Scope\n\nD637 Graph Rule example only; not a declaration.\n",
        }
        refresh_raw(example)
        carriers = [*supports, malformed, unsupported, example]

        catalog = compose_declaration_catalog(carriers)

        self.assertEqual(catalog["graph_rules"], [])
        self.assertEqual(len(catalog["unresolved"]), 2)
        self.assertTrue(any("structural validation" in row["reason"] for row in catalog["unresolved"]))

    def test_rule_does_not_drop_invalid_entries_from_governs_list(self):
        supports = support_carriers()
        malformed_subjects = graph_rule_carrier("CA-R-901051")
        malformed_subjects["subjects"]["governs"] = [
            "Entity/Node/Continuant/Atom.Relations",
            7,
        ]
        catalog = compose_declaration_catalog([*supports, malformed_subjects])

        self.assertEqual(catalog["graph_rules"], [])
        self.assertEqual(len(catalog["unresolved"]), 1)
        self.assertIn("exactly one nonempty valid governed Subject", catalog["unresolved"][0]["reason"])

    def test_graph_rule_keeps_exact_yaml_but_is_not_admitted_without_support_sources(self):
        yaml_block = (
            "```yaml\ngraph_rule_type: whitelist\napplies_to:\n"
            "  relation_type: evaluation_for\ncondition:\n"
            '  source: ["Entity/Node/Continuant/Atom/Content Role: Evaluation"]\n'
            '  target: ["Entity/Node/Continuant/Atom/Content Role: Requirement"]\n```'
        )
        body = "# Summary\n\nPermit evaluation links.\n\n" + yaml_block + "\n"
        raw = b"---\natom_id: CA-R-901021\nversion: 3\ncontent_role: Requirement\ntype: Graph Rule\nstatus: Active\n---\n" + body.encode("utf-8")
        carrier = {
            "source": {
                "atom_id": "CA-R-901021",
                "version": 3,
                "path": "CA-R-901021.md",
                "sha256": hashlib.sha256(raw).hexdigest(),
            },
            "metadata": {
                "atom_id": "CA-R-901021",
                "version": 3,
                "content_role": "Requirement",
                "type": "Graph Rule",
                "status": "Active",
            },
            "subjects": {"governs": "Entity/Node/Continuant/Atom.Relations"},
            "body": body,
            "raw_body": body,
            "raw": raw,
        }

        catalog = compose_declaration_catalog([carrier])

        self.assertEqual(catalog["graph_rules"], [])
        self.assertEqual(len(catalog["unresolved"]), 1)
        unresolved = catalog["unresolved"][0]
        self.assertIn("source-bound Graph Rule governing authority", unresolved["reason"])
        self.assertEqual(unresolved["yaml_block"], yaml_block + "\n")


if __name__ == "__main__":
    unittest.main()
