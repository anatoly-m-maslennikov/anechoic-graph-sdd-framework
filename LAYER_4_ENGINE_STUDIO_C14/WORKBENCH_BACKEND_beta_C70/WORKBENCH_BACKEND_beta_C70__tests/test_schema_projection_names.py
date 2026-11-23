"""Check public schema aliases and rebuild target routing."""

import unittest
from unittest.mock import AsyncMock, patch

from .. import projection_tools
from ..projection_tools import FLOW_HISTORY, TABLE_ALIASES, TABLES, _target, invoke
from ..schema_tools import _valid_schema


class SchemaProjectionNamesTests(unittest.TestCase):
    def test_rebuild_aliases_and_unknown_targets(self):
        business = {"package_coupling", "architecture_code_metrics", "architecture_spec_metrics",
                    "architecture_ratios", "package_review_profiles", "package_largest_files"}
        expected = {f"{'biz' if name in business else 'mrt'}_{name}": name for name in TABLES}
        expected.update({f"{'src' if name == 'flow_events' else 'mrt'}_{name}": name for name in FLOW_HISTORY})
        expected.update({"ops_work_journal": "work_journal", "ops_query_log": "query_log"})
        expected.update({f"mrt_real_graph_{name}": name for name in (
            "import_edges", "package_imports", "package_external_imports", "code_units", "code_unit_calls",
            "test_edges", "tested_by_edges")})
        expected.update({
            "mrt_atom_graph_relations": "relations",
            "mrt_atom_references": "native_references",
            "mrt_flow_actions": "component_flows",
            "mrt_real_graph_import_nodes": "import_nodes",
            "mrt_real_graph_import_occurrences": "module_imports",
            "mrt_real_graph_package_spec_bindings": "architecture_package_bindings",
            "mrt_diag_import_read_issues": "import_read_issues",
            "mrt_diag_import_cycles": "import_cycles",
            "mrt_diag_antipatterns": "antipattern_findings",
            "mrt_diag_code_access": "code_access_findings",
            "mrt_diag_state_effects": "state_effect_findings",
            **{f"mrt_{family}_atoms": "atoms" for family in ("spec", "ticket", "project_config")},
        })
        self.assertEqual(expected, TABLE_ALIASES)
        for alias, original in TABLE_ALIASES.items():
            if original in (*TABLES, *FLOW_HISTORY):
                with self.subTest(alias=alias):
                    self.assertEqual((original, f"main.{alias}"), _target({"target": f"main.{alias}"}))
                    self.assertEqual((original, original), _target({"target": original}))
            else:
                with self.assertRaises(ValueError):
                    _target({"target": alias})
        for name in ("mrt_flow_events", "mrt_package_coupling", "biz_atoms", "mrt_unknown"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                _target({"target": name})
        with self.assertRaises(ValueError):
            _target({"target": "ops_ingestion_issues"})
        result_id = "a" * 32
        self.assertEqual((result_id, f"workbench_results.query_{result_id}"),
                         _target({"target": f"workbench_results.query_{result_id}"}))

    def test_schema_aliases_and_status_values(self):
        status = {"name": "header.state.status", "type": "VARCHAR", "values": ["active"]}
        for table in (*TABLES, *FLOW_HISTORY, "work_journal", "query_log", *TABLE_ALIASES):
            columns = [status] if TABLE_ALIASES.get(table, table) == "atoms" else []
            with self.subTest(table=table):
                self.assertTrue(_valid_schema({"tables": {table: columns}}))
        self.assertFalse(_valid_schema({"tables": {"mrt_unknown": []}}))
        self.assertTrue(_valid_schema({"tables": {"ops_ingestion_issues": [{"name": "code", "type": "VARCHAR"}]}}))
        self.assertFalse(_valid_schema({"tables": {"ops_generation_carrier_hashes": []}}))
        self.assertFalse(_valid_schema({"tables": {"biz_atoms": [status]}}))
        self.assertFalse(_valid_schema({"tables": {"mrt_relations": [status]}}))


class IngestionStatusTests(unittest.IsolatedAsyncioTestCase):
    async def test_status_reads_issues_without_sql(self):
        rows = [{"source": "atom", "relative_path": "bad.md", "code": "invalid",
                 "message": "bad Atom", "atom_ref": None, "related_paths": []}]
        with patch.object(projection_tools, "upstream", new_callable=AsyncMock,
                          side_effect=[{"result": {"active": None, "latest": None}},
                                       {"result": {"rows": rows}}]) as upstream:
            result = await invoke("workbench_status", {}, "kernel", "orchestrator", None, "instance")
        self.assertEqual(rows, result["result"]["value"]["ingestion_issues"])
        self.assertEqual("/ingestion/issues", upstream.await_args_list[1].args[2])
        self.assertEqual({"instance_id": "instance"}, upstream.await_args_list[1].kwargs["params"])
