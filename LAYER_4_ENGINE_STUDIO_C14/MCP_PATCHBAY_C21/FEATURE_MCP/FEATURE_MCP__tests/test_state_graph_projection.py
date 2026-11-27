"""Check native gateway publication and refresh of state findings."""

import shutil
from unittest import IsolatedAsyncioTestCase, skipUnless
from unittest.mock import patch


class StateProjectionWatcherTests(IsolatedAsyncioTestCase):
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.test_native_import_graph import NativeImportGraphTests as Fixture

    _write = Fixture._write
    _source = Fixture._source
    _gateway = Fixture._gateway
    _prepare_boundaries = Fixture._prepare_boundaries
    setUp = Fixture.setUp
    del Fixture

    @skipUnless(
        shutil.which("lean"), "Lean is required for the state graph canary"
    )
    async def test_graph_publishes_lean_evidence_and_lint_findings(self):
        from mcp import types

        self._source(
            "src/effects.py",
            "from contextvars import ContextVar\n"
            "CHANNEL = ContextVar('REQUEST_CTX')\n"
            "def action(write: bool):\n"
            "    if write:\n"
            "        CHANNEL.set(1)\n"
            "# anechoic: no-op\n"
            "def declared():\n"
            "    pass\n",
        )
        gateway = await self._gateway()
        result = await gateway.call(
            None,
            types.CallToolRequestParams(
                name="query_run",
                arguments={
                    "sql": "SELECT * FROM state_effect_findings WHERE relative_path = 'src/effects.py' "
                    "ORDER BY action, status",
                    "result_delivery": "inline",
                    "result_format": "json_matrix",
                },
            ),
        )
        self.assertFalse(result.is_error, result.structured_content)
        rows = result.structured_content["rows"]
        self.assertEqual(
            [
                ("action", "deadEnd"),
                ("action", "hasEffects"),
                ("declared", "declaredNoOp"),
            ],
            [(row[3], row[6]) for row in rows],
        )

    @skipUnless(
        shutil.which("lean"), "Lean is required for the state graph canary"
    )
    async def test_named_grant_refresh_clears_denied_read(self):
        import asyncio
        import json
        from mcp import types

        self._source(
            "src/RIGHT_C2/effects.py",
            "from contextvars import ContextVar\n"
            "CHANNEL = ContextVar('REQUEST_CTX', default=None)\n"
            "def action():\n"
            "    return CHANNEL.get()\n",
        )
        right, snapshot, structure, gateway = await self._prepare_boundaries()

        async def count():
            result = await gateway.call(
                None,
                types.CallToolRequestParams(
                    name="query_run",
                    arguments={
                        "sql": "SELECT json_array_length(violations) FROM state_effect_findings "
                        "WHERE relative_path = 'src/RIGHT_C2/effects.py' AND action = 'action'",
                        "result_delivery": "inline",
                    },
                ),
            )
            self.assertFalse(result.is_error, result.structured_content)
            return result.structured_content["rows"]

        self.assertEqual([[1]], await count())
        right["boundaries"]["state"] = {
            "mode": "local",
            "channels": {"REQUEST_CTX": "r"},
        }
        stage = self._source(
            ".anechoic_tmp/generation/structure.pending", json.dumps(snapshot)
        )
        stage.replace(structure)
        async with asyncio.timeout(30):
            while await count() != [[0]]:
                await asyncio.sleep(0.1)

    async def test_unavailable_lean_is_published(self):
        from mcp import types

        self._source("src/a.py", "x = 1\n")
        with patch(
            (
                'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.stat'
                'e_effects.shutil.which'
            ),
            return_value=None,
        ):
            gateway = await self._gateway()
            result = await gateway.call(
                None,
                types.CallToolRequestParams(
                    name="query_run",
                    arguments={
                        "sql": (
                            'SELECT source_key, status, detail FROM '
                            'state_effect_findings WHERE relative_path = '
                            "'src/a.py'"
                        ),
                        "result_delivery": "inline",
                    },
                ),
            )
        self.assertFalse(result.is_error, result.structured_content)
        self.assertEqual(
            [
                [
                    "module:src/a.py",
                    "unresolved",
                    "Lean executable unavailable on PATH",
                ]
            ],
            result.structured_content["rows"],
        )

    async def test_source_change_rebuild_and_disabled_projection(self):
        import asyncio
        from mcp import types

        source = self._source('src/a.py', 'x = 1\n')

        def analyze(root, sources, ownership=None):
            return [
                (
                    f"module:{path}",
                    path,
                    item.language,
                    "<module>",
                    1,
                    None,
                    "unresolved",
                    False,
                    "[]",
                    "[]",
                    item.signature,
                )
                for path, item in sources.items()
                if path == "src/a.py"
            ]

        with patch('KERNEL_MIXER_C59.boundary_tables.analyze_state', side_effect=analyze):
            gateway = await self._gateway()

            async def rows():
                response = await gateway.call(None, types.CallToolRequestParams(name='query_run', arguments={
                    'sql': 'SELECT detail FROM state_effect_findings', 'result_delivery': 'inline',
                }))
                self.assertFalse(response.is_error, response.structured_content)
                return response.structured_content['rows']

            original = await rows()
            self.assertEqual(1, len(original))
            source.write_text('x = 2\n', encoding='utf-8')
            async with asyncio.timeout(6):
                while await rows() == original:
                    await asyncio.sleep(.03)
            changed = await rows()
            result = await gateway.call(None, types.CallToolRequestParams(
                name='query_rebuild', arguments={'target': 'state_effect_findings'}))
            self.assertFalse(result.is_error, result.structured_content)
            self.assertEqual(changed, await rows())
            await gateway.close()
            disabled = await self._gateway(enabled=False)
            schema = await disabled.call(None, types.CallToolRequestParams(name='query_schema', arguments={}))
            self.assertNotIn('state_effect_findings', schema.structured_content['tables'])
