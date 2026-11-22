"""Exercise the Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from dataclasses import replace
from io import StringIO
import json
from unittest.mock import patch

import httpx2
from mcp import types
from starlette.applications import Starlette

from . import test_native_query_stdio as fixture
from KERNEL_MIXER_C59.import_cache import read_import_sources
from .native_query_test_support import create_native_gateway
from MCP_PATCHBAY_C21.FEATURE_MCP.workbench_web import routes


class ImportGraphCases2:
    async def _check_graph_schema(self, client, base, rows):
        schema = await client.post(f"{base}/schema", json={})
        self.assertEqual(schema.status_code, 200, schema.text)
        self.assertTrue({"import_nodes", "module_imports", "import_edges", "package_imports"}
                        <= set(schema.json()["tables"]))
        self.assertEqual(await rows("""
            SELECT DISTINCT s.kind, d.kind, e.derived
            FROM import_edges e JOIN import_nodes s ON s.node_key = e.source_key
            JOIN import_nodes d ON d.node_key = e.target_key
            JOIN module_imports i USING (occurrence_key)
            WHERE i.written_specifier = 'dep.helper' AND i.line = 1
            ORDER BY ALL
        """), [["module", "module", False], ["module", "package", True],
               ["package", "module", True], ["package", "package", True]])
        self.assertEqual(await rows("""
            SELECT written_specifier, line, resolution_status FROM module_imports
            WHERE written_specifier IN ('dep.helper', 'missing', '.', 'declared') ORDER BY line
        """), [["dep.helper", 1, "internal"], ["missing", 3, "unresolved"],
               ["dep.helper", 4, "internal"], [".", 6, "internal"], ["declared", 7, "external"]])
        self.assertEqual(await rows("""
            SELECT relative_path, scan_status FROM import_nodes
            WHERE relative_path IN ('src/generated/ignored.py', 'src/unsupported.ts')
        """), [["src/unsupported.ts", "unsupported"]])
        graph = """
            SELECT count(*) FROM GRAPH_TABLE (anechoic
            MATCH (s:ImportNode)-[e:Imports]->(d:ImportNode)
            COLUMNS (e.occurrence_key AS occurrence_key))
        """
        self.assertGreater((await rows(graph))[0][0], 0)
        self.assertTrue(await rows("SELECT * FROM relations LIMIT 1"))
        counts = "SELECT count(*) FROM package_imports"
        return graph, counts

    async def _check_graph_updates(self, gateway, rows, graph):
        owner = gateway._native_query
        with owner._owner()._lock:
            importer = read_import_sources(owner._owner()._connection)["src/app/main.py"]
        target = self._source("src/missing.py", "")
        sql = "SELECT resolution_status FROM module_imports WHERE written_specifier = 'missing'"
        async with asyncio.timeout(6):
            while await rows(sql) != [["internal"]]:
                await asyncio.sleep(.03)
        target.rename(target.with_name("moved.py"))
        async with asyncio.timeout(6):
            while await rows(sql) != [["unresolved"]]:
                await asyncio.sleep(.03)
        with owner._owner()._lock:
            self.assertEqual(importer, read_import_sources(owner._owner()._connection)["src/app/main.py"])

        self._source("new_root/added.py", "import os\n")
        async with asyncio.timeout(6):
            while not await rows("SELECT 1 FROM import_nodes WHERE relative_path = 'new_root/added.py'"):
                await asyncio.sleep(.03)

        self._write("001_TICKETS/TASKS/AN-T-010-TASK--external.md", "AN-T-010", "active", 1)
        async with asyncio.timeout(6):
            while not await rows("SELECT 1 FROM atoms WHERE reference = 'AN-T-010'"):
                await asyncio.sleep(.03)
        self.assertGreater((await rows(graph))[0][0], 0)

        owner._inputs = replace(owner._inputs, relation_types=owner._inputs.relation_types | {"TEST_LINK"})
        owner._refresh_after_write(owner._owner())
        self.assertGreater((await rows(graph))[0][0], 0)


    async def test_queries_four_relations_and_notices_target_changes(self):
        self._source("src/app/__init__.py", "")
        self._source("src/app/util.py", "")
        self._source("src/dep/__init__.py", "")
        self._source("src/dep/helper.py", "import app.main\n")
        self._source("src/app/main.py", "import dep.helper\nimport dep\nimport missing\nimport dep.helper\n"
                     "if False:\n    from . import util as helper\nimport declared\n")
        self._source("pyproject.toml", '[dependency-groups]\nworkbench = ["declared>=1"]\n')
        self._source("src/unsupported.ts", "import './app';\n")
        self._source("src/generated/ignored.py", "import dep\n")
        self._source("src/invalid.py", "import\n")
        stderr = StringIO()
        with redirect_stderr(stderr):
            gateway = await self._gateway()
        self.assertIn("src/invalid.py", stderr.getvalue())
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                     base_url="http://127.0.0.1:18093") as client:
            base = "/anechoic/Anechoic/api"

            async def rows(sql):
                response = await client.post(f"{base}/run", json={"sql": sql, "result_delivery": "inline"})
                self.assertEqual(response.status_code, 200, response.text)
                return response.json()["rows"]

            graph, counts = await self._check_graph_schema(client, base, rows)

            async def workbench(operation, arguments):
                response = await client.post(f"{base}/interface", json={
                    "operation": operation, "arguments": arguments,
                })
                self.assertEqual(response.status_code, 200, response.text)
                return response.json()

            workspace = await workbench("workspace_open", {"session_id": "imports"})
            view = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
            await workbench("view_update", view | {"sql": counts, "expected_revision": 0})
            await workbench("view_run", view)
            result = await workbench("view_fetch", view | {"result_delivery": "inline"})
            self.assertEqual(result["rows"], await rows(counts))

            await self._check_graph_updates(gateway, rows, graph)


    async def test_spec_bindings_are_indexed_and_follow_sidecar_changes(self):
        self._source("src/app/main.py", "pass\n")
        sidecar = self._source("src/app/app__spec_bind.yaml", "implements:\n  - AN-S-001@1\n")
        self._source("src/app/main.py.spec_trace.md", "## Implements\n- AN-S-10@2\n")
        gateway = await self._gateway()
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                     base_url="http://127.0.0.1:18093") as client:
            base = "/anechoic/Anechoic/api"
            schema = await client.post(f"{base}/schema", json={})
            self.assertEqual(schema.status_code, 200, schema.text)
            self.assertIn("implementation_rmedo", schema.json()["tables"])

            async def pins():
                result = await client.post(f"{base}/run", json={
                    "sql": "SELECT owner_path, entry_kind, atom_id, version FROM implementation_rmedo ORDER BY 1",
                    "result_delivery": "inline",
                })
                self.assertEqual(result.status_code, 200, result.text)
                return result.json()["rows"]

            module = ["src/app/main.py", "implements", "AN-S-10", 2]
            self.assertEqual(await pins(), [["src/app", "implements", "AN-S-001", 1], module])
            sidecar.write_text("applies:\n  - AN-S-007@3\n", encoding="utf-8")
            async with asyncio.timeout(6):
                while await pins() != [["src/app", "applies", "AN-S-007", 3], module]:
                    await asyncio.sleep(.03)
            sidecar.unlink()
            async with asyncio.timeout(6):
                while await pins() != [module]:
                    await asyncio.sleep(.03)


    def _prepare_sidecars(self):
        self._source('src/app/main.py', 'pass\n')
        self._source('src/other/other.py', 'pass\n')
        sidecar = self._source('src/app/app__spec_bind.yaml', 'implements: [AN-S-001@1]\n')
        other_sidecar = self._source('src/other/other__spec_bind.yaml', 'implements: [AN-S-001@1]\n')
        module_sidecar = self._source('src/app/main.py.spec_trace.md', '## Implements\n- AN-S-10@2\n')
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        owner = gateway._native_query
        owner.start()
        self.addCleanup(owner.close)
        store = owner._owner()

        return owner, store, sidecar, other_sidecar, module_sidecar

    def _check_trace_rollback(self, owner, store, snapshot):
        before = snapshot()
        replacement = [('src/app', 'src/app/app__spec_bind.yaml', 'implements', 'AN-S-001', 1)]
        with patch('KERNEL_MIXER_C59.native_query_projection.native_trace_snapshot', return_value=(replacement, {'src/app': 'valid'})), \
             patch('KERNEL_MIXER_C59.native_query_projection.replace_package_audit', side_effect=RuntimeError('audit failed')):
            with self.assertRaisesRegex(RuntimeError, 'audit failed'):
                owner._refresh_traces(store, {'src/app/app__spec_bind.yaml'})
        self.assertEqual(before, snapshot())


    def _trace_snapshot(self, store):
        with store._lock:
            pins = store._connection.execute(
                'SELECT owner_path, entry_kind, atom_id, version FROM implementation_rmedo ORDER BY 1'
            ).fetchall()
            states = dict(store._connection.execute(
                'SELECT relative_path, binding_status FROM package_audit').fetchall())
        return pins, states


    async def test_sidecar_only_refresh_reads_only_affected_owner_and_updates_audit(self):
        from KERNEL_MIXER_C59.spec_trace import _read_pins

        owner, store, sidecar, other_sidecar, module_sidecar = self._prepare_sidecars()

        def snapshot():
            return self._trace_snapshot(store)

        other = ('src/other', 'implements', 'AN-S-001', 1)
        module = ('src/app/main.py', 'implements', 'AN-S-10', 2)
        with patch('KERNEL_MIXER_C59.spec_trace._read_pins', wraps=_read_pins) as reads, \
             patch.object(owner, '_prepare_realization', wraps=owner._prepare_realization) as prepare:
            async def expect(pin, state):
                async with asyncio.timeout(6):
                    while True:
                        pins, states = snapshot()
                        if pins == sorted([row for row in (pin, module, other) if row]) and states['src/app'] == state:
                            return
                        await asyncio.sleep(.03)

            sidecar.write_text('applies: [AN-S-001@1]\n')
            await expect(('src/app', 'applies', 'AN-S-001', 1), 'valid')
            stderr = StringIO()
            with redirect_stderr(stderr):
                sidecar.write_text('implements: invalid\n')
                await expect(None, 'invalid')
            self.assertIn('Invalid spec trace', stderr.getvalue())
            fallback = self._source('src/app/app.p.spec_trace.md', '## Implements\n- AN-S-001@1\n')
            sidecar.unlink()
            await expect(('src/app', 'implements', 'AN-S-001', 1), 'missing')
            fallback.unlink()
            await expect(None, 'missing')
            module = ('src/app/main.py', 'implements', 'AN-S-11', 3)
            module_sidecar.write_text('## Implements\n- AN-S-11@3\n')
            await expect(None, 'missing')
            sidecar.write_text('applies: [AN-S-001@1]\n')
            await expect(('src/app', 'applies', 'AN-S-001', 1), 'valid')
            self.assertNotIn(other_sidecar, {call.args[2] for call in reads.call_args_list})
            other = ('src/other', 'applies', 'AN-S-001', 1)
            sidecar.replace(other_sidecar)
            await expect(None, 'missing')
            self.assertTrue(reads.call_count)
            self.assertEqual({sidecar, other_sidecar, fallback, module_sidecar},
                             {call.args[2] for call in reads.call_args_list})
            prepare.assert_not_called()
        self._check_trace_rollback(owner, store, snapshot)


    async def test_component_ratios_follow_formal_test_assets(self):
        self._source("src/UNIT_C1/main.py", "pass\npass\n")
        self._source("src/UNIT_C1/tests/test_legacy.py", "pass\n")
        self._source("src/UNIT_C1/UNIT_C1__tests/test_main.py", "pass\n")
        asset = self._source("src/UNIT_C1/UNIT_C1__tests/assets/input.txt", "x\n")
        body = "## Summary\n\nDescribe C1.\n"
        spec = self._source(f"{fixture.CONTROL}/UNIT_C1/AN-S-007-SPEC--description.md", (
            "---\nidentity: {atom_id: AN-S-007}\ncontext: {container: {component: C1}, lens: SPEC}\n"
            "state: {status: active, version: 1}\n---\n" + body
        ))
        structure = self._source(".anechoic_tmp/structure.json", json.dumps({
            "model_sha256": "fixture", "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
            "components": {"C1": {"parent": "C00", "ref": "AN-S-006@1", "sha256": "fixture",
                                  "source_path": "AN-S-006-SPEC-COMPONENT_MANIFEST--unit.md",
                                  "fields": {"name": "Unit"}}},
        }))
        gateway = await self._gateway(structure_snapshot=structure)

        async def ratios():
            response = await gateway.call(None, types.CallToolRequestParams(name="query_run", arguments={
                "sql": "SELECT denominator, realization_kb, realization_lines, spec_full_kb_ratio, "
                       "spec_body_kb_ratio, spec_body_lines_ratio FROM component_metrics "
                       "WHERE component_id = 'C1' ORDER BY denominator", "result_delivery": "inline",
            }))
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"]

        populations = {"implementation": (10, 2), "implementation_and_tests": (17, 4),
                       "test_assets": (2, 1), "test_code": (5, 1), "tests": (7, 2)}
        expected = [[kind, size / 1000, lines, spec.stat().st_size / size, len(body) / size, 3 / lines]
                    for kind, (size, lines) in sorted(populations.items())]
        self.assertEqual(expected, await ratios())
        asset.unlink()
        async with asyncio.timeout(6):
            while (await ratios())[2] != ["test_assets", 0.0, 0, None, None, None]:
                await asyncio.sleep(.03)

