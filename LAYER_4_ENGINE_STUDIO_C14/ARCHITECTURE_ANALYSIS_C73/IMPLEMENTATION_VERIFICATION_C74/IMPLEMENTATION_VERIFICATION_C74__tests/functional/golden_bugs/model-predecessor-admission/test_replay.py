"""Replay Model predecessor admission before either compiler path."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve().parent
ENGINE = next(
    path for path in HERE.parents if path.name == ("LAYER_4_ENGINE_STUDIO_C14")
)
sys.path.insert(0, str(ENGINE))
CASE = json.loads((HERE / "case.json").read_text())
IMAGE = "sha256:" + "a" * 64


def invalid_predecessors():
    return [
        ("", inspect(), "immutable image ID"),
        ("latest", inspect(), "immutable image ID"),
        (
            IMAGE,
            inspect(image="sha256:" + "b" * 64),
            "not an admitted runtime image",
        ),
        (
            IMAGE,
            inspect(system="windows"),
            "not an admitted runtime image",
        ),
        (IMAGE, inspect(schema="2"), "not an admitted runtime image"),
    ]


def load(version):
    module = types.ModuleType("_image_stage_replay")
    module.__file__ = str(HERE / CASE[version]["fixture"])
    source = Path(module.__file__).read_text()
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def inspect(image=IMAGE, system="linux", schema="1"):
    details = [
        {
            "Id": image,
            "Os": system,
            "Config": {"Labels": {"org.anechoic.runtime.schema": schema}},
        }
    ]
    return subprocess.CompletedProcess([], 0, json.dumps(details), "")


class Replay(unittest.TestCase):
    def test_invalid_predecessors_on_both_paths(self):
        cases = invalid_predecessors()
        for version in ("before", "fixed"):
            for authored in (False, True):
                for image, details, error in cases:
                    with (
                        self.subTest(
                            version=version,
                            authored=authored,
                            image=image,
                            error=error,
                        ),
                        tempfile.TemporaryDirectory() as temporary,
                    ):
                        project = Path(temporary).resolve()
                        if authored:
                            (project / ".anechoic_tmp").mkdir()
                            (project / "LAYER_1_META_ONTOLOGY_C9").mkdir()
                        stage = load(version)
                        stage.bounded_run = Mock(return_value=details)
                        stage._run = Mock(return_value="fingerprint")
                        admitted_before = version == "before" and (
                            not authored or image == ""
                        )
                        if admitted_before:
                            self.assertEqual(
                                stage.stage_model(project, project, 5, image),
                                "fingerprint",
                            )
                            stage._run.assert_called_once()
                        else:
                            with self.assertRaisesRegex(ValueError, error):
                                stage.stage_model(project, project, 5, image)
                            stage._run.assert_not_called()

    def test_valid_predecessor_compiles_on_both_paths(self):
        for version in ("before", "fixed"):
            for authored in (False, True):
                with (
                    self.subTest(version=version, authored=authored),
                    tempfile.TemporaryDirectory() as temporary,
                ):
                    project = Path(temporary).resolve()
                    if authored:
                        (project / ".anechoic_tmp").mkdir()
                        (project / "LAYER_1_META_ONTOLOGY_C9").mkdir()
                    stage = load(version)
                    stage.bounded_run = Mock(
                        side_effect=[
                            inspect(),
                            subprocess.CompletedProcess([], 0, "[]", ""),
                        ]
                    )

                    def compile_model(command, deadline):
                        if authored:
                            (Path(command[-1]) / "model.json").write_text(
                                '{"declarations": []}'
                            )
                        return "fingerprint"

                    stage._run = Mock(side_effect=compile_model)
                    with patch.object(stage.shutil, "copyfile"):
                        self.assertEqual(
                            stage.stage_model(project, project, 5, IMAGE),
                            ("fingerprint"),
                        )
                    stage._run.assert_called_once()
                    self.assertEqual(
                        stage.bounded_run.call_count,
                        2 if authored else int(version == "fixed"),
                    )

    def test_no_predecessor_compiles_on_both_paths(self):
        for version in ("before", "fixed"):
            for authored in (False, True):
                with (
                    self.subTest(version=version, authored=authored),
                    tempfile.TemporaryDirectory() as temporary,
                ):
                    project = Path(temporary).resolve()
                    if authored:
                        (project / ".anechoic_tmp").mkdir()
                        (project / "LAYER_1_META_ONTOLOGY_C9").mkdir()
                    stage = load(version)
                    stage.bounded_run = Mock()
                    stage._run = Mock(return_value="fingerprint")
                    self.assertEqual(
                        stage.stage_model(project, project, 5, None),
                        ("fingerprint"),
                    )
                    stage._run.assert_called_once()
                    stage.bounded_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
