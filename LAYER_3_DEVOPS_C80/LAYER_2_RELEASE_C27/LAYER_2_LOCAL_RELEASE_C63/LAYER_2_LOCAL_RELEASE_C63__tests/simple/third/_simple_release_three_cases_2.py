"""Mocked local release and temporary checkout cases."""

import io
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
    LocalReleaseError,
    local_release_safety,
)
from LAYER_1_RUNTIME_IMAGES_C81.input_selection.input_selection__shared import (
    read_release_selection,
)
from LAYER_2_LOCAL_RELEASE_C63 import (
    local_release_package_phases as package_phases,
    local_release_runner,
)
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)


class SimpleReleaseThreeCases2:
    def test_installed_copies_are_checked_for_corruption(self):
        copy_tree = package_phases._copy_tree
        for destination, step in (
            (self.installed, "copy_product_to_installed_framework"),
            (self.root / ".agents/skills/ane", "install_project_runtime"),
        ):
            with self.subTest(destination=destination):

                def corrupt(
                    source, target, *, destination=destination, **kwargs
                ):
                    copy_tree(source, target, **kwargs)
                    if target == destination:
                        next(
                            path
                            for path in target.rglob("*")
                            if path.is_file() and path.name != "config.toml"
                        ).write_text("corrupt")

                runner, _ = self._runner()
                with patch.object(package_phases, "_copy_tree", corrupt):
                    result = run_local_release(
                        self.root, run_id=f"corrupt-{step}", runner=runner
                    )
                self.assertEqual("failed", result["outcome"])
                self.assertEqual(step, result["failed_step"])

    def test_installation_lock_refuses_contention_before_replacement(self):
        runner, calls = self._runner()
        version = (self.root / "version.toml").read_bytes()
        product = {
            p.relative_to(self.product): p.read_bytes()
            for p in self.product.rglob("*")
            if p.is_file()
        }
        stderr = io.StringIO()
        with (
            local_release_safety._installation_lock(
                self.root, read_release_selection(self.root)
            ),
            patch("sys.stderr", stderr),
        ):
            result = run_local_release(
                self.root, run_id="locked-install", runner=runner
            )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("installation_lock", result["failed_step"])
        self.assertIn(
            "local-release-installation-lock-busy", stderr.getvalue()
        )
        self.assertEqual("obsolete", (self.installed / "old.txt").read_text())
        self.assertEqual(version, (self.root / "version.toml").read_bytes())
        self.assertEqual(
            product,
            {
                p.relative_to(self.product): p.read_bytes()
                for p in self.product.rglob("*")
                if p.is_file()
            },
        )
        self.assertFalse(any(argv[0] == "git" for argv in calls))
        self.start_container.assert_not_called()
        with local_release_safety._installation_lock(
            self.root, read_release_selection(self.root)
        ):
            pass

    def test_installation_lock_and_staging_refuse_symlinked_owners(self):
        temporary = self.root / ".anechoic_tmp"
        temporary.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other)
            (temporary / "local_release_installation").symlink_to(
                outside, target_is_directory=True
            )
            (temporary / "simple_local_release").symlink_to(
                outside, target_is_directory=True
            )

            runner, calls = self._runner()
            result = run_local_release(
                self.root, run_id="linked-lock", runner=runner
            )
            self.assertEqual(
                ("failed", "installation_lock"),
                (result["outcome"], result["failed_step"]),
            )
            self.assertEqual([], calls)
            with self.assertRaisesRegex(
                LocalReleaseError, "temporary-directory-unsafe"
            ):
                local_release_safety._new_staging_directory(
                    self.root, "linked-stage-"
                )
            self.assertEqual([], list(outside.iterdir()))

    def test_staging_refuses_an_owner_replaced_during_allocation(self):
        owner = self.root / ".anechoic_tmp/simple_local_release"
        owner.mkdir(parents=True)
        moved = owner.with_name("moved")
        mkdir = os.mkdir

        def replace_owner(path, *args, **kwargs):
            mkdir(path, *args, **kwargs)
            if str(path).startswith("swap-"):
                owner.rename(moved)
                owner.symlink_to(moved, target_is_directory=True)

        with patch.object(
            local_release_safety.os, "mkdir", side_effect=replace_owner
        ):
            with self.assertRaisesRegex(
                LocalReleaseError, "temporary-directory-changed"
            ):
                local_release_safety._new_staging_directory(self.root, "swap-")
        self.assertEqual([], list(moved.iterdir()))

    def test_installation_lock_covers_copy_and_mcp_handoff(self):
        runner, _ = self._runner()
        copy_tree = package_phases._copy_tree
        checked = []

        def check_locked():
            with self.assertRaisesRegex(
                LocalReleaseError, "installation-lock-busy"
            ):
                with local_release_safety._installation_lock(
                    self.root, read_release_selection(self.root)
                ):
                    pass
            checked.append(True)

        def copy(source, target, **kwargs):
            if target in (
                self.installed,
                self.runtime / "simple_local_release/package",
                self.root / ".agents/skills/ane",
            ):
                check_locked()
            return copy_tree(source, target, **kwargs)

        def start(*args, **kwargs):
            check_locked()
            return "http://localhost:12345/mcp"

        with (
            patch.object(package_phases, "_copy_tree", copy),
            patch.object(
                local_release_runner, "start_container", side_effect=start
            ),
        ):
            result = run_local_release(
                self.root, run_id="lock-coverage", runner=runner
            )
        self.assertEqual("completed", result["outcome"])
        self.assertEqual(4, len(checked))
