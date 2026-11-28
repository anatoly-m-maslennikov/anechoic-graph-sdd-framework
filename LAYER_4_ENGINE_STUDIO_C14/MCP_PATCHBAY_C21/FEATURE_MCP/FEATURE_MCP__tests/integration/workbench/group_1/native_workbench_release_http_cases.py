"""Focused Workbench HTTP contract cases."""


class NativeWorkbenchReleaseHttpCases:
    async def test_rebuild_contract_over_mcp_and_http(self):
        from ..group_3 import test_native_workbench_http as _test_module

        gateway = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        query = await gateway.call(
            None,
            _test_module.types.CallToolRequestParams(
                name="query_run",
                arguments={
                    "sql": "SELECT reference FROM atoms ORDER BY reference",
                    "result_delivery": "inline",
                },
            ),
        )
        self.assertFalse(query.is_error, query.structured_content)
        first = query.structured_content["query_id"]
        result = await gateway.call(
            None,
            _test_module.types.CallToolRequestParams(
                name="query_rebuild", arguments={"target": "all"}
            ),
        )
        self.assertFalse(result.is_error, result.structured_content)
        self.assertEqual(
            ("ready", "all"),
            (
                result.structured_content["status"],
                result.structured_content["target"],
            ),
        )
        second = result.structured_content["result_ids"][first]
        self.assertNotEqual(first, second)
        await self._assert_rebuild_http(gateway, second)

    async def _assert_rebuild_http(self, gateway, second):
        from ..group_3 import test_native_workbench_http as _test_module

        app = _test_module.Starlette(routes=_test_module.routes(gateway))
        async with _test_module.httpx2.AsyncClient(
            transport=_test_module.httpx2.ASGITransport(app=app),
            base_url="http://127.0.0.1",
        ) as client:
            http = await client.post(
                "/anechoic/Anechoic/api/rebuild", json={"target": "all"}
            )
            self.assertEqual(200, http.status_code, http.text)
            response = http.json()
            self.assertEqual(
                ("ready", "all"), (response["status"], response["target"])
            )
            self.assertNotEqual(second, response["result_ids"][second])
            invalid = await client.post(
                "/anechoic/Anechoic/api/rebuild", json={"target": ""}
            )
            self.assertEqual(400, invalid.status_code)

    async def test_manifest_gates_release_commands(self):
        names = {"local_release_command", "public_release_command"}
        for operation in ("local", "public"):
            self._release_claim(operation)
        for flag in (
            {},
            {"release_workflows_enabled": False},
            {"release_workflows_enabled": True},
        ):
            with self.subTest(flag=flag):
                await self._assert_release_flag(flag, names)

    async def _assert_release_flag(self, flag, names):
        from ..group_3 import test_native_workbench_http as _test_module

        gateway = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        settings = {"project_mcp": flag}
        host_root = _test_module.Path("/host/Anechoic checkout")
        gateway.selection = gateway._native_query.selection = (
            _test_module.replace(
                gateway.selection,
                host_root=host_root,
                parameters=settings,
            )
        )
        with _test_module.patch.dict(
            "os.environ", {"ANECHOIC_RUNTIME_NAMESPACE": "docker"}
        ):
            await gateway.initialize()
        try:
            enabled = flag.get("release_workflows_enabled") is True
            advertised = {tool.name for tool in gateway.tools}
            self.assertEqual(names if enabled else set(), advertised & names)
            for name, operation in (
                ("local_release_command", "local"),
                ("public_release_command", "public"),
            ):
                await self._assert_release_command(
                    gateway, host_root, enabled, name, operation
                )
        finally:
            await gateway.close()

    async def _assert_release_command(
        self, gateway, host_root, enabled, name, operation
    ):
        from ..group_3 import test_native_workbench_http as _test_module

        response = await gateway.call(
            None,
            _test_module.types.CallToolRequestParams(
                name=name,
                arguments={
                    "run_id": "release-check-1",
                    **(
                        {"content_draft": "/host/review draft.json"}
                        if operation == "public"
                        else {}
                    ),
                },
            ),
        )
        self.assertEqual(
            not enabled,
            response.is_error,
            response.structured_content,
        )
        if enabled:
            self._assert_release_content(response, host_root, operation)

    def _assert_release_content(self, response, host_root, operation):
        from ..group_3 import test_native_workbench_http as _test_module

        args = _test_module.shlex.split(response.structured_content["command"])
        self.assertEqual(["uv", "run"], args[1:3])
        script = str(host_root / f"release scripts/{operation}.py")
        self.assertIn(script, args)
        expected = [
            operation,
            "--project-root",
            str(host_root),
            "--run-id",
            "release-check-1",
        ]
        if operation == "public":
            expected += [
                "--content-draft",
                "/host/review draft.json",
            ]
        self.assertEqual(expected, args[args.index(script) + 1 :])
        self.assertEqual(
            response.structured_content["command"],
            response.content[0].text,
        )
        self.assertEqual(
            str(host_root),
            response.structured_content["working_directory"],
        )

    async def test_release_claim_errors_and_recovery(self):
        from ..group_3 import test_native_workbench_http as _test_module

        gateway = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        gateway.selection = gateway._native_query.selection = (
            _test_module.replace(
                gateway.selection,
                parameters={
                    "project_mcp": {"release_workflows_enabled": True}
                },
            )
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)

        async def call():
            return await gateway.call(
                None,
                _test_module.types.CallToolRequestParams(
                    name="local_release_command",
                    arguments={"run_id": "release-check-1"},
                ),
            )

        self.assertTrue((await call()).is_error)
        path = self._release_claim("local", status="draft")
        self.assertTrue((await call()).is_error)
        self._release_claim("local")
        self.assertFalse((await call()).is_error)
        duplicate = self._release_claim("local", atom_id="AN-P-059")
        self.assertTrue((await call()).is_error)
        duplicate.unlink()
        self._release_claim(
            "local",
            body="## Claim\n\n### Formal Claim\n\n```python\n"
            'release_command(operation="local", entrypoint="../escape.py")\n```\n',
        )
        self.assertTrue((await call()).is_error)
        self._release_claim("local")
        self.assertFalse((await call()).is_error)
        path.unlink()
        self.assertTrue((await call()).is_error)

    async def test_manifest_blacklist_applies_to_mcp_and_http(self):
        from ..group_3 import test_native_workbench_http as _test_module

        gateway = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        selection = _test_module.replace(
            gateway.selection,
            parameters={
                "project_mcp": {
                    "tool_blacklist": ["query_schema", "workbench_status"]
                },
            },
        )
        gateway.selection = gateway._native_query.selection = selection
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        self.assertNotIn("query_schema", {tool.name for tool in gateway.tools})
        self.assertNotIn(
            "workbench_status", {tool.name for tool in gateway.tools}
        )
        response = await gateway.call(
            None,
            _test_module.types.CallToolRequestParams(
                name="query_schema", arguments={}
            ),
        )
        self.assertTrue(response.is_error)
        response = await gateway.call(
            None,
            _test_module.types.CallToolRequestParams(
                name="workbench_status", arguments={}
            ),
        )
        self.assertTrue(response.is_error)
        await self._assert_blacklist_http(gateway)

        await gateway.close()
        await self._assert_invalid_blacklist()

    async def _assert_invalid_blacklist(self):
        from ..group_3 import test_native_workbench_http as _test_module

        invalid = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        invalid.selection = invalid._native_query.selection = (
            _test_module.replace(
                invalid.selection,
                parameters={"project_mcp": {"tool_blacklist": "query_schema"}},
            )
        )
        with self.assertRaises(ValueError):
            await invalid.initialize()
        await invalid.close()

    async def _assert_blacklist_http(self, gateway):
        from ..group_3 import test_native_workbench_http as _test_module

        async with _test_module.httpx2.AsyncClient(
            transport=_test_module.httpx2.ASGITransport(
                app=_test_module.Starlette(routes=_test_module.routes(gateway))
            ),
            base_url="http://127.0.0.1:18093",
        ) as client:
            response = await client.post(
                "/anechoic/Anechoic/api/schema", json={}
            )
            self.assertEqual(400, response.status_code)
            response = await client.post(
                "/anechoic/Anechoic/api/status", json={}
            )
            self.assertEqual(400, response.status_code)
