from __future__ import annotations

from pathlib import Path
import hashlib
import sys
import unittest


TOOL = Path(__file__).resolve().parents[1]
TOOLS = TOOL.parent
sys.path[:0] = [str(TOOLS), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.declaration_relations import resolve_relation_authorities  # noqa: E402
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.declaration_sources import compose_declaration_catalog  # noqa: E402


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__tests.declaration_source_fixtures import refresh_raw, relation_carrier


def _relation_identity_carriers() -> list[dict]:
    carriers = [
        relation_carrier(
            "CA-R-901001", "Entity/Relation/Type: IS_NARROWER_THAN", "Entities Graph"
        ),
        relation_carrier(
            "CA-R-901002", "Entity/Relation/Type: IS_NARROWER_THAN", "Terms Graph"
        ),
        relation_carrier("CA-R-901003", "IS_BORNE_BY", "Entities Graph", version=2),
        relation_carrier("CA-R-901004", "BORNE_BY", "Entities Graph"),
        relation_carrier("CA-R-901005", "Entity/Relation/Type: IS_NARROWER_THAN", "Entities Graph"),
        relation_carrier("CA-R-901007", "IS_ALLOWED_VALUE_OF", "Entities Graph"),
        {
            **relation_carrier("CA-R-901006", "a prose topic", "Entities Graph"),
            "subjects": {"governs": "Entity/Node/Continuant/Atom"},
        },
    ]
    carriers[2]["body"] = (
        "## Scope\n\nAn IS_BORNE_BY Relation from Entity A to Entity B **in** the Entities Graph.\n"
        "\n## Claim\nText."
    )
    refresh_raw(carriers[2])
    carriers[-2]["body"] = carriers[-2]["body"].replace("in the", "within the")
    refresh_raw(carriers[-2])
    return carriers


class DeclarationSourcesTests(unittest.TestCase):
    def test_relation_identity_is_graph_kind_and_exact_literal_name(self):
        carriers = _relation_identity_carriers()
        catalog = compose_declaration_catalog(carriers)
        rows = {(row["graph_kind"], row["canonical_name"]): row for row in catalog["relation_types"]}

        self.assertEqual(
            set(rows),
            {
                ("Entities Graph", "IS_NARROWER_THAN"),
                ("Terms Graph", "IS_NARROWER_THAN"),
                ("Entities Graph", "IS_BORNE_BY"),
                ("Entities Graph", "BORNE_BY"),
                ("Entities Graph", "IS_ALLOWED_VALUE_OF"),
            },
        )
        self.assertEqual(len(rows[("Entities Graph", "IS_NARROWER_THAN")]["sources"]), 2)
        self.assertEqual(
            rows[("Entities Graph", "IS_BORNE_BY")]["sources"][0]["version"], 2
        )
        self.assertEqual(
            rows[("Entities Graph", "IS_NARROWER_THAN")]["metadata"],
            {
                "meaning": None,
                "direction": None,
                "inverse": None,
                "authority_effect": None,
                "transitivity": None,
                "applicability": None,
                "status": None,
                "exclusive_purpose": None,
            },
        )
        self.assertTrue(rows[("Entities Graph", "IS_NARROWER_THAN")]["evidence"])

    def test_relation_candidates_without_unique_scope_graph_remain_unresolved(self):
        missing_scope = relation_carrier(
            "CA-R-901011", "Entity/Relation/Type: CONTAINS", "Entities Graph"
        )
        missing_scope["body"] = "## Scope\n\nA named relation but no owner.\n"
        ambiguous_scope = relation_carrier(
            "CA-R-901012", "Entity/Relation/Type: CONTAINS", "Entities Graph"
        )
        ambiguous_scope["body"] = (
            "## Scope\n\nCONTAINS Relation in the Entities Graph and in the Terms Graph.\n"
        )
        refresh_raw(missing_scope)
        refresh_raw(ambiguous_scope)

        catalog = compose_declaration_catalog([missing_scope, ambiguous_scope])

        self.assertEqual(catalog["relation_types"], [])
        self.assertEqual(len(catalog["unresolved"]), 2)
        self.assertTrue(all("owning graph kind" in row["reason"] for row in catalog["unresolved"]))

    def test_scope_does_not_admit_incidental_graph_mention_or_fenced_fake_scope(self):
        incidental = relation_carrier("CA-R-901013", "IS_BORNE_BY", "Entities Graph")
        incidental["body"] = (
            "## Scope\n\nIS_BORNE_BY Relation is described here. The check applies to the Entities Graph.\n"
        )
        refresh_raw(incidental)
        fenced = relation_carrier("CA-R-901014", "IS_BORNE_BY", "Entities Graph")
        fenced["body"] = (
            "```markdown\n## Scope\n\nIS_BORNE_BY Relation in the Entities Graph.\n```\n"
            "## Claim\nReal body without a Scope.\n"
        )
        refresh_raw(fenced)

        catalog = compose_declaration_catalog([incidental, fenced])

        self.assertEqual(catalog["relation_types"], [])
        self.assertEqual(len(catalog["unresolved"]), 2)

    def test_approved_relation_identity_resolver_requires_exact_unique_active_definition(self):
        def definition(atom_id):
            carrier = relation_carrier(atom_id, "Entity/Graph Syntax <+ Relation//IS_PROPERTY_OF", "Entities Graph")
            carrier["metadata"]["type"] = "Relation Definition"
            raw = carrier["raw"].replace(
                b"status: Active\n---", b"status: Active\ntype: Relation Definition\nsubjects:\n"
                b"  governs: Entity/Graph Syntax <+ Relation//IS_PROPERTY_OF\n---")
            carrier["raw"] = raw
            carrier["source"]["sha256"] = hashlib.sha256(raw).hexdigest()
            return carrier
        carrier = definition("CA-R-99001")
        resolved = resolve_relation_authorities([carrier], ["IS_PROPERTY_OF"])
        self.assertEqual(carrier["source"], resolved["IS_PROPERTY_OF"])
        with self.assertRaisesRegex(ValueError, "found 2"):
            resolve_relation_authorities([carrier, definition("CA-R-99002")], ["IS_PROPERTY_OF"])
        for change in ("draft", "bytes", "missing", "metadata"):
            with self.subTest(change=change):
                altered = definition("CA-R-99001")
                if change == "draft":
                    altered["metadata"]["status"] = "Draft"
                elif change == "bytes":
                    altered["raw"] += b"changed"
                elif change == "metadata":
                    altered["metadata"]["version"] = 2
                    altered["source"]["version"] = 2
                with self.assertRaisesRegex(ValueError, "found 0"):
                    resolve_relation_authorities([] if change == "missing" else [altered], ["IS_PROPERTY_OF"])

    def test_migrated_role_form_relation_definition_stays_in_the_relation_catalog(self):
        body = "## Scope\n\nRUN Relation in the Entities Graph.\n\n## Claim\nText.\n"
        raw = (
            "---\natom_id: CA-R-901090\nversion: 1\nstatus: Active\n"
            "role: Requirement\nform: Relation Definition\nsubjects:\n"
            "  active: Entity/CFEL <+ Relation//RUN\n  passive: []\n---\n" + body
        ).encode("utf-8")
        carrier = {
            "source": {
                "atom_id": "CA-R-901090", "version": 1, "path": "CA-R-901090.md",
                "sha256": hashlib.sha256(raw).hexdigest(),
            },
            "metadata": {
                "atom_id": "CA-R-901090", "version": 1, "status": "Active",
                "role": "Requirement", "form": "Relation Definition",
            },
            "subjects": {"active": "Entity/CFEL <+ Relation//RUN", "passive": []},
            "body": body,
            "raw_body": body,
            "raw": raw,
        }

        self.assertEqual(
            carrier["source"], resolve_relation_authorities([carrier], ["RUN"])["RUN"],
        )
        catalog = compose_declaration_catalog([carrier])
        self.assertEqual(
            [("Entities Graph", "RUN")],
            [(row["graph_kind"], row["canonical_name"]) for row in catalog["relation_types"]],
        )
