"""Release metadata comes from the owning repository and canonical selection."""

from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock, NonCallableMock, call

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests import test_simple_local_release as fixtures
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release
from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import release_image_provenance


class ReleaseImageProvenanceTests(unittest.TestCase):
    def test_native_provenance_uses_validated_manifest_name(self) -> None:
        root = Path("/owner")
        selection = NonCallableMock(
            spec_set=["instance_id", "control_relative", "project_name",
                      "settings"],
            instance_id="c" * 64, control_relative=Path(".anechoic_anechoic"),
            project_name="Anechoic", settings={"project": {"name": "Legacy"}},
        )
        runner = Mock(return_value=subprocess.CompletedProcess([], 0, "d" * 40, ""))
        metadata = release_image_provenance(root, selection, runner)
        self.assertEqual("Anechoic", metadata["project_name"])
        self.assertEqual(selection.instance_id, metadata["project_id"])

    def test_owner_name_and_full_head_are_observed_from_owning_root(self) -> None:
        root = Path("/owning-repository")
        selection = NonCallableMock(
            spec_set=["instance_id", "control_relative", "settings"],
            instance_id="c" * 64,
            control_relative=Path(".anechoic_anechoic"),
            settings={"project": {"name": "Named Project"}},
        )
        runner = Mock(return_value=subprocess.CompletedProcess([], 0, "d" * 40 + "\n", ""))
        metadata = release_image_provenance(root, selection, runner)
        runner.assert_called_once_with(("git", "rev-parse", "--verify", "HEAD"), root)
        self.assertEqual(
            metadata,
            {
                "project_id": "c" * 64,
                "project_root": str(root),
                "control_root": ".anechoic_anechoic",
                "project_name": "Named Project",
                "head_commit": "d" * 40,
            },
        )

    def test_missing_name_bad_head_and_failed_git_refuse(self) -> None:
        selection = NonCallableMock(
            spec_set=["instance_id", "control_relative", "project_name",
                      "settings"],
            instance_id="c" * 64,
            control_relative=Path(".anechoic_anechoic"),
            settings={"project": {"name": "Named Project"}},
        )
        del selection.project_name
        for status, output in ((0, "short-sha"), (1, "d" * 40), (0, "")):
            with self.subTest(status=status, output=output), self.assertRaises(ValueError):
                release_image_provenance(
                    Path("/owner"),
                    selection,
                    Mock(return_value=subprocess.CompletedProcess([], status, output, "")),
                )
        selection.settings = {"project": {"name": ""}}
        runner = Mock()
        with self.assertRaises(ValueError):
            release_image_provenance(Path("/owner"), selection, runner)
        runner.assert_not_called()
        selection.settings = {"project": {"name": "Legacy"}}
        selection.project_name = ""
        with self.assertRaises(ValueError):
            release_image_provenance(Path("/owner"), selection, runner)
        runner.assert_not_called()

    def test_native_runner_preserves_candidate_provenance_through_recheck(self) -> None:
        fixture = fixtures.SimpleLocalReleaseTests("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            output = ("d" * 40 if argv[:2] == ("git", "rev-parse") else
                      "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n"
                      if "--phase" in argv and argv[argv.index("--phase") + 1] == "canary" else "")
            return subprocess.CompletedProcess(argv, 0, output, "")

        result = run_local_release(fixture.root, run_id="provenance", runner=runner)
        self.assertEqual("completed", result["outcome"], result)
        fixture.provenance.assert_called_once()
        self.assertEqual(fixture.provenance.call_args.args[0], fixture.root)
        prepared, rechecked, installed = fixture.image_factory.call_args_list
        self.assertEqual(fixture.provenance.return_value, prepared.kwargs["build_provenance"])
        self.assertEqual(prepared, rechecked)
        self.assertEqual({"project_root": fixture.root}, installed.kwargs)
        exact = call(explicit_id=fixture.image_id, build_if_missing=False)
        self.assertEqual([call(use_packaged_assets=True), exact, exact], fixture.image.resolve.call_args_list)

    def test_unavailable_head_stops_before_candidate_build(self) -> None:
        fixture = fixtures.SimpleLocalReleaseTests("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        version = (fixture.root / "version.toml").read_bytes()

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(argv, 0, "", "")

        result = run_local_release(fixture.root, run_id="no-head", runner=runner)
        self.assertEqual(result["failed_step"], "git_before_validate_inputs")
        self.assertEqual(version, (fixture.root / "version.toml").read_bytes())
        fixture.provenance.assert_not_called()
        fixture.image_factory.assert_not_called()

    def test_build_head_observation_follows_initial_commit_in_owning_repository(self) -> None:
        fixture = fixtures.SimpleLocalReleaseTests("runTest")
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.provenance.side_effect = release_image_provenance
        calls: list[tuple[str, ...]] = []
        dirty = True
        head = "d" * 40

        def runner(argv: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
            nonlocal dirty, head
            self.assertEqual(root, fixture.root)
            calls.append(argv)
            if argv == ("git", "diff", "--cached", "--quiet"):
                return subprocess.CompletedProcess(argv, int(dirty), "", "")
            if argv[:2] == ("git", "commit"):
                dirty, head = False, "e" * 40
            if "--phase" in argv and argv[argv.index("--phase") + 1] == "canary":
                return subprocess.CompletedProcess(
                    argv, 0, "ANECHOIC_CANARY_ENDPOINT http://127.0.0.1:49152/anechoic/mcp\n", ""
                )
            return subprocess.CompletedProcess(
                argv, 0, head if argv[:3] == ("git", "rev-parse", "--verify") else "", ""
            )

        result = run_local_release(fixture.root, run_id="post-commit-head", runner=runner)
        self.assertEqual(result["outcome"], "completed")
        commit = next(index for index, argv in enumerate(calls) if argv[:2] == ("git", "commit"))
        observe = calls.index(("git", "rev-parse", "--verify", "HEAD"))
        self.assertLess(commit, observe)
        metadata = fixture.image_factory.call_args_list[0].kwargs["build_provenance"]
        self.assertEqual(metadata["head_commit"], "e" * 40)
        self.assertEqual(metadata["project_root"], str(fixture.root))


if __name__ == "__main__":
    unittest.main()
