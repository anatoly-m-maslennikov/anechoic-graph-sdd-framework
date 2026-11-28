"""Host release dispatch and refusals, with release effects replaced."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import runpy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from LAYER_2_RELEASE_C27__tests.LAYER_2_RELEASE_C27__tests__shared import (
    DRAFT,
    ReleaseCliFixture,
)

REPOSITORY = Path(__file__).resolve().parents[3]
LOCAL_ENTRY = (
    "LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared.run_local_rel"
    "ease"
)
PUBLIC_MODULE = "LAYER_3_PUBLIC_RELEASE_C64.LAYER_3_PUBLIC_RELEASE_C64__shared"
PUBLIC_ENTRY = PUBLIC_MODULE + ".run_public_release"
IMAGE_ENTRY = "LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared"


class ReleaseCliTests(ReleaseCliFixture, unittest.TestCase):
    def test_build_image_dispatch(self) -> None:
        result = {"outcome": "completed", "image_id": "sha256:" + "a" * 64}
        entry = IMAGE_ENTRY + ".build_image"
        with patch(entry, return_value=result) as build:
            self.assertEqual(
                self.invoke(["build-image", "--run-id", "build-1"]),
                (0, result),
            )
        build.assert_called_once_with(REPOSITORY, run_id="build-1")

    def test_run_image_dispatch(self) -> None:
        image = "sha256:" + "a" * 64
        result = {"ready": True, "image": image}
        with patch(
            IMAGE_ENTRY + ".launch_shared_image", return_value=result
        ) as launch:
            arguments = [
                "run-image",
                "--image",
                image,
                "--host-settings",
                "runtime.toml",
                "--apply",
                "--verify-mcp",
            ]
            self.assertEqual(
                self.invoke(arguments), (0, {**result, "outcome": "completed"})
            )
        launch.assert_called_once_with(
            host_settings=Path("runtime.toml"),
            image=image,
            apply=True,
            verify_mcp=True,
            startup_timeout=None,
            readiness_timeout=None,
        )

    def test_run_image_uses_saved_mounted_settings(self) -> None:
        result = {"mode": "dry-run", "http_port": 7777}
        with patch(
            IMAGE_ENTRY + ".launch_shared_image", return_value=result
        ) as launch:
            self.assertEqual(
                self.invoke(["run-image", "--mounted-folder", "/mounted"]),
                (0, {**result, "outcome": "completed"}),
            )
        launch.assert_called_once_with(
            host_settings=None,
            image=None,
            mounted_folder=Path("/mounted"),
            apply=False,
            verify_mcp=False,
            startup_timeout=None,
            readiness_timeout=None,
        )

    def test_local_dispatch_preserves_result_and_defaults(self) -> None:
        result = {"outcome": "completed", "receipt_path": "receipt.json"}
        with patch(LOCAL_ENTRY, return_value=result) as run:
            self.assertEqual(
                self.invoke(["local", "--run-id", "local-1"]), (0, result)
            )
        run.assert_called_once_with(
            REPOSITORY, run_id="local-1", image_mode="refresh"
        )

    def test_local_resume_dispatch_preserves_run_id_and_saved_options(
        self,
    ) -> None:
        result = {"outcome": "completed", "receipt_path": "receipt.json"}
        with patch(LOCAL_ENTRY, return_value=result) as run:
            self.assertEqual(
                self.invoke(["local", "--resume", "--run-id", "local-1"]),
                (0, result),
            )
        run.assert_called_once()
        self.assertEqual((REPOSITORY,), run.call_args.args)
        self.assertEqual("local-1", run.call_args.kwargs["run_id"])
        self.assertIs(run.call_args.kwargs["resume"], True)
        self.assertIsNone(run.call_args.kwargs.get("image_mode"))
        self.assertIsNone(run.call_args.kwargs.get("test_modules"))

    def test_local_cli_can_run_without_public_component(self) -> None:
        result = {"outcome": "completed"}
        with (
            patch(
                (
                    "LAYER_2_LOCAL_RELEASE_C63."
                    "LAYER_2_LOCAL_RELEASE_C63__shared.r"
                    "un_local_release"
                ),
                return_value=result,
            ),
            patch.dict(
                sys.modules,
                {PUBLIC_MODULE: None},
            ),
            redirect_stdout(io.StringIO()) as output,
        ):
            command = runpy.run_path(
                str(
                    REPOSITORY / "LAYER_3_DEVOPS_C80/"
                    "LAYER_2_RELEASE_C27/release.py"
                )
            )
            self.assertEqual(
                0, command["main"](["local", "--run-id", "local-only"])
            )
        self.assertEqual(result, json.loads(output.getvalue()))

    def test_local_dispatch_forwards_repeatable_focused_modules(self) -> None:
        result = {"outcome": "completed", "receipt_path": "receipt.json"}
        modules = (
            (
                "LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJEC"
                "T_TOOLS/FEATURE_PROJECT_TOOLS__tests/test_first.py"
            ),
            "LAYER_4_ENGINE_STUDIO_C14/component/tests/test_second.py",
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

    def test_public_dispatch_without_runtime_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.json"
            draft.write_text(json.dumps(DRAFT), encoding="utf-8")
            result = {
                "outcome": "completed",
                "version_history_entry": "## 1.0.1",
            }
            with patch(PUBLIC_ENTRY, return_value=result) as run:
                status, actual = self.invoke(
                    [
                        "public",
                        "--run-id",
                        "public-1",
                        "--project-root",
                        directory,
                        "--base",
                        "main",
                        "--head",
                        "candidate",
                        "--content-draft",
                        str(draft),
                    ]
                )
            self.assertEqual((status, actual), (0, result))
            run.assert_called_once_with(
                Path(directory).resolve(),
                run_id="public-1",
                base_ref="main",
                head_ref="candidate",
                content_draft=DRAFT,
            )

    def test_missing_draft_requests_evidence(self) -> None:
        result = {"outcome": "input_required", "completed_tickets": []}
        with patch(PUBLIC_ENTRY, return_value=result) as run:
            self.assertEqual(
                self.invoke(["public", "--run-id", "public-1"]), (1, result)
            )
        run.assert_called_once_with(
            REPOSITORY,
            run_id="public-1",
            base_ref="origin/main",
            head_ref="amm/dev",
            content_draft=None,
        )
