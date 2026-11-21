"""Host release dispatch and refusals, with release effects replaced."""


from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY))
from LAYER_5_FRAMEWORK_DELIVERY import release  # noqa: E402
from LAYER_5_FRAMEWORK_DELIVERY import release_events  # noqa: E402

LOCAL_ENTRY = "LAYER_5_FRAMEWORK_DELIVERY.RELEASE_VERSION.RELEASE_VERSION__family_pub.run_local_release"
PUBLIC_MODULE = "LAYER_5_FRAMEWORK_DELIVERY.PUBLIC_RELEASE.PUBLIC_RELEASE__family_pub"
PUBLIC_ENTRY = PUBLIC_MODULE + ".run_public_release"


DRAFT = {
    "description": "## New\n- Host command.\n\n## Fixed\n- Routing.\n",
    "summary": ["Host command."],
}


class ReleaseCliTests(unittest.TestCase):
    def setUp(self) -> None:
        recording = patch.object(
            release_events, "record_release_event", return_value=("event", None)
        )
        self.record = recording.start()
        self.addCleanup(recording.stop)

    def invoke(self, arguments: list[str]) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        with redirect_stdout(output):
            status = release.main(arguments)
        return status, json.loads(output.getvalue())

    def test_local_dispatch_preserves_result_and_defaults(self) -> None:
        result = {"outcome": "completed", "receipt_path": "receipt.json"}
        with patch(LOCAL_ENTRY, return_value=result) as run:
            self.assertEqual(self.invoke(["local", "--run-id", "local-1"]), (0, result))
        run.assert_called_once_with(REPOSITORY, run_id="local-1", image_mode="refresh")

    def test_local_cli_can_run_without_public_component(self) -> None:
        result = {"outcome": "completed"}
        with (
            patch(LOCAL_ENTRY, return_value=result),
            patch.dict(sys.modules, {PUBLIC_MODULE: None}),
            redirect_stdout(io.StringIO()) as output,
        ):
            command = runpy.run_path(str(REPOSITORY / "LAYER_5_FRAMEWORK_DELIVERY/release.py"))
            self.assertEqual(0, command["main"](["local", "--run-id", "local-only"]))
        self.assertEqual(result, json.loads(output.getvalue()))

    def test_local_dispatch_forwards_repeatable_focused_modules(self) -> None:
        result = {"outcome": "completed", "receipt_path": "receipt.json"}
        modules = (
            "LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_first.py",
            "LAYER_3_ENGINE_STUDIO_C14/component/tests/test_second.py",
        )
        with patch(LOCAL_ENTRY, return_value=result) as run:
            self.assertEqual(
                self.invoke(
                    [
                        "local",
                        "--run-id",
                        "local-focused",
                        "--image-mode",
                        "existing",
                        "--test-module",
                        modules[0],
                        "--test-module",
                        modules[1],
                    ]
                ),
                (0, result),
            )
        run.assert_called_once_with(
            REPOSITORY,
            run_id="local-focused",
            image_mode="existing",
            test_modules=modules,
        )

    def test_public_dispatch_and_failed_result(self) -> None:
        temporary = REPOSITORY / ".anechoic_tmp/verification/release-cli"
        temporary.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            draft = Path(directory) / "draft.json"
            draft.write_text(json.dumps(DRAFT), encoding="utf-8")
            control = Path(directory) / "_anechoic_fixture"
            control.mkdir()
            (control / "FX-S-1-SPEC-PROJECT_MANIFEST--declare-fixture.md").write_text(
                "---\natom_family: SPEC\natom_id: FX-S-1\ncontainer:\n  component: C00\n"
                "tier: -1\ncontext:\n  template: project_manifest\n  lens: SPEC\n"
                "state:\n  status: active\n  version: 1\n  updated_at: '2026-11-21T00:00:00Z'\n---\n"
                "## Summary\n\nDeclare Fixture\n\n## Claim\n\n### Formal Claim\n\n```python\n"
                "from anechoic.formal_claims import declare_entity\n"
                "from anechoic.model import ProjectManifest\n"
                "declare_entity(entity_name='Project Manifest', instance=ProjectManifest("
                "name='Fixture', prefix='FX', parameters={'project': {'repository_slug': 'fixture-repo'}}))\n```\n",
                encoding="utf-8",
            )
            result = {"outcome": "failed", "failed_step": "tests", "report_path": "issue.md"}
            with patch(PUBLIC_ENTRY, return_value=result) as run:
                status, actual = self.invoke(
                    [
                        "public",
                        "--run-id",
                        "public-1",
                        "--project-root",
                        directory,
                        "--content-draft",
                        str(draft),
                    ]
                )
            self.assertEqual((status, actual), (1, result))
            run.assert_called_once_with(
                Path(directory), run_id="public-1", content_draft=DRAFT, repository_slug="fixture-repo",
            )

    def test_public_release_refuses_a_checkout_with_only_legacy_settings(self) -> None:
        temporary = REPOSITORY / ".anechoic_tmp/verification/release-cli"
        temporary.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory, patch(PUBLIC_ENTRY) as run:
            root = Path(directory)
            draft = root / "draft.json"
            draft.write_text(json.dumps(DRAFT), encoding="utf-8")
            control = root / ".anechoic_anechoic"
            control.mkdir()
            (control / "anechoic_project_settings.toml").write_text(
                '[project]\nname = "fixture"\nkey = "fixture"\nrepository_slug = "fixture-repo"\n'
                '[artifacts.identity]\nproject_prefix = "FX"\n', encoding="utf-8",
            )
            status, actual = self.invoke([
                "public", "--run-id", "legacy-only", "--project-root", directory, "--content-draft", str(draft),
            ])
        self.assertEqual(1, status)
        self.assertEqual("invocation", actual["failed_step"])
        run.assert_not_called()
        self.record.assert_not_called()

    def test_missing_draft_uses_native_input_required_without_effects(self) -> None:
        with patch("subprocess.run", side_effect=AssertionError("release effect")):
            status, result = self.invoke(["public", "--run-id", "public-1"])
        self.assertEqual(status, 1)
        self.assertEqual(result["outcome"], "input_required")
        self.assertIn("content_draft_schema", result)
        self.record.assert_not_called()

    def test_malformed_drafts_do_not_dispatch(self) -> None:
        temporary = REPOSITORY / ".anechoic_tmp/verification/release-cli"
        temporary.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary) as directory:
            draft = Path(directory) / "draft.json"
            for payload in (
                b"{",
                b"[]",
                b"{}",
                b"\xff",
                b" " * 1_048_577,
                json.dumps({**DRAFT, "extra": True}).encode(),
                json.dumps({**DRAFT, "summary": [7]}).encode(),
            ):
                with self.subTest(payload=payload[:10]):
                    draft.write_bytes(payload)
                    with patch(PUBLIC_ENTRY) as run:
                        status, result = self.invoke(
                            [
                                "public",
                                "--run-id",
                                "bad",
                                "--content-draft",
                                str(draft),
                            ]
                        )
                    self.assertEqual(status, 1)
                    self.assertEqual(result["failed_step"], "invocation")
                    run.assert_not_called()
            self.record.assert_not_called()

    def test_native_exception_is_bounded_and_not_retried(self) -> None:
        with patch(
            LOCAL_ENTRY, side_effect=ValueError("private payload")
        ) as run:
            status, result = self.invoke(["local", "--run-id", "bad"])
        self.assertEqual(status, 1)
        self.assertEqual(result["error_type"], "ValueError")
        self.assertNotIn("private payload", json.dumps(result))
        run.assert_called_once()

    def test_interruption_returns_one_json_result_and_exit_130(self) -> None:
        for returned in (
            {"outcome": "failed", "error_type": "KeyboardInterrupt"},
            KeyboardInterrupt(),
        ):
            with self.subTest(returned=type(returned).__name__):
                side_effect = returned if isinstance(returned, BaseException) else None
                with patch(
                    LOCAL_ENTRY,
                    return_value=None if side_effect else returned,
                    side_effect=side_effect,
                ) as run:
                    output = io.StringIO()
                    with redirect_stdout(output):
                        status = release.main(["local", "--run-id", "interrupted"])
                self.assertEqual(status, 130)
                self.assertEqual(output.getvalue().count("\n"), 1)
                result = json.loads(output.getvalue())
                self.assertEqual(result["error_type"], "KeyboardInterrupt")
                self.assertEqual(result["outcome"], "failed")
                run.assert_called_once_with(REPOSITORY, run_id="interrupted", image_mode="refresh")

    def test_main_interruption_fallback_returns_one_json_result_and_exit_130(self) -> None:
        output = io.StringIO()
        with patch.object(release, "_invoke", side_effect=KeyboardInterrupt):
            with redirect_stdout(output):
                status = release.main(["local", "--run-id", "interrupted"])
        self.assertEqual(status, 130)
        self.assertEqual(output.getvalue().count("\n"), 1)
        self.assertEqual(
            json.loads(output.getvalue()),
            {
                "outcome": "failed",
                "failed_step": "invocation",
                "error_type": "KeyboardInterrupt",
            },
        )

    def test_terminal_record_interruption_preserves_completion_and_exits_130(self) -> None:
        self.record.side_effect = [("start", None), KeyboardInterrupt]
        with patch(
            LOCAL_ENTRY, return_value={"outcome": "completed"}):
            status, result = self.invoke(["local", "--run-id", "interrupted"])
        self.assertEqual(status, 130)
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["error_type"], "KeyboardInterrupt")
        self.assertIn("completed recording interrupted", str(result["recording_error"]))

    def test_invalid_file_path_does_not_dispatch(self) -> None:
        with patch(PUBLIC_ENTRY) as run:
            status, result = self.invoke(
                ["public", "--run-id", "missing", "--content-draft", "\x00"]
            )
        self.assertEqual(status, 1)
        self.assertEqual(result["failed_step"], "invocation")
        run.assert_not_called()

    def test_real_cli_help_and_invalid_arguments(self) -> None:
        for arguments, expected in ((["--help"], 0), (["local"], 2), (["wrong"], 2)):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(REPOSITORY / "LAYER_5_FRAMEWORK_DELIVERY/release.py"),
                        *arguments,
                    ],
                    cwd=REPOSITORY / ".anechoic_tmp",
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )
                self.assertEqual(result.returncode, expected, result.stderr)

    def test_native_stdout_does_not_corrupt_json(self) -> None:
        def noisy_release(*args: object, **kwargs: object) -> dict[str, object]:
            print("native progress")
            return {"outcome": "completed"}

        with patch(LOCAL_ENTRY, side_effect=noisy_release):
            status, result = self.invoke(["local", "--run-id", "stdout"])
        self.assertEqual(status, 0)
        self.assertEqual(result["outcome"], "completed")

    def test_invalid_root_and_run_id_do_not_record_or_dispatch(self) -> None:
        for arguments in (
            ["local", "--run-id", "../unsafe"],
            ["local", "--run-id", "safe", "--project-root", "/"],
        ):
            with (
                self.subTest(arguments=arguments),
                patch(LOCAL_ENTRY) as run,
            ):
                self.assertEqual(self.invoke(arguments)[0], 1)
                run.assert_not_called()
        self.record.assert_not_called()


if __name__ == "__main__":
    unittest.main()
