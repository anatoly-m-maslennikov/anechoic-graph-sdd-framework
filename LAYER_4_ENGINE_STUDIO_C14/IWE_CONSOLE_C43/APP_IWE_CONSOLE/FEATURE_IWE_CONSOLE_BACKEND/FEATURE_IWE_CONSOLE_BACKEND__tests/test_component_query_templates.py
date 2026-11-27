"""Verify Component query templates against their projected tables."""

from unittest import TestCase

import duckdb
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    query_templates \
    import run_arguments  # fmt: skip


class ComponentQueryTests(TestCase):
    def test_contract_and_solution_queries(self):
        db = duckdb.connect(":memory:")
        self.addCleanup(db.close)
        db.execute(
            "CREATE TABLE components (component_id VARCHAR, name VARCHAR, manifest_ref VARCHAR, has_contract BOOLEAN, purpose_refs VARCHAR[])"
        )
        db.execute(
            "INSERT INTO components VALUES ('C3', 'Example', 'AN-S-3@2', true, []), ('C4', 'Empty', 'AN-S-4@1', false, []), ('C00', 'Project', 'AN-S-1@1', false, ['AN-S-1@1'])"
        )
        db.execute(
            'CREATE TABLE atoms (reference VARCHAR, status_group VARCHAR, "content.summary" VARCHAR, relative_path VARCHAR, filename VARCHAR, "header.state.status" VARCHAR, "header.tier" INTEGER, "header.context.template" VARCHAR)'
        )
        db.execute(
            "INSERT INTO atoms VALUES ('AN-S-1', 'Current', 'Root', '', 'root.md', 'active', -1, 'project_manifest'), ('AN-S-3', 'Current', 'Manifest', '', 'manifest.md', 'active', 1, 'component_manifest'), ('AN-S-4', 'Current', 'Empty', '', 'empty.md', 'active', 1, 'component_manifest'), ('AN-S-5', 'Current', 'Solution', '', 'solution.md', 'active', 0, 'solution'), ('AN-S-6', 'Current', 'Other', '', 'other.md', 'active', 1, 'solution'), ('AN-S-7', 'Current', 'Draft', '', 'draft.md', 'draft', 0, 'solution'), ('AN-S-8', 'Current', 'Axiom', '', 'axiom.md', 'active', 0, 'axiom')"
        )
        db.execute(
            "CREATE TABLE native_references (reference VARCHAR, exact_ref VARCHAR)"
        )
        db.execute(
            "INSERT INTO native_references VALUES ('AN-S-1', 'AN-S-1@1'), ('AN-S-3', 'AN-S-3@2'), ('AN-S-4', 'AN-S-4@1'), ('AN-S-5', 'AN-S-5@1'), ('AN-S-6', 'AN-S-6@1'), ('AN-S-7', 'AN-S-7@1'), ('AN-S-8', 'AN-S-8@1')"
        )
        db.execute(
            "CREATE TABLE relations (source_ref VARCHAR, source_kind VARCHAR, target_kind VARCHAR, target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)"
        )
        db.execute(
            "INSERT INTO relations VALUES ('AN-S-5', 'Atom', 'Component', 'C3', 'IS_CONTAINED_BY', false), ('AN-S-6', 'Atom', 'Component', 'C3', 'IS_CONTAINED_BY', false), ('AN-S-7', 'Atom', 'Component', 'C3', 'CONTAINED_BY', false), ('AN-S-8', 'Atom', 'Component', 'C3', 'IS_CONTAINED_BY', false)"
        )

        def refs(template, component):
            sql = run_arguments(
                {"template": template, "component": component}
            )["sql"]
            return [row[0] for row in db.execute(sql).fetchall()]

        for label in ("C00", "Project"):
            self.assertEqual(["AN-S-1@1"], refs("get_component_manifest", label))
            self.assertEqual(["AN-S-1@1"], refs("get_component_purpose", label))
        self.assertEqual(["AN-S-3@2"], refs("fetch_contracts", "C3"))
        self.assertEqual([], refs("fetch_contracts", "C4"))
        self.assertEqual(["AN-S-5@1"], refs("fetch_solutions", "C3"))
