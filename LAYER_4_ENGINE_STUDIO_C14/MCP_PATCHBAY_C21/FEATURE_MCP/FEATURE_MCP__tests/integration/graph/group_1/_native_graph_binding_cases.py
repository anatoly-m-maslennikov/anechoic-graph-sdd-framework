"""Exercise the Import Graph through the native Workbench routes."""

import asyncio
from contextlib import redirect_stderr
from io import StringIO
import json
from unittest.mock import patch

import httpx2
from mcp import types
from starlette.applications import Starlette

from ...query.group_1 import test_native_query_stdio as fixture
from ....native_query_test_support import create_native_gateway
from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
    routes as routes,
)


class NativeGraphBindingCases:
    async def test_spec_bindings_are_indexed_and_follow_sidecar_changes(self):
        self._source("src/app/main.py", "pass\n")
        sidecar = self._source(
            "src/app/app__spec_bind.yaml", "implements:\n  - AN-S-001@1\n"
        )
        self._source(
            "src/app/main.py.spec_trace.md", "## Implements\n- AN-S-10@2\n"
        )
        gateway = await self._gateway()
        app = Starlette(routes=routes(gateway))
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app),
            base_url="http://127.0.0.1:18093",
        ) as client:
            base = "/anechoic/Anechoic/api"
            schema = await client.post(f"{base}/schema", json={})
            self.assertEqual(schema.status_code, 200, schema.text)
            self.assertIn("implementation_rmedo", schema.json()["tables"])

            async def pins():
                result = await client.post(
                    f"{base}/run",
                    json={
                        "sql": (
                            'SELECT owner_path, entry_kin'
                            'd, atom_id, version FROM imp'
                            'lementation_rmedo ORDER BY 1'
                        ),
                        "result_delivery": "inline",
                    },
                )
                self.assertEqual(result.status_code, 200, result.text)
                return result.json()["rows"]

            module = ["src/app/main.py", "implements", "AN-S-10", 2]
            self.assertEqual(
                await pins(),
                [["src/app", "implements", "AN-S-001", 1], module],
            )
            sidecar.write_text("applies:\n  - AN-S-007@3\n", encoding="utf-8")
            async with asyncio.timeout(6):
                while await pins() != [
                    ["src/app", "applies", "AN-S-007", 3],
                    module,
                ]:
                    await asyncio.sleep(0.03)
            sidecar.unlink()
            async with asyncio.timeout(6):
                while await pins() != [module]:
                    await asyncio.sleep(0.03)

    def _prepare_sidecars(self):
        self._source("src/app/main.py", "pass\n")
        self._source("src/other/other.py", "pass\n")
        sidecar = self._source(
            "src/app/app__spec_bind.yaml", "implements: [AN-S-001@1]\n"
        )
        other_sidecar = self._source(
            "src/other/other__spec_bind.yaml", "implements: [AN-S-001@1]\n"
        )
        module_sidecar = self._source(
            "src/app/main.py.spec_trace.md", "## Implements\n- AN-S-10@2\n"
        )
        gateway = create_native_gateway(
            self.root, fixture.CONTROL, fixture._native_inputs()
        )
        owner = gateway._native_query
        owner.start()
        self.addCleanup(owner.close)
        store = owner._owner()

        return owner, store, sidecar, other_sidecar, module_sidecar

    def _check_trace_rollback(self, owner, store, snapshot):
        before = snapshot()
        replacement = [
            (
                "src/app",
                "src/app/app__spec_bind.yaml",
                "implements",
                "AN-S-001",
                1,
            )
        ]
        with (
            patch(
                (
                    'KERNEL_MIXER_C59.native_quer'
                    'y_projection.native_trace_sn'
                    'apshot'
                ),
                return_value=(replacement, {"src/app": "valid"}),
            ),
            patch(
                (
                    'KERNEL_MIXER_C59.native_quer'
                    'y_projection.replace_package'
                    '_audit'
                ),
                side_effect=RuntimeError("audit failed"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "audit failed"):
                owner._refresh_traces(store, {"src/app/app__spec_bind.yaml"})
        self.assertEqual(before, snapshot())

    def _trace_snapshot(self, store):
        with store._lock:
            pins = store._connection.execute(
                (
                    'SELECT owner_path, entry_kin'
                    'd, atom_id, version FROM imp'
                    'lementation_rmedo ORDER BY 1'
                )
            ).fetchall()
            states = dict(
                store._connection.execute(
                    "SELECT relative_path, binding_status FROM package_audit"
                ).fetchall()
            )
        return pins, states

    async def test_sidecar_only_refresh_reads_only_affected_owner_and_updates_audit(
        self,
    ):
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.\
            FEATURE_IMPORT_GRAPH_C61.import_graph__shared import (
            _read_pins,
        )

        owner, store, sidecar, other_sidecar, module_sidecar = (
            self._prepare_sidecars()
        )

        def snapshot():
            return self._trace_snapshot(store)

        other = ("src/other", "implements", "AN-S-001", 1)
        module = ("src/app/main.py", "implements", "AN-S-10", 2)
        with (
            patch(
                (
                    'IWE_CONSOLE_C43.APP_IWE_CONS'
                    'OLE.FEATURE_IMPORT_GRAPH_C61'
                    '.trace_bindings._read_pins'
                ),
                wraps=_read_pins,
            ) as reads,
            patch.object(
                owner, "_prepare_realization", wraps=owner._prepare_realization
            ) as prepare,
        ):
            expect = self._sidecar_expectation(
                snapshot, lambda: (module, other)
            )

            fallback = await self._change_sidecar(sidecar, expect)
            module = ("src/app/main.py", "implements", "AN-S-11", 3)
            module_sidecar.write_text("## Implements\n- AN-S-11@3\n")
            await expect(None, "missing")
            sidecar.write_text("applies: [AN-S-001@1]\n")
            await expect(("src/app", "applies", "AN-S-001", 1), "valid")
            self.assertNotIn(
                other_sidecar, {call.args[2] for call in reads.call_args_list}
            )
            other = ("src/other", "applies", "AN-S-001", 1)
            sidecar.replace(other_sidecar)
            await expect(None, "missing")
            self.assertTrue(reads.call_count)
            self.assertEqual(
                {sidecar, other_sidecar, fallback, module_sidecar},
                {call.args[2] for call in reads.call_args_list},
            )
            prepare.assert_not_called()
        self._check_trace_rollback(owner, store, snapshot)

    async def _change_sidecar(self, sidecar, expect):
        sidecar.write_text("applies: [AN-S-001@1]\n")
        await expect(("src/app", "applies", "AN-S-001", 1), "valid")
        stderr = StringIO()
        with redirect_stderr(stderr):
            sidecar.write_text("implements: invalid\n")
            await expect(None, "invalid")
        self.assertIn("Invalid spec trace", stderr.getvalue())
        fallback = self._source(
            "src/app/app.p.spec_trace.md", "## Implements\n- AN-S-001@1\n"
        )
        sidecar.unlink()
        await expect(("src/app", "implements", "AN-S-001", 1), "missing")
        fallback.unlink()
        await expect(None, "missing")
        return fallback

    def _sidecar_expectation(self, snapshot, other_pins):
        async def expect(pin, state):
            async with asyncio.timeout(6):
                while True:
                    pins, states = snapshot()
                    if (
                        pins
                        == sorted([row for row in (pin, *other_pins()) if row])
                        and states["src/app"] == state
                    ):
                        return
                    await asyncio.sleep(0.03)

        return expect

    async def test_component_ratios_follow_formal_test_assets(self):
        asset, spec, body, structure = self._component_ratio_fixture()
        gateway = await self._gateway(structure_snapshot=structure)

        async def ratios():
            response = await gateway.call(
                None,
                types.CallToolRequestParams(
                    name="query_run",
                    arguments={
                        "sql": "SELECT denominator, realization_kb, realization_lines, spec_full_kb_ratio, "
                        "spec_body_kb_ratio, spec_body_lines_ratio FROM component_metrics "
                        "WHERE component_id = 'C1' ORDER BY denominator",
                        "result_delivery": "inline",
                    },
                ),
            )
            self.assertFalse(response.is_error, response.structured_content)
            return response.structured_content["rows"]

        expected = self._expected_component_ratios(spec, body)
        self.assertEqual(expected, await ratios())
        asset.unlink()
        async with asyncio.timeout(6):
            while (await ratios())[2] != [
                "test_assets",
                0.0,
                0,
                None,
                None,
                None,
            ]:
                await asyncio.sleep(0.03)

    def _component_ratio_fixture(self):
        self._source("src/UNIT_C1/main.py", "pass\npass\n")
        self._source("src/UNIT_C1/tests/test_legacy.py", "pass\n")
        self._source("src/UNIT_C1/UNIT_C1__tests/test_main.py", "pass\n")
        asset = self._source(
            "src/UNIT_C1/UNIT_C1__tests/assets/input.txt", "x\n"
        )
        body = "## Summary\n\nDescribe C1.\n"
        spec = self._source(
            f"{fixture.CONTROL}/UNIT_C1/AN-S-007-SPEC--description.md",
            (
                "---\nidentity: {atom_id: AN-S-007}\ncontext: {container: {component: C1}, lens: SPEC}\n"
                "state: {status: active, version: 1}\n---\n" + body
            ),
        )
        structure = self._source(
            ".anechoic_tmp/structure.json",
            json.dumps({
                "model_sha256": "fixture",
                "project": {"ref": "AN-S-001@1", "sha256": "fixture"},
                "components": {
                    "C1": {
                        "parent": "C00",
                        "ref": "AN-S-006@1",
                        "sha256": "fixture",
                        "source_path": (
                            'AN-S-006-SPEC-COMPONENT_MANI'
                            'FEST--unit.md'
                        ),
                        "fields": {"name": "Unit"},
                    }
                },
            }),
        )
        return asset, spec, body, structure

    def _expected_component_ratios(self, spec, body):
        populations = {
            "implementation": (10, 2),
            "implementation_and_tests": (17, 4),
            "test_assets": (2, 1),
            "test_code": (5, 1),
            "tests": (7, 2),
        }
        return [
            [
                kind,
                size / 1000,
                lines,
                spec.stat().st_size / size,
                len(body) / size,
                3 / lines,
            ]
            for kind, (size, lines) in sorted(populations.items())
        ]
