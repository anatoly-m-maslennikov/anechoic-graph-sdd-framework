"""Focused Workbench HTTP contract cases."""


class NativeWorkbenchLifecycleCases:
    async def test_manifest_change_blocks_lifecycle_until_gateway_restarts(
        self,
    ):
        from ..group_3 import test_native_workbench_http as _test_module

        gateway = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        manifest = gateway.selection.manifest_path
        renamed = manifest.with_name(
            manifest.name.replace("--declare-", "--define-")
        )
        renamed.write_text(
            manifest.read_text().replace("version: 1", "version: 2", 1)
        )
        manifest.unlink()

        await self._wait_manifest_reload(gateway)

        arguments = {
            "newAtom": {
                "template": "task",
                "label": "Task",
                "container": {"component": "C00"},
                "body": "## Summary\n\nManifest reload regression.\n",
            }
        }
        await self._assert_reload_blocked(gateway, arguments)

        await self._assert_reload_recovered(gateway, arguments)

    async def _assert_reload_recovered(self, gateway, arguments):
        from ..group_3 import test_native_workbench_http as _test_module

        await gateway.close()
        fresh = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        await fresh.initialize()
        self.addAsyncCleanup(fresh.close)
        self.assertEqual("AN-S-001@2", fresh.selection.manifest_ref)
        result = await fresh.call(
            None,
            _test_module.types.CallToolRequestParams(
                name="atom_lifecycle_create_draft",
                arguments=arguments,
            ),
        )
        self.assertEqual(
            "completed",
            result.structured_content["status"],
            result.structured_content,
        )
        self.assertTrue(result.structured_content["savedDraft"])

    async def _assert_reload_blocked(self, gateway, arguments):
        from ..group_3 import test_native_workbench_http as _test_module

        source = self.root / _test_module.fixture.CONTROL
        before = {
            p.relative_to(source): p.read_bytes()
            for p in source.rglob("*")
            if p.is_file()
        }
        result = await gateway.call(
            None,
            _test_module.types.CallToolRequestParams(
                name="atom_lifecycle_create_draft",
                arguments=arguments,
            ),
        )
        self.assertEqual(
            "blocked",
            result.structured_content["status"],
            result.structured_content,
        )
        self.assertEqual(
            "project_manifest_reload_required",
            result.structured_content["errors"][0]["code"],
        )
        self.assertIn(
            "restart",
            result.structured_content["errors"][0]["message"].lower(),
        )
        self.assertEqual(
            before,
            {
                p.relative_to(source): p.read_bytes()
                for p in source.rglob("*")
                if p.is_file()
            },
        )

    async def _wait_manifest_reload(self, gateway):
        from ..group_3 import test_native_workbench_http as _test_module

        async with _test_module.asyncio.timeout(15):
            while True:
                query = await gateway.call(
                    None,
                    _test_module.types.CallToolRequestParams(
                        name="query_run",
                        arguments={
                            "sql": "SELECT 1",
                            "result_delivery": "inline",
                        },
                    ),
                )
                self.assertFalse(query.is_error, query.structured_content)
                if (
                    gateway._native_query._projection_selection.manifest_ref
                    == "AN-S-001@2"
                ):
                    break
                await _test_module.asyncio.sleep(0.1)

    async def test_lifecycle_catalog_and_saved_references(self):
        from ..group_3 import test_native_workbench_http as _test_module

        gateway = _test_module.create_native_gateway(
            self.root,
            _test_module.fixture.CONTROL,
            _test_module.fixture._native_inputs(),
        )
        await gateway.initialize()
        self.addAsyncCleanup(gateway.close)
        tools = {tool.name: tool for tool in gateway.tools}
        lifecycle = {
            name for name in tools if name.startswith("atom_lifecycle_")
        }
        self.assertEqual(
            {
                "atom_lifecycle_archive",
                "atom_lifecycle_change_status",
                "atom_lifecycle_create_asset",
                "atom_lifecycle_create_draft",
                "atom_lifecycle_direct_update",
                "atom_lifecycle_promote_draft",
                "atom_lifecycle_update",
            },
            lifecycle,
        )
        self.assertEqual(
            {"sourceCurrent", "changes", "newAtom"},
            set(
                tools["atom_lifecycle_create_draft"].input_schema["properties"]
            ),
        )

        draft = await self._create_lifecycle_examples(gateway)
        await self._promote_and_revise(gateway, draft)

    async def _create_lifecycle_examples(self, gateway):
        await self._call_lifecycle(
            gateway,
            "atom_lifecycle_create_asset",
            {
                "newAtom": {
                    "template": "spec_proposal",
                    "body": "## Summary\n\nExample proposal.\n",
                }
            },
            "completed",
            "artifact",
        )
        draft = await self._call_lifecycle(
            gateway,
            "atom_lifecycle_create_draft",
            {
                "newAtom": {
                    "template": "task",
                    "label": "Task",
                    "container": {"component": "C00"},
                    "body": "## Summary\n\nLifecycle catalog check.\n",
                }
            },
            "completed",
            "savedDraft",
        )
        return draft

    async def _promote_and_revise(self, gateway, draft):
        current = await self._call_lifecycle(
            gateway,
            "atom_lifecycle_promote_draft",
            {
                "target": {
                    "ref_id": draft["ref_id"],
                    "version": draft["version"],
                },
                "targetStatus": "backlog",
            },
            "completed",
            "artifact",
        )
        self.assertEqual(draft["atom_id"], current["ref_id"])
        revision = await self._call_lifecycle(
            gateway,
            "atom_lifecycle_update",
            {
                "sourceCurrent": {
                    "ref_id": current["ref_id"],
                    "version": current["version"],
                },
                "changes": {
                    "body": (
                        '## Summary\n\nLifecycle catalo'
                        'g check.\n\nRevised.\n'
                    )
                },
            },
            "draft_created",
            "savedDraft",
        )
        self.assertEqual(draft["atom_id"], revision["atom_id"])
        self.assertEqual(current["version"] + 1, revision["version"])
        self.assertEqual(
            f"{revision['atom_id']}@{revision['version']}-draft",
            revision["ref_id"],
        )

    async def _call_lifecycle(self, gateway, name, arguments, status, field):
        from ..group_3 import test_native_workbench_http as _test_module

        response = await gateway.call(
            None,
            _test_module.types.CallToolRequestParams(
                name=name, arguments=arguments
            ),
        )
        self.assertFalse(response.is_error, response.structured_content)
        value = response.structured_content
        self.assertEqual(status, value["status"], value)
        saved = value[field]
        self.assertTrue((self.root / saved["path"]).is_file(), saved)
        self.assertTrue(
            _test_module.Path(saved["path"]).name.startswith(
                saved["ref_id"] + "-"
            ),
            saved,
        )
        return saved

    async def test_generated_lifecycle_catalog_is_public(self):
        from ..group_3 import test_native_workbench_http as _test_module

        mcp = _test_module.Path(_test_module.__file__).resolve().parents[4]
        _test_module.sys.path.insert(0, str(mcp / "docker"))
        self.addCleanup(_test_module.sys.path.remove, str(mcp / "docker"))
        from MCP_PATCHBAY_C21.FEATURE_MCP.docker.image.image__shared import (
            compile_tool_registry,
        )

        registry = _test_module.json.loads(
            await _test_module.asyncio.to_thread(
                compile_tool_registry,
                mcp.parents[2],
                timeout=60,
                max_output=2_000_000,
            )
        )
        provider = next(
            item
            for item in registry["providers"]
            if item["provider_id"] == "lifecycle"
        )
        self.assertEqual("tool_descriptors", provider["descriptor_factory"])
        expected = {
            "atom_lifecycle_archive",
            "atom_lifecycle_change_status",
            "atom_lifecycle_create_asset",
            "atom_lifecycle_create_draft",
            "atom_lifecycle_direct_update",
            "atom_lifecycle_promote_draft",
            "atom_lifecycle_update",
        }
        self.assertEqual(
            expected, {tool["name"] for tool in provider["tools"]}
        )
        self.assertTrue(expected <= set(registry["public_tools"]))
        self.assertFalse(expected & set(registry["mcp_blacklist"]))
        create = next(
            tool
            for tool in provider["tools"]
            if tool["name"] == "atom_lifecycle_create_draft"
        )
        self.assertEqual(
            {"sourceCurrent", "changes", "newAtom"},
            set(create["inputSchema"]["properties"]),
        )
