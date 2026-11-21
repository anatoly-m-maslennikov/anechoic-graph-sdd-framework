"""Exercise the Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from dataclasses import replace
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import duckdb
import httpx2
from mcp import types
from starlette.applications import Starlette
from watchdog.observers.polling import PollingObserver

import test_native_query_stdio as fixture
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_cache import read_import_sources
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_tables import publish_imports
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from native_query import create_native_gateway
from workbench_web import routes


class NativeImportGraphTests(unittest.IsolatedAsyncioTestCase):
    _write = fixture.NativeQueryStdioTests._write

    def setUp(self):
        fixture.NativeQueryStdioTests.setUp(self)
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

    def _source(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    async def _gateway(self, *, enabled=True, structure_snapshot=None):
        inputs = fixture._native_inputs()

        def validate(fields, component):
            manifest = inputs.validate_manifest(fields, component)
            workbench = {"import_graph": {"python_roots": ["src"]} if enabled else False}
            return SimpleNamespace(name=manifest.name, prefix=manifest.prefix,
                                   parameters={"runtime": {"workbench": workbench}})

        gateway = create_native_gateway(self.root, fixture.CONTROL, replace(inputs, validate_manifest=validate))
        if structure_snapshot is not None:
            selected = replace(gateway.selection, structure_snapshot=structure_snapshot)
            gateway.selection = gateway._native_query.selection = selected
        with patch("APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_watcher.NativeObserver",
                   lambda: PollingObserver(timeout=.05)):
            await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        return gateway

    async def test_lifecycle_writes_refresh_atoms_without_full_projection(self):
        unrelated = self._source(f"{fixture.CONTROL}/001_TICKETS/TASKS/AN-T-010-TASK--existing-task.md", """---
atom_family: TKT
atom_id: AN-T-010
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-19T00:00:00Z'
---
## Summary

Existing task
""")
        gateway = await self._gateway(enabled=False)
        owner = gateway._native_query
        store = owner._owner()
        with owner._interface_lock, patch.object(owner, '_project', side_effect=AssertionError('full projection')):
            created = owner.lifecycle('atom_lifecycle_create_draft', {'newAtom': {
                'template': 'task', 'label': 'Task', 'container': {'component': 'C00'},
                'body': '## Summary\n\nIncremental lifecycle refresh.\n',
            }})
            self.assertFalse(created['errors'], created)
            draft = created['savedDraft']
            with store._lock:
                self.assertEqual(store._connection.execute(
                    'SELECT reference FROM atoms WHERE reference = ?', [draft['ref_id']]
                ).fetchall(), [(draft['ref_id'],)])

            reads = []
            read = ReadContext.read

            def record_read(reader, path, **kwargs):
                reads.append(path)
                return read(reader, path, **kwargs)

            with patch.object(ReadContext, 'read', record_read):
                promoted = owner.lifecycle('atom_lifecycle_promote_draft', {
                    'target': {'ref_id': draft['ref_id'], 'version': draft['version']},
                    'targetStatus': 'backlog',
                })
            self.assertNotIn(unrelated, reads)
            self.assertFalse(promoted['errors'], promoted)
            with store._lock:
                self.assertEqual(store._connection.execute(
                    'SELECT reference FROM atoms WHERE reference IN (?, ?) ORDER BY reference',
                    [draft['ref_id'], draft['atom_id']],
                ).fetchall(), [(draft['atom_id'],)])

            revised = owner.lifecycle('atom_lifecycle_update', {
                'sourceCurrent': {'ref_id': draft['atom_id'], 'version': 1},
                'changes': {'body': '## Summary\n\nIncremental lifecycle refresh.\n\nRevised.\n'},
            })
            self.assertFalse(revised['errors'], revised)
            revision = revised['savedDraft']
            published = owner.lifecycle('atom_lifecycle_promote_draft', {
                'target': {'ref_id': revision['ref_id'], 'version': revision['version']},
                'targetStatus': 'backlog',
            })
            self.assertFalse(published['errors'], published)
            active, archived = draft['atom_id'], draft['atom_id'] + '@1'
            with store._lock:
                self.assertEqual(store._connection.execute(
                    'SELECT reference, "header.state.version", "header.state.status" '
                    'FROM atoms WHERE reference IN (?, ?, ?) ORDER BY "header.state.version"',
                    [active, archived, revision['ref_id']],
                ).fetchall(), [(archived, 1, 'archived'), (active, 2, 'backlog')])

    async def test_promotion_detects_unseen_duplicate_with_restored_mtime(self):
        carrier = """---
atom_family: TKT
atom_id: AN-T-010
structure:
  container:
    component: C00
  priority: 2
context:
  template: task
  label: Task
state:
  status: active
  version: 1
  updated_at: '2026-11-19T00:00:00Z'
---
## Summary

Existing task
"""
        self._source(f"{fixture.CONTROL}/001_TICKETS/TASKS/AN-T-010-TASK--existing-task.md", carrier)
        duplicate = self._source(
            f"{fixture.CONTROL}/001_TICKETS/TASKS/09_archived/unrelated.md",
            carrier.replace('AN-T-010', 'AN-T-999').replace('status: active', 'status: archived')
                   .replace('version: 1', 'version: 2'),
        )
        gateway = await self._gateway(enabled=False)
        owner = gateway._native_query
        with owner._interface_lock:
            result = owner.lifecycle('atom_lifecycle_update', {
                'sourceCurrent': {'ref_id': 'AN-T-010', 'version': 1},
                'changes': {'body': '## Summary\n\nExisting task\n\nRevised.\n'},
            })
            self.assertFalse(result['errors'], result)
            self.assertIn('savedDraft', result, result)
            draft = result['savedDraft']
            before = duplicate.stat()
            duplicate.write_text(duplicate.read_text().replace('AN-T-999', 'AN-T-010'))
            os.utime(duplicate, ns=(before.st_atime_ns, before.st_mtime_ns))
            self.assertEqual(duplicate.stat().st_size, before.st_size)
            self.assertEqual(duplicate.stat().st_mtime_ns, before.st_mtime_ns)
            promoted = owner.lifecycle('atom_lifecycle_promote_draft', {
                'target': {'ref_id': draft['ref_id'], 'version': draft['version']},
                'targetStatus': 'backlog',
            })
            self.assertEqual(promoted['outcome'], 'needs_input', promoted)
            self.assertIn('already has a non-Draft revision',
                          promoted['requested_input']['target']['error'])
            self.assertFalse(promoted['effects'])
            self.assertTrue(duplicate.exists())

    async def test_workbench_file_and_directory_changes_read_only_affected_carriers(self):
        gateway = await self._gateway(enabled=False)
        owner = gateway._native_query
        store = owner._owner()
        control = self.root / fixture.CONTROL
        source = control / "__TKT/TASKS/AN-T-010-TASK--created.md"
        read, inventory = ReadContext.read, ReadContext.inventory
        reads = []

        def record_read(reader, path, **kwargs):
            raw = read(reader, path, **kwargs)
            if raw is not None:
                reads.append(path)
            return raw

        def scoped_inventory(reader, path, **kwargs):
            self.assertNotEqual(path, control)
            return inventory(reader, path, **kwargs)

        def refresh(operations, *, expected, files):
            batch = [{"old_path": old.relative_to(self.root).as_posix() if old else None,
                      "new_path": new.relative_to(self.root).as_posix() if new else None}
                     for old, new in operations]
            reads.clear()
            self.assertEqual(owner._watch_atom_changes(store, batch, set()), set())
            self.assertCountEqual(reads, expected)
            with store._lock:
                rows = store._connection.execute(
                    "SELECT relative_path, filename FROM atoms WHERE reference IN ('AN-T-010', 'AN-T-011')"
                ).fetchall()
            self.assertCountEqual([self.root / folder / name for folder, name in rows], files)

        with (owner._interface_lock, patch.object(ReadContext, "read", record_read),
              patch.object(ReadContext, "inventory", scoped_inventory)):
            self._write(source.relative_to(control), "AN-T-010", "active", 1)
            refresh([(None, source), (None, source)], expected=[source], files=[source])
            refresh([(None, source)], expected=[], files=[source])
            self._write(source.relative_to(control), "AN-T-010", "active", 2)
            refresh([(None, source)], expected=[source], files=[source])
            temporary = source.with_suffix(".tmp")
            temporary.write_bytes(source.read_bytes().replace(b"version: 2", b"version: 3"))
            temporary.replace(source)
            refresh([(temporary, source)], expected=[source], files=[source])
            with store._lock:
                self.assertEqual(store._connection.execute(
                    'SELECT "header.state.version" FROM atoms WHERE reference = ?', ['AN-T-010'],
                ).fetchall(), [(3,)])
            renamed = source.rename(source.with_name("AN-T-010-TASK--renamed.md"))
            refresh([(source, renamed)], expected=[renamed], files=[renamed])
            folder = control / "__TKT/TASKS/container"
            added = folder / "nested/AN-T-011-TASK--nested.md"
            self._write(added.relative_to(control), "AN-T-011", "active", 1)
            refresh([(None, folder), (None, added)], expected=[added], files=[renamed, added])
            moved = renamed.rename(folder / renamed.name)
            refresh([(renamed, moved)], expected=[moved], files=[moved, added])
            destination = folder.rename(folder.with_name("renamed-folder"))
            new_moved, new_added = [destination / path.relative_to(folder) for path in (moved, added)]
            refresh([(folder, destination), (added, new_added)], expected=[new_moved, new_added],
                    files=[new_moved, new_added])
            new_moved.unlink()
            refresh([(new_moved, None)], expected=[], files=[new_added])
            new_added.unlink()
            new_added.parent.rmdir()
            destination.rmdir()
            refresh([(destination, None)], expected=[], files=[])

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

            self._write("__TKT/TASKS/AN-T-010-TASK--external.md", "AN-T-010", "active", 1)
            async with asyncio.timeout(6):
                while not await rows("SELECT 1 FROM atoms WHERE reference = 'AN-T-010'"):
                    await asyncio.sleep(.03)
            self.assertGreater((await rows(graph))[0][0], 0)

            owner._inputs = replace(owner._inputs, relation_types=owner._inputs.relation_types | {"TEST_LINK"})
            owner._refresh_after_write(owner._owner())
            self.assertGreater((await rows(graph))[0][0], 0)

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

    async def test_sidecar_only_refresh_reads_only_affected_owner_and_updates_audit(self):
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import spec_trace

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

        def snapshot():
            with store._lock:
                pins = store._connection.execute(
                    'SELECT owner_path, entry_kind, atom_id, version FROM implementation_rmedo ORDER BY 1'
                ).fetchall()
                states = dict(store._connection.execute(
                    'SELECT relative_path, binding_status FROM package_audit').fetchall())
            return pins, states

        other = ('src/other', 'implements', 'AN-S-001', 1)
        module = ('src/app/main.py', 'implements', 'AN-S-10', 2)
        with patch.object(spec_trace, '_read_pins', wraps=spec_trace._read_pins) as reads, \
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
        before = snapshot()
        replacement = [('src/app', 'src/app/app__spec_bind.yaml', 'implements', 'AN-S-001', 1)]
        with patch('native_query.native_trace_snapshot', return_value=(replacement, {'src/app': 'valid'})), \
             patch('native_query.replace_package_audit', side_effect=RuntimeError('audit failed')):
            with self.assertRaisesRegex(RuntimeError, 'audit failed'):
                owner._refresh_traces(store, {'src/app/app__spec_bind.yaml'})
        self.assertEqual(before, snapshot())

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

    async def test_package_audit_tracks_exact_pins_and_contracts(self):
        package = "src/UNIT_C1/service_pkg1"
        self._source("src/UNIT_C1/__init__.py", "")
        marker = self._source(f"{package}/main__pub.py", "pass\n")
        self._source(f"{package}/child/main__internal.py", "pass\n")
        self._source(f"{package}/service_pkg1__tests/test_main.py", "pass\n")
        control = f"{fixture.CONTROL}/UNIT_C1"
        spec_source = (
            "---\nidentity: {atom_id: AN-S-007}\n"
            "context: {container: {component: C1}, lens: SPEC, template: PKG, package_id: pkg1}\n"
            "state: {status: active, version: 2}\n---\n"
            "## Summary\n\nDescribe the service.\n\n## Purpose\n\nProvide a service.\n\n"
            "## Contract\n\nAccept a request.\n"
        )
        spec = self._source(f"{control}/AN-S-007-SPEC-PKG--service.md", spec_source)
        self._source(f"{control}/099_archived/AN-S-007@1-SPEC-PKG--service.md",
                     spec_source.replace("active, version: 2", "archived, version: 1"))
        sidecar = self._source(
            f"{package}/service_pkg1__spec_bind.yaml",
            "implements: [AN-S-007@1, AN-S-999@1]\napplies: [AN-S-007@2]\n",
        )
        structure = self._source(".anechoic_tmp/structure.json", json.dumps({
            "model_sha256": "fixture", "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
            "components": {"C1": {"parent": "C00", "ref": "AN-S-006@1", "sha256": "fixture",
                                  "source_path": "AN-S-006-SPEC-COMPONENT_MANIFEST--unit.md",
                                  "fields": {"name": "Unit"}}},
        }))
        gateway = await self._gateway(structure_snapshot=structure)

        async def audit(owner=gateway, path=package):
            response = await owner.call(None, types.CallToolRequestParams(name="query_run", arguments={
                "sql": "SELECT has_internal, has_public, has_spec_bind, binding_status, "
                       "all_pins_active, list_sort(json_extract_string(pin_issues, '$[*].reason')), "
                       "contract_ref, contract_covered FROM package_audit "
                       f"WHERE relative_path = '{path}'",
                "result_delivery": "inline",
            }))
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"][0]

        async def expect_audit(expected):
            async with asyncio.timeout(6):
                while await audit() != expected:
                    await asyncio.sleep(.03)

        schema = await gateway.call(None, types.CallToolRequestParams(name="query_schema", arguments={}))
        self.assertIn("package_audit", schema.structured_content["tables"])
        self.assertEqual([False, True, True, "valid", False, ["archived", "missing"], "AN-S-007@2", False],
                         await audit())
        self.assertEqual([False, False, False, "missing", None, [], None, None],
                         await audit(path=f"{package}/service_pkg1__tests"))
        sidecar.write_text("{}\n", encoding="utf-8")
        await expect_audit([False, True, True, "empty", None, [], "AN-S-007@2", False])
        sidecar.write_text("implements: not-a-list\n", encoding="utf-8")
        await expect_audit([False, True, True, "invalid", None, [], "AN-S-007@2", False])
        self._source(f"{package}/service_pkg1.p.spec_trace.md", "## Implements\n- AN-S-007@2\n")
        sidecar.unlink()
        await expect_audit([False, True, False, "missing", None, [], "AN-S-007@2", False])
        sidecar.write_text("implements: [AN-S-007@2]\n", encoding="utf-8")
        marker.rename(marker.with_name("main__internal.py"))
        await expect_audit([True, False, True, "valid", True, [], "AN-S-007@2", True])
        updated_spec = spec_source.replace("version: 2", "version: 3")
        spec.write_text(updated_spec, encoding="utf-8")
        expected = [True, False, True, "valid", False, ["missing"], "AN-S-007@3", False]
        await expect_audit(expected)
        stderr = StringIO()
        with redirect_stderr(stderr):
            spec.write_text(updated_spec.replace("Accept a request.", ""), encoding="utf-8")
            await expect_audit(expected[:-2] + [None, None])
        self.assertIn("Invalid Package Spec", stderr.getvalue())
        spec.write_text(updated_spec, encoding="utf-8")
        await expect_audit(expected)
        rebuild = await gateway.call(None, types.CallToolRequestParams(
            name="query_rebuild", arguments={"target": "package_audit"}))
        self.assertFalse(rebuild.is_error, rebuild.structured_content)
        self.assertEqual(expected, await audit())
        await gateway.close()
        reopened = await self._gateway(structure_snapshot=structure)
        self.assertEqual(expected, await audit(owner=reopened))

    async def test_boundaries_follow_structure_and_named_imports(self):
        self._source("src/LEFT_C1/client.py", "from RIGHT_C2.api import exposed, hidden\n")
        self._source("src/RIGHT_C2/api.py", "exposed = 1\nhidden = 2\n")
        self._source("src/RIGHT_C2/service_pkg1/main.py", "pass\n")

        def carrier(ref, fields, **relations):
            return {"ref": ref, "sha256": "fixture", "source_path": "manifest.md",
                    "fields": fields, **relations}

        left = {"name": "Left", "layer": 2, "boundaries": {
            "state": "local", "io": {"client": [{"component": "C2", "interface": "run"}]}},
        }
        right = {"name": "Right", "layer": 1, "boundaries": {
            "code": {"exports": {"api.exposed": None}},
            "io": {"server": {"run": {"transport": "cli", "path": "src/RIGHT_C2/api.py"}}}},
        }
        snapshot = {
            "model_sha256": "fixture", "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
            "components": {"C1": carrier("AN-S-010@1", left, parent="C00"),
                           "C2": carrier("AN-S-011@1", right, parent="C00")},
            "packages": {"pkg1": carrier("AN-S-012@1", {"boundaries": {"state": "pure"}}, component="C2"),
                         "pkg2": carrier("AN-S-013@1", {"boundaries": {"state": "local"}}, component="C2")},
        }
        structure = self._source(".anechoic_tmp/generation/structure.json", json.dumps(snapshot))
        gateway = await self._gateway(structure_snapshot=structure)

        async def query(sql):
            result = await gateway.call(None, types.CallToolRequestParams(name="query_run", arguments={
                "sql": sql, "result_delivery": "inline",
            }))
            self.assertFalse(result.is_error, result.structured_content)
            return result.structured_content["rows"]

        schema = await gateway.call(None, types.CallToolRequestParams(name="query_schema", arguments={}))
        self.assertTrue({"boundary_declarations", "code_access_findings"} <= schema.structured_content["tables"].keys())
        declarations = await query("""
            SELECT owner_id, node_key, layer, json_extract_string(state, '$'),
                   json_extract_string(io, '$.client[0].interface'),
                   json_extract_string(io, '$.server.run.transport')
            FROM boundary_declarations ORDER BY owner_id
        """)
        self.assertEqual([
            ["C1", "C1", 2, "local", "run", None], ["C2", "C2", 1, None, None, "cli"],
            ["pkg1", "package:local:src/RIGHT_C2/service_pkg1", None, "pure", None, None],
            ["pkg2", None, None, "local", None, None],
        ], declarations)
        findings_sql = "SELECT written_specifier, reason FROM code_access_findings ORDER BY written_specifier"
        self.assertEqual([["from RIGHT_C2.api import hidden", "code access rule"]], await query(findings_sql))

        right["layer"] = 3
        pending = self._source(".anechoic_tmp/generation/structure.pending", json.dumps(snapshot))
        pending.replace(structure)
        expected = [[f"from RIGHT_C2.api import {name}", "sibling layer order"] for name in ("exposed", "hidden")]
        async with asyncio.timeout(6):
            while await query(findings_sql) != expected:
                await asyncio.sleep(.03)
        rebuild = await gateway.call(None, types.CallToolRequestParams(
            name="query_rebuild", arguments={"target": "boundary_declarations"}))
        self.assertFalse(rebuild.is_error, rebuild.structured_content)
        self.assertEqual(expected, await query(findings_sql))
        await gateway.close()
        disabled = await self._gateway(enabled=False, structure_snapshot=structure)
        schema = await disabled.call(None, types.CallToolRequestParams(name="query_schema", arguments={}))
        self.assertTrue({"boundary_declarations", "code_access_findings"}.isdisjoint(schema.structured_content["tables"]))

    async def test_direct_packages_follow_unsupported_source_removal(self):
        source = self._source("src/tree/nested/leaf/main.go", "package leaf\n")
        self._source("src/tree/assets/image.txt", "asset\n")
        self._source("src/tree/tree__tests/assets/input.txt", "asset\n")
        self._source("src/tree/.hidden/hidden.go", "package hidden\n")
        self._source("src/tree/generated/generated.go", "package generated\n")
        self._source("src/tree/ignored/ignored.go", "package ignored\n")
        self._source(".gitignore", "src/tree/ignored/\n")
        (self.root / "src/tree/empty").mkdir()
        gateway = await self._gateway()

        async def rows(owner, sql):
            response = await owner.call(None, types.CallToolRequestParams(name="query_run", arguments={
                "sql": sql, "result_delivery": "inline",
            }))
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"]

        packages = """
            SELECT n.node_key, count(a.relative_path)
            FROM import_nodes n LEFT JOIN package_audit a ON a.relative_path = n.relative_path
            WHERE n.kind = 'package' AND n.relative_path LIKE 'src/tree%'
            GROUP BY n.node_key ORDER BY n.node_key
        """
        expected = [["package:local:src/tree/nested/leaf", 1]]
        self.assertEqual(expected, await rows(gateway, packages))
        self.assertEqual([["src/tree/nested/leaf/main.go", "unsupported"]], await rows(gateway, """
            SELECT relative_path, scan_status FROM import_nodes
            WHERE kind = 'module' AND relative_path LIKE 'src/tree%' ORDER BY relative_path
        """))
        source.unlink()
        async with asyncio.timeout(6):
            while await rows(gateway, packages):
                await asyncio.sleep(.03)
        await gateway.close()
        reopened = await self._gateway()
        self.assertEqual([], await rows(reopened, packages))
        source.write_text("package leaf\n", encoding="utf-8")
        async with asyncio.timeout(6):
            while await rows(reopened, packages) != expected:
                await asyncio.sleep(.03)

    async def test_component_test_package_and_unmarked_package(self):
        self._source("src/UNIT_C1/UNIT_C1__tests/test_e2e.py", "pass\n")
        implementation = self._source("src/UNIT_C1/service_pkg1/main.py", "pass\n")
        self._source("src/UNIT_C1/service_pkg1/service_pkg1__tests/test_main.py", "pass\n")
        self._source("src/group/group__tests/test_e2e.py", "pass\n")
        structure = self._source(".anechoic_tmp/structure.json", json.dumps({
            "model_sha256": "fixture", "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
            "components": {"C1": {"parent": "C00", "ref": "AN-S-006@1", "sha256": "fixture",
                                  "source_path": "AN-S-006-SPEC-COMPONENT_MANIFEST--unit.md",
                                  "fields": {"name": "Unit"}}},
        }))
        gateway = await self._gateway(structure_snapshot=structure)

        async def rows(sql):
            response = await gateway.call(None, types.CallToolRequestParams(name="query_run", arguments={
                "sql": sql, "result_delivery": "inline",
            }))
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"]

        self.assertEqual([["src/UNIT_C1/UNIT_C1__tests"], ["src/UNIT_C1/service_pkg1"],
                          ["src/UNIT_C1/service_pkg1/service_pkg1__tests"]],
                         await rows("SELECT relative_path FROM import_nodes WHERE kind = 'package' "
                                    "AND relative_path LIKE 'src/UNIT_C1%' ORDER BY relative_path"))
        self.assertEqual([
            ["package:local:src/UNIT_C1/UNIT_C1__tests", "C1"],
            ["package:local:src/UNIT_C1/service_pkg1/service_pkg1__tests",
             "package:local:src/UNIT_C1/service_pkg1"],
        ], await rows("SELECT source_key, target_key FROM test_edges ORDER BY source_key"))
        self.assertEqual([["Component", "C1"]], await rows("""
            FROM GRAPH_TABLE (anechoic
                MATCH (test:ImportNode)-[edge:TESTS_COMPONENT]->(component:Reference)
                COLUMNS (component.kind AS kind, component.ref AS ref))
        """))
        inverse = """
            FROM GRAPH_TABLE (anechoic
                MATCH (component:Reference)-[edge:COMPONENT_IS_TESTED_BY]->(test:ImportNode)
                COLUMNS (component.ref AS component, test.relative_path AS test_path))
        """
        expected = [["C1", "src/UNIT_C1/UNIT_C1__tests"]]
        self.assertEqual(expected, await rows(inverse))
        issues = "SELECT relative_path, test_issue FROM package_audit WHERE test_issue IS NOT NULL ORDER BY relative_path"
        orphan = ["src/group/group__tests", "missing_test_target"]
        self.assertEqual([["src/UNIT_C1/service_pkg1", "missing_visibility_marker"], orphan], await rows(issues))
        implementation.rename(implementation.with_name("main__shared.py"))
        async with asyncio.timeout(6):
            while await rows(issues) != [orphan]:
                await asyncio.sleep(.03)
        await gateway.close()
        gateway = await self._gateway(structure_snapshot=structure)
        self.assertEqual(expected, await rows(inverse))
        self.assertEqual([orphan], await rows(issues))

    async def test_import_publication_failure_reports_stderr_once(self):
        self._source("src/from_source.py", "import to_source\n")
        self._source("src/to_source.py", "")
        gateway = await self._gateway()
        stderr = StringIO()
        with redirect_stderr(stderr), patch("native_query.replace_imports", side_effect=ValueError("fixture write")) as write:
            self._source("src/new_source.py", "")
            async with asyncio.timeout(6):
                while "fixture write" not in stderr.getvalue():
                    await asyncio.sleep(.03)
            self.assertEqual(write.call_count, 1)
        store = gateway._native_query._owner()
        duplicate = ("duplicate", "module", "python", "new.py", "ok", None)
        with self.assertRaises(duckdb.ConstraintException):
            publish_imports(store, [duplicate, duplicate], [], [])
        with store._lock:
            self.assertEqual(store._connection.execute(
                "SELECT relative_path FROM import_nodes ORDER BY relative_path",
            ).fetchall(), [("src",), ("src/from_source.py",), ("src/to_source.py",)])

    async def test_disk_reopen_rebuild_and_test_relations(self):
        self._source("src/app/main.py", "import dep.helper\n")
        self._source("src/dep/helper.py", "")
        test_directory = self._source("src/app/app__tests/test_app.py", "pass\n").parent
        gateway = await self._gateway()
        owner = gateway._native_query
        store = owner._owner()
        database = self.root / ".anechoic_runtime/workbench/projection.duckdb"
        self.assertTrue(database.is_file())
        sql = """
            SELECT parent.relative_path, test.relative_path, test.package_type
            FROM tested_by_edges e JOIN import_nodes parent ON parent.node_key = e.source_key
            JOIN import_nodes test ON test.node_key = e.target_key
        """
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                     base_url="http://127.0.0.1:18093") as client:
            base = "/anechoic/Anechoic/api"

            async def post(operation, arguments, status=200):
                response = await client.post(f"{base}/{operation}", json=arguments)
                self.assertEqual(status, response.status_code, response.text)
                return response.json()

            async def view_call(operation, arguments):
                return await post("interface", {"operation": operation, "arguments": arguments})

            workspace = await view_call("workspace_open", {"session_id": "realization"})
            view = {"workspace_id": workspace["workspace_id"], "view_id": workspace["active_view_id"]}
            await view_call("view_update", view | {"sql": sql, "expected_revision": 0})
            first = (await view_call("view_run", view))["query_id"]
            independent = (await post("run", {"sql": "SELECT 7", "result_delivery": "inline"}))["query_id"]
            expected = [["src/app", "src/app/app__tests", "Test Package"]]
            self.assertEqual(expected, (await view_call("view_fetch", view | {"result_delivery": "inline"}))["rows"])
            with store._lock:
                database_file = store._connection.execute(
                    "SELECT path FROM duckdb_databases() WHERE NOT internal"
                ).fetchone()[0]
                self.assertEqual(database.resolve().as_posix(), database_file)
            stderr = StringIO()
            with redirect_stderr(stderr):
                rejected = await post("rebuild", {"target": "unknown"}, 400)
            self.assertIn("Unknown Workbench rebuild target", rejected["error"])
            self.assertIn("Unknown Workbench rebuild target", stderr.getvalue())
            with redirect_stderr(StringIO()) as errors:
                response = await gateway.call(None, types.CallToolRequestParams(
                    name="query_rebuild", arguments={"target": "missing"},
                ))
            self.assertTrue(response.is_error)
            self.assertIn("Unknown Workbench rebuild target", str(response.structured_content))
            self.assertIn("Unknown Workbench rebuild target", errors.getvalue())
            moved = test_directory.parent.parent / test_directory.name
            test_directory.rename(moved)
            rebuilt = await post("rebuild", {"target": "test_edges"})
            second = rebuilt["result_ids"][first]
            self.assertNotEqual(first, second)
            self.assertNotIn(independent, rebuilt["result_ids"])
            fetched = await view_call("view_fetch", view | {"result_delivery": "inline"})
            self.assertEqual((second, []), (fetched["query_id"], fetched["rows"]))
            self.assertTrue(store._results[second].pinned)
            stderr = StringIO()
            with redirect_stderr(stderr), patch.object(store, "prepare_result_rebuild",
                                                       side_effect=ValueError("fixture rebuild failure")):
                await post("rebuild", {"target": "test_edges"}, 400)
            self.assertIn("fixture rebuild failure", stderr.getvalue())
            fetched = await view_call("view_fetch", view | {"result_delivery": "inline"})
            self.assertEqual((second, []), (fetched["query_id"], fetched["rows"]))
            moved.rename(test_directory)
            mcp = await gateway.call(None, types.CallToolRequestParams(
                name="query_rebuild", arguments={"target": "all"},
            ))
            self.assertFalse(mcp.is_error, mcp.structured_content)
            third = mcp.structured_content["result_ids"][second]
            fetched = await view_call("view_fetch", view | {"result_delivery": "inline"})
            self.assertEqual((third, expected), (fetched["query_id"], fetched["rows"]))
            single = await post("rebuild", {"target": f"workbench_results.query_{third}"})
            self.assertIn(third, single["result_ids"])

        await gateway.close()
        self._source("src/dep/helper.py", "import app.main\n")
        from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61 import source
        with patch.object(source, "_parse", wraps=source._parse) as parse:
            reopened = await self._gateway()
            self.assertEqual(["src/dep/helper.py"], [call.args[0] for call in parse.call_args_list])
        reopened_store = reopened._native_query._owner()
        self.assertFalse(reopened_store._results)
        with reopened_store._lock:
            self.assertEqual([(2,)], reopened_store._connection.execute("SELECT count(*) FROM module_imports").fetchall())
            self.assertEqual([], reopened_store._connection.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workbench_results'"
            ).fetchall())
        await reopened.close()
        disabled = await self._gateway(enabled=False)
        self.assertNotIn("test_edges", disabled._native_query.schema()["tables"])
        disabled_store = disabled._native_query._owner()
        with disabled_store._lock:
            self.assertFalse(read_import_sources(disabled_store._connection))

    async def test_read_issue_is_queryable_and_clears_on_the_next_scan(self):
        source = self._source("src/app/main.py", "import os\n")
        read_bytes = Path.read_bytes

        def read(path):
            if path == source:
                raise PermissionError("fixture read denied")
            return read_bytes(path)

        with patch.object(Path, "read_bytes", read), redirect_stderr(StringIO()) as errors:
            gateway = await self._gateway()
        self.assertIn("fixture read denied", errors.getvalue())
        sql = "SELECT relative_path, error_message FROM import_read_issues"
        owner = gateway._native_query
        self.assertIn("import_read_issues", owner.schema()["tables"])
        self.assertEqual([["src/app/main.py", "fixture read denied"]],
                         owner.run(sql, result_delivery="inline")["rows"])
        owner.rebuild("import_read_issues")
        self.assertEqual([], owner.run(sql, result_delivery="inline")["rows"])

    async def test_graph_rebuild_failure_disables_queries_at_the_public_boundary(self):
        self._source("src/main.py", "")
        gateway = await self._gateway()
        owner = gateway._native_query
        store = owner._owner()
        async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=Starlette(routes=routes(gateway))),
                                     base_url="http://127.0.0.1:18093") as client:
            stderr = StringIO()
            with redirect_stderr(stderr), patch(
                "APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store.insert_rows",
                side_effect=OSError("fixture atom insert blocked"),
            ):
                failure = await client.post("/anechoic/Anechoic/api/rebuild", json={"target": "atoms"})
            self.assertEqual(400, failure.status_code)
            self.assertIn("restart required", failure.json()["error"])
            self.assertIn("fixture atom insert blocked", stderr.getvalue())
            response = await gateway.call(None, types.CallToolRequestParams(
                name="query_run", arguments={"sql": "SELECT count(*) FROM atoms"},
            ))
            self.assertTrue(response.is_error)
            self.assertIn("restart required", str(response.structured_content))
        with store._lock:
            self.assertGreater(store._connection.execute("SELECT count(*) FROM atoms").fetchone()[0], 0)
