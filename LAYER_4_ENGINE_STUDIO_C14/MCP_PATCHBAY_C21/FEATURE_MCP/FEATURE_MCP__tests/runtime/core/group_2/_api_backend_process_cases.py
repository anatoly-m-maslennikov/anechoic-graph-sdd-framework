"""Focused release and web assertions for the Backend process tests."""


async def _check_command(self, gateway, root, script, fixture):
    os, types, shlex = fixture["os"], fixture["types"], fixture["shlex"]
    owner = gateway._native_query
    self.assertNotEqual(os.getpid(), owner.backend_pid)
    arguments = {"run_id": "smoke-1"}
    direct = (
        await gateway.workbench.call_tool("local_release_command", arguments)
    )["value"]
    command = await gateway.call(
        None,
        types.CallToolRequestParams(
            name="local_release_command",
            arguments={"run_id": "smoke-1"},
        ),
    )
    self.assertFalse(command.is_error, command.structured_content)
    self.assertEqual(direct, command.structured_content)
    args = shlex.split(direct["command"])
    self.assertEqual(
        "UV_PROJECT_ENVIRONMENT="
        + str(root / "LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release"),
        args[0],
    )
    self.assertNotIn("--no-sync", args)
    self.assertIn("-E", args)
    self.assertEqual(
        str(root),
        command.structured_content["working_directory"],
    )
    self.assertEqual(
        [
            "local",
            "--project-root",
            str(root),
            "--run-id",
            "smoke-1",
        ],
        args[args.index(str(script)) + 1 :],
    )
    return arguments, direct


async def _check_changed_inputs(
    self, gateway, claim, selection, arguments, direct, ToolProtocolError
):
    duplicate = claim.with_name("AN-P-59-WORKFLOW--duplicate.md")
    duplicate.write_bytes(claim.read_bytes().replace(b"AN-P-58", b"AN-P-59"))
    with self.assertRaisesRegex(
        ToolProtocolError, "Expected one Active"
    ) as caught:
        await gateway.workbench.call_tool("local_release_command", arguments)
    self.assertEqual("value_error", caught.exception.code)
    duplicate.unlink()
    self.assertEqual(
        direct,
        (
            await gateway.workbench.call_tool(
                "local_release_command", arguments
            )
        )["value"],
    )
    manifest = selection.manifest_path
    original = manifest.read_bytes()
    manifest.write_bytes(original + b"\n")
    with self.assertRaisesRegex(
        ToolProtocolError, "Project binding changed"
    ) as caught:
        await gateway.workbench.call_tool("local_release_command", arguments)
    self.assertEqual("value_error", caught.exception.code)
    manifest.write_bytes(original)
    self.assertEqual(
        direct,
        (
            await gateway.workbench.call_tool(
                "local_release_command", arguments
            )
        )["value"],
    )


async def release_case(self, fixture):
    tempfile = fixture["tempfile"]
    patch = fixture["patch"]
    os = fixture["os"]
    Path = fixture["Path"]
    _test_environment = fixture["_test_environment"]
    _project = fixture["_project"]
    _release_claim = fixture["_release_claim"]
    select_runtime_project = fixture["select_runtime_project"]
    CONTROL = fixture["CONTROL"]
    native_runtime_gateway = fixture["native_runtime_gateway"]
    ToolProtocolError = fixture["ToolProtocolError"]
    with (
        tempfile.TemporaryDirectory() as temporary,
        patch.dict(os.environ, _test_environment()),
    ):
        root = Path(temporary).resolve() / "Project with spaces"
        root.mkdir()
        _project(root)
        claim, script = _release_claim(root)
        selection = select_runtime_project(root, CONTROL)
        self.assertTrue(selection.release_workflows_enabled)
        with native_runtime_gateway(selection) as gateway:
            try:
                await gateway.initialize()
                arguments, direct = await _check_command(
                    self, gateway, root, script, fixture
                )
                await _check_changed_inputs(
                    self,
                    gateway,
                    claim,
                    selection,
                    arguments,
                    direct,
                    ToolProtocolError,
                )
            finally:
                await gateway.close()


def assert_web_probe(self, probe, os):
    self.assertNotEqual(probe["gateway_pid"], probe["backend_pid"])
    self.assertIsInstance(probe["backend_pid"], int)
    self.assertNotIn(
        probe["kernel_pid"], {probe["backend_pid"], probe["gateway_pid"]}
    )
    os.kill(probe["backend_pid"], 0)
    self.assertEqual(400, probe["invalid_status"], probe["invalid_body"])
    self.assertEqual(
        {
            "error": "name is only valid when save is true",
            "code": "value_error",
            "tool_result": {
                "outcome": "failed",
                "diagnostics": [
                    "query_error: name is only valid when save is true"
                ],
            },
        },
        probe["invalid_body"],
    )
    self.assertEqual("value_error", probe["rejected_method"]["error"]["code"])
    self.assertEqual(200, probe["http_status"], probe["http_body"])
    self.assertEqual([[42]], probe["http_body"]["rows"])


def write_gateway_probe(
    root, gateway, response, invalid, rejected_method, fixture
):
    os, json, _kernel_pid = (
        fixture["os"],
        fixture["json"],
        fixture["_kernel_pid"],
    )
    (root / "gateway-probe.json").write_text(
        json.dumps({
            "gateway_pid": os.getpid(),
            "backend_pid": gateway._native_query.backend_pid,
            "kernel_pid": _kernel_pid(gateway._native_query),
            "http_status": response.status_code,
            "http_body": response.json(),
            "invalid_status": invalid.status_code,
            "invalid_body": invalid.json(),
            "rejected_method": rejected_method,
        }),
        encoding="utf-8",
    )
