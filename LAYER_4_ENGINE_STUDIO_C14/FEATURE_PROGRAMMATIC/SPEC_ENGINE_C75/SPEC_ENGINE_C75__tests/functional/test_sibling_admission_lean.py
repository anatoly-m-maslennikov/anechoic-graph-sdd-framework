"""Replay C89 sibling admission on the translated implementation."""

import json
import os
import subprocess
import sys
import unittest
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

STUDIO = Path(__file__).resolve().parents[4]
SOURCE = (
    STUDIO
    / "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75"
    / "LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_SPEC_COMPARISON_C88"
    / "DELEGATION_VERIFICATION_C89/sibling_delegation__pub.py"
)
TOOL = "ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74"
CONFIGURATION = ("AUTOFORM_CHECKOUT", "JOERN_HOME", "LEAN_PATH")
WITNESS = Path(__file__).with_name("sibling_admission.lean")


def _translate(source, implementation):
    env = os.environ | {
        "AUTOFORM_PYTHON": sys.executable,
        "PATH": os.pathsep.join(
            (str(Path(sys.executable).parent), os.environ.get("PATH", ""))
        ),
    }
    translation = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            f"{TOOL}.code_to_lean",
            str(source),
            "--sha256",
            sha256(source.read_bytes()).hexdigest(),
            "--output",
            str(implementation),
        ],
        cwd=STUDIO,
        env=env,
        capture_output=True,
        text=True,
        timeout=1800,
        check=False,
    )
    if translation.returncode:
        raise AssertionError(translation.stderr + translation.stdout)


def _admission_results(source, work):
    implementation = work / "Implementation.lean"
    _translate(source, implementation)
    check = work / "Admission.lean"
    check.write_text(
        "import Lean\n"
        + implementation.read_text()
        + "\n"
        + WITNESS.read_text(),
        encoding="utf-8",
    )
    lean = os.environ.get("ANECHOIC_TEST_LEAN", "lean")
    result = subprocess.run(
        [lean, str(check)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr + result.stdout)
    return json.loads(result.stdout)


@unittest.skipUnless(
    all(os.environ.get(name) for name in CONFIGURATION),
    "Autoform and its Lean libraries are not configured",
)
class SiblingAdmissionLeanTests(unittest.TestCase):
    def test_translated_admission_detects_an_ignored_interface(self):
        expected = {
            "matching_list": "accepted",
            "wrong_parent": "ValueError",
            "wrong_provider": "ValueError",
            "wrong_interface": "ValueError",
            "wrong_transport": "ValueError",
            "matching_map": "accepted",
        }
        source = SOURCE.read_bytes()
        interface_check = (
            b'            or client.get("interface", name) != interface\n'
        )
        self.assertEqual(1, source.count(interface_check))
        with TemporaryDirectory() as directory:
            work = Path(directory)
            implementation = work / SOURCE.name
            implementation.write_bytes(source)
            self.assertEqual(
                expected, _admission_results(implementation, work)
            )
            implementation.write_bytes(source.replace(interface_check, b""))
            self.assertEqual(
                {**expected, "wrong_interface": "accepted"},
                _admission_results(implementation, work),
            )
