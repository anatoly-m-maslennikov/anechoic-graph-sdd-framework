"""Exercise the Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from io import StringIO
import json

from mcp import types

from . import test_native_query_stdio as fixture


class ImportGraphCases3:
    async def test_manifest_previous_image_import_is_scoped_to_source(self):
        from .native_query_test_support import create_native_gateway

        self._source("src/app/client.py", "import old_image.runtime\n")
        self._source("src/app/other.py", "import old_image.runtime\n")
        manifest = self.root / fixture.CONTROL / fixture.MANIFEST
        text = manifest.read_text(encoding="utf-8")
        text = text.replace(
            'ProjectManifest(name="Anechoic", prefix="AN")',
            'ProjectManifest(name="Anechoic", prefix="AN", parameters={"runtime": {"workbench": '
            '{"import_graph": {"python_roots": ["src"], "python_image_imports": '
            '{"src/app/client.py": ["old_image.runtime"]}}}}})',
        )
        manifest.write_text(text, encoding="utf-8")
        gateway = create_native_gateway(self.root, fixture.CONTROL, fixture._native_inputs())
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)

        response = await gateway.call(None, types.CallToolRequestParams(name="query_run", arguments={
            "sql": "SELECT i.source_key, i.resolution_status, i.target_key, n.scan_status "
                   "FROM module_imports i LEFT JOIN import_nodes n ON n.node_key = i.target_key "
                   "WHERE i.written_specifier = 'old_image.runtime' ORDER BY i.source_key",
            "result_delivery": "inline",
        }))
        self.assertFalse(response.is_error, response.structured_content)
        self.assertEqual([
            ["module:src/app/client.py", "external", "module:external:previous-image:old_image.runtime",
             "declared_previous_image"],
            ["module:src/app/other.py", "unresolved", None, None],
        ], response.structured_content["rows"])

    async def _prepare_package_audit(self):
        package = "src/UNIT_C1/service_CS1"
        self._source("src/UNIT_C1/__init__.py", "")
        marker = self._source(f"{package}/main__public.py", "pass\n")
        self._source(f"{package}/child/main__shared.py", "pass\n")
        self._source(f"{package}/service_CS1__tests/test_main.py", "pass\n")
        control = f"{fixture.CONTROL}/UNIT_C1"
        spec_source = (
            "---\natom_family: SPEC\natom_id: AN-S-007\ncontainer: {component: C1}\ntier: 2\n"
            "context: {lens: SPEC, template: component_seed_manifest}\n"
            "state: {status: active, version: 2, updated_at: '2026-11-22T09:00:00+00:00'}\n---\n"
            "## Formal Manifest\n\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ComponentSeedManifest\n"
            'declare_entity(entity_name="Component Seed Manifest", '
            'instance=ComponentSeedManifest(component_seed_id="CS1"))\n```\n\n'
            "## Purpose\n\nProvide a service.\n\n## Solution\n\nAccept a request.\n"
        )
        spec = self._source(f"{control}/AN-S-007-SPEC-COMPONENT_SEED_MANIFEST--service.md", spec_source)
        self._source(f"{control}/099_archived/AN-S-007@1-SPEC-COMPONENT_SEED_MANIFEST--service.md",
                     spec_source.replace("active, version: 2", "archived, version: 1"))
        sidecar = self._source(
            f"{package}/service_CS1__spec_bind.yaml",
            "implements: [AN-S-007@1, AN-S-999@1]\napplies: [AN-S-007@2]\n",
        )
        structure = self._source(".anechoic_tmp/structure.json", json.dumps({
            "model_sha256": "fixture", "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
            "components": {"C1": {"parent": "C00", "ref": "AN-S-006@1", "sha256": "fixture",
                                  "source_path": "AN-S-006-SPEC-COMPONENT_MANIFEST--unit.md",
                                  "fields": {"name": "Unit"}}},
        }))
        gateway = await self._gateway(structure_snapshot=structure)

        return package, marker, spec_source, spec, sidecar, structure, gateway

    async def _package_audit(self, owner, path):
        response = await owner.call(None, types.CallToolRequestParams(name="query_run", arguments={
            "sql": "SELECT has_internal, has_public, has_spec_bind, binding_status, "
                   "all_pins_active, list_sort(json_extract_string(pin_issues, '$[*].reason')), "
                   "contract_ref, contract_covered FROM package_audit "
                   f"WHERE relative_path = '{path}'",
            "result_delivery": "inline",
        }))
        self.assertFalse(response.is_error, response.structured_content)
        return response.structured_content["rows"][0]

    async def _expect_package_audit(self, audit, expected):
        async with asyncio.timeout(6):
            while await audit() != expected:
                await asyncio.sleep(.03)

    async def test_package_audit_tracks_exact_pins_and_contracts(self):
        package, marker, spec_source, spec, sidecar, structure, gateway = await self._prepare_package_audit()

        async def audit(owner=gateway, path=package):
            return await self._package_audit(owner, path)

        async def expect_audit(expected):
            await self._expect_package_audit(audit, expected)

        schema = await gateway.call(None, types.CallToolRequestParams(name="query_schema", arguments={}))
        self.assertIn("package_audit", schema.structured_content["tables"])
        self.assertEqual([False, True, True, "valid", False, ["archived", "missing"], "AN-S-007@2", False],
                         await audit())
        self.assertEqual([False, False, False, "missing", None, [], None, None],
                         await audit(path=f"{package}/service_CS1__tests"))
        sidecar.write_text("{}\n", encoding="utf-8")
        await expect_audit([False, True, True, "empty", None, [], "AN-S-007@2", False])
        sidecar.write_text("implements: not-a-list\n", encoding="utf-8")
        await expect_audit([False, True, True, "invalid", None, [], "AN-S-007@2", False])
        self._source(f"{package}/service_CS1.p.spec_trace.md", "## Implements\n- AN-S-007@2\n")
        sidecar.unlink()
        await expect_audit([False, True, False, "missing", None, [], "AN-S-007@2", False])
        sidecar.write_text("implements: [AN-S-007@2]\n", encoding="utf-8")
        marker.rename(marker.with_name("main__shared.py"))
        await expect_audit([True, False, True, "valid", True, [], "AN-S-007@2", True])
        updated_spec = spec_source.replace("version: 2", "version: 3")
        spec.write_text(updated_spec, encoding="utf-8")
        expected = [True, False, True, "valid", False, ["missing"], "AN-S-007@3", False]
        await expect_audit(expected)
        stderr = StringIO()
        with redirect_stderr(stderr):
            spec.write_text(updated_spec.replace("Accept a request.", ""), encoding="utf-8")
            await expect_audit(expected[:-2] + [None, None])
        self.assertIn("Invalid Component Seed Manifest", stderr.getvalue())
        spec.write_text(updated_spec, encoding="utf-8")
        await expect_audit(expected)
        rebuild = await gateway.call(None, types.CallToolRequestParams(
            name="query_rebuild", arguments={"target": "package_audit"}))
        self.assertFalse(rebuild.is_error, rebuild.structured_content)
        self.assertEqual(expected, await audit())
        await gateway.close()
        reopened = await self._gateway(structure_snapshot=structure)
        self.assertEqual(expected, await audit(owner=reopened))


    async def _prepare_boundaries(self):
        self._source("src/_bypass__shared.py", "")
        self._source("src/LEFT_C1/_package__shared.py", "")
        self._source("src/RIGHT_C2/_package__shared.py", "")
        self._source("src/LEFT_C1/client.py", "from RIGHT_C2.api import exposed, hidden\n")
        self._source("src/RIGHT_C2/api.py", "exposed = 1\nhidden = 2\n")
        self._source("src/RIGHT_C2/service_CS1/main__shared.py", "pass\n")

        def carrier(ref, fields, **relations):
            return {"ref": ref, "sha256": "fixture", "source_path": "manifest.md",
                    "fields": fields, **relations}

        left = {"name": "Left", "layer": 2, "boundaries": {
            "code": {"imports": ["RIGHT_C2.api.exposed"]},
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
            "packages": {"CS1": carrier("AN-S-012@1", {"boundaries": {"state": "pure"}}, component="C2"),
                         "CS2": carrier("AN-S-013@1", {"boundaries": {"state": "local"}}, component="C2")},
        }
        structure = self._source(".anechoic_tmp/generation/structure.json", json.dumps(snapshot))
        gateway = await self._gateway(structure_snapshot=structure)

        return right, snapshot, structure, gateway

    async def test_boundaries_follow_structure_and_named_imports(self):
        right, snapshot, structure, gateway = await self._prepare_boundaries()

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
            ["CS1", "package:local:src/RIGHT_C2/service_CS1", None, "pure", None, None],
            ["CS2", None, None, "local", None, None],
        ], declarations)
        findings_sql = "SELECT written_specifier, status, reason FROM code_access_findings ORDER BY written_specifier"
        self.assertEqual([
            ["from RIGHT_C2.api import exposed", "declared_bypass", "exact import and export declarations"],
            ["from RIGHT_C2.api import hidden", "denied", "code access rule"],
        ], await query(findings_sql))

        right["layer"] = 3
        pending = self._source(".anechoic_tmp/generation/structure.pending", json.dumps(snapshot))
        pending.replace(structure)
        expected = [[f"from RIGHT_C2.api import {name}", "denied", "sibling layer order"]
                    for name in ("exposed", "hidden")]
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


    async def test_native_projection_revision_and_containment_facts_through_mcp(self):
        self._write('001_TICKETS/ASSETS/AN-T-010-ASSET--child.md', 'AN-T-010', 'active', 1,
                    container={'atom': 'AN-T-009'})
        gateway = await self._gateway(enabled=False)

        async def rows(sql):
            response = await gateway.call(None, types.CallToolRequestParams(
                name='query_run', arguments={'sql': sql, 'result_delivery': 'inline'},
            ))
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content['rows']

        refs = await rows("SELECT stable_ref, exact_ref FROM native_references "
                          "WHERE exact_ref LIKE 'AN-T-009@%' ORDER BY exact_ref")
        self.assertEqual([[None, 'AN-T-009@1'], ['AN-T-009', 'AN-T-009@2'],
                          [None, 'AN-T-009@3-draft']], refs)
        facts = await rows("SELECT source_kind, source_ref, target_kind, target_ref, relation_type, derived "
                           "FROM relations WHERE (source_ref = 'AN-T-010' AND target_ref = 'AN-T-009') "
                           "OR (source_ref = 'AN-T-009' AND target_ref = 'AN-T-010') "
                           "OR (source_kind = 'Component' AND source_ref = 'C0' "
                           "AND target_ref = 'AN-T-009')")
        self.assertIn(['Atom', 'AN-T-010', 'Atom', 'AN-T-009', 'CONTAINED_BY', False], facts)
        self.assertIn(['Atom', 'AN-T-009', 'Atom', 'AN-T-010', 'CONTAINS', True], facts)
        self.assertIn(['Component', 'C0', 'Atom', 'AN-T-009', 'CONTAINS', True], facts)
        self.assertEqual([], await rows('SELECT * FROM scope_units'))
