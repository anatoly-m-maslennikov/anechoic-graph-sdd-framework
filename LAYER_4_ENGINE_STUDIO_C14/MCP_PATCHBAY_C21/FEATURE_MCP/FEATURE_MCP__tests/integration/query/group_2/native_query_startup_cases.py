"""Startup behavior cases for the native query entry points."""


class NativeQueryStartupCases:
    def test_http_entrypoint_uses_native_selection(self):
        from ..group_1 import test_native_query_stdio as host
        from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
            main as http_main,
        )
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
            server_main,
        )

        inputs = host._native_inputs()

        def factory(root, control):
            return host.create_native_gateway(root, control, inputs)

        args = [
            "--project-root",
            str(self.root),
            "--control-root",
            host.CONTROL,
        ]
        with (
            host.patch(
                (
                    'MCP_PATCHBAY_C21.FEATURE_MCP'
                    '.gateway.http_server.startup'
                    '_selection'
                ),
                side_effect=AssertionError("legacy selection"),
            ),
            host.patch("uvicorn.run") as run,
        ):
            self.assertIsNone(
                server_main(
                    args + ["--transport", "streamable-http"],
                    gateway_factory=factory,
                )
            )
            app = run.call_args.args[0]
            self.assertEqual(self.root, app.gateway.selection.root)
            self.assertIsNotNone(app.gateway._native_query)
        self._assert_http_selectors(server_main, http_main, args, factory)

    def _assert_http_selectors(self, server_main, http_main, args, factory):
        for main, extra in (
            (server_main, ["--transport", "streamable-http"]),
            (http_main, []),
        ):
            for selector in (
                ["--instance-id", "legacy"],
                ["--host-project-root", str(self.root)],
            ):
                with (
                    self.subTest(main=main, selector=selector),
                    self.assertRaises(SystemExit),
                ):
                    main(args + extra + selector, gateway_factory=factory)
            with (
                self.subTest(main=main, selector="missing control"),
                self.assertRaises(SystemExit),
            ):
                main(
                    ["--project-root", str(self.root), *extra],
                    gateway_factory=factory,
                )

    def test_second_native_process_reports_project_lock_to_stderr(self):
        from ..group_1 import test_native_query_stdio as host

        owner = host.create_native_gateway(
            self.root, host.CONTROL, host._native_inputs()
        )._native_query
        self.addCleanup(owner.close)
        owner.start()
        completed = host.subprocess.run(
            [host.sys.executable, *self.args],
            input="",
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stdout)
        self.assertIn("This Project is already open", completed.stderr)

    def test_startup_refuses_an_unapproved_manifest_owner(self):
        from ..group_1 import test_native_query_stdio as host

        manifest_path = self.root / host.CONTROL / host.MANIFEST
        source = manifest_path.read_text(encoding="utf-8")
        manifest_path.write_text(
            source.replace("component: C0", "component: C1"), encoding="utf-8"
        )
        result = host.subprocess.run(
            [host.sys.executable, *self.args],
            input="",
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)
        self.assertIn("mcp_stdio_startup_failed", result.stderr)
        self.assertIn("anechoic: operation failed", result.stderr)
