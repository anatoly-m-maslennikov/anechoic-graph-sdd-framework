import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    _package__shared import load_boundary_model
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import outcome_cases
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84.\
    _package__shared import compile_lean
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import compare_obligations, compare_trace_workflow
# fmt: on

_C94_SPECS = Path(
    "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/"
    "SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94"
)
_SOURCES = (
    (
        "01_TIER_1_ARCHITECTURE/"
        "AN-S-4935-SPEC-COMPONENT_MANIFEST--declare-spec-comparison.md",
        "AN-S-4935",
        "C94",
        "929c914afb640966de04ce2f96420b484a3eaaab991066c2eaf3203d10b2d9cd",
    ),
    (
        "LAYER_4_SPEC_COMPARISON_C88/"
        "AN-S-5030-DES-SOLUTION--compare-formal-spec-obligations.md",
        "AN-S-5030",
        "C88",
        "ad6af299477be8d524d398f808d99acd79b9ebc96361d7bb44a413dfe0d1822d",
    ),
)


class ComparisonDirectionTests(unittest.TestCase):
    def test_each_comparison_is_a_required_effect(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean unavailable")
        root = Path(__file__).resolve().parents[7]
        pins = []
        for relative, atom, component, digest in _SOURCES:
            path = _C94_SPECS / relative
            pins.append(
                {
                    "path": path.as_posix(),
                    "atom_id": atom,
                    "version": 1,
                    "status": "active",
                    "container_component": component,
                    "sha256": digest,
                }
            )
        compiled = compile_lean(load_boundary_model(root, "C88", *pins))
        self.assertEqual(
            ["manifest", "contract", "solution"], compiled["compiled_roles"]
        )
        contract, workflow = (
            compiled["claims"]["contract"],
            compiled["claims"]["solution"],
        )
        targets = (
            "C88.manifest_contract",
            "C88.manifest_solution",
            "C88.contract_solution",
        )
        expected = {(target, "compared") for target in targets}
        cases, _ = outcome_cases(compiled["claims"]["manifest"]["boundaries"])
        self.assertEqual(expected, set(cases[0]["must_effect"]))
        self.assertEqual(expected, set(contract["must_effect"]))
        self.assertEqual(
            "matched",
            compare_trace_workflow(contract, workflow, lean=lean)["status"],
        )
        self._assert_public_comparison(pins, contract, lean)
        self._assert_required_effects(contract, workflow, targets, lean)

    def _assert_required_effects(self, contract, workflow, targets, lean):
        for target in targets:
            with self.subTest(target=target):
                mutant = copy.deepcopy(workflow)
                for state in mutant["states"]:
                    for transition in state["transitions"]:
                        if transition["expect"].get("target") == target:
                            transition["expect"]["target"] = "missing"
                report = compare_trace_workflow(contract, mutant, lean=lean)
                self.assertEqual("conflicting", report["status"])
                self.assertTrue(
                    any(
                        f["key"] == "must_effect"
                        and f["left"][0] == target
                        and f["status"] == "conflicting"
                        for f in report["facts"]
                    )
                )

    def _assert_public_comparison(self, pins, contract, lean):
        sources = {
            "manifest": pins[0],
            "contract": pins[0],
            "solution": pins[1],
        }
        obligations = {
            "manifest": {"z": 1, "m": 8, "a": 2},
            "contract": {"z": 1, "a": 2},
            "solution": {"z": 3, "a": 2},
        }
        report = compare_obligations(sources, obligations, lean=lean)
        directions = [
            target.removeprefix("C88.")
            for target, _ in contract["must_effect"]
        ]
        self.assertEqual(directions, list(report["directions"]))

        def fact(key, left, right, status):
            return {"key": key, "left": left, "right": right, "status": status}

        a = fact("a", 2, 2, "matched")
        m = fact("m", 8, None, "unresolved")
        z_equal = fact("z", 1, 1, "matched")
        z_conflict = fact("z", 1, 3, "conflicting")
        expected = {
            "manifest_contract": {
                "status": "unresolved",
                "facts": [a, m, z_equal],
            },
            "manifest_solution": {
                "status": "conflicting",
                "facts": [a, m, z_conflict],
            },
            "contract_solution": {
                "status": "conflicting",
                "facts": [a, z_conflict],
            },
        }
        self.assertEqual(
            {
                "sources": sources,
                "status": "conflicting",
                "directions": expected,
            },
            report,
        )


_ASSETS = Path(__file__).parents[2] / "assets/c88_public_chain.json"
_CLI = (
    "ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare"
)
_TRANSLATOR_ENV = ("AUTOFORM_CHECKOUT", "JOERN_HOME", "LEAN_PATH")


class PublicComparisonCLITests(unittest.TestCase):
    @unittest.skipUnless(
        all(os.environ.get(name) for name in _TRANSLATOR_ENV),
        "Autoform and its Lean libraries are not configured",
    )
    def test_pinned_mixed_witness_and_rejections(self):
        root = Path(__file__).resolve().parents[7]
        studio = root / "LAYER_4_ENGINE_STUDIO_C14"
        request = json.loads(_ASSETS.read_text())["request"]
        lean = os.environ.get("ANECHOIC_TEST_LEAN", "lean")
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            path = folder / "request.json"
            path.write_text(json.dumps(request), encoding="utf-8")
            code, report = self._run_comparison(root, studio, path, lean)
            self.assertEqual(
                (0, "no_mismatch_in_cases"), (code, report["status"]), report
            )
            self._assert_mixed_report(request, report["public_report"])
            staged = folder / "stale"
            for pin in (request["manifest"], request["solution"]):
                source = root / pin["path"]
                target = staged / pin["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            relative = next(iter(request["implementation_sha256"]))
            source = (
                studio
                / "FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75"
                / "LAYER_2_FORMAL_SPECIFICATION_C94"
                / relative
            )
            target = staged / source.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes() + b"\n# changed\n")
            code, stale = self._run_comparison(staged, studio, path, lean)
            self.assertEqual((1, "unresolved"), (code, stale["status"]), stale)
            self.assertIsNone(stale["public_report"])
            self.assertIn("source digest changed", json.dumps(stale))

    def _run_comparison(self, target, studio, path, lean):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                _CLI,
                "--root",
                str(target),
                "--component",
                "C88",
                "--pins",
                str(path),
                "--lean",
                lean,
            ],
            cwd=studio,
            capture_output=True,
            text=True,
            timeout=2000,
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def _assert_mixed_report(self, request, observed):
        self.assertEqual("conflicting", observed["status"])
        sources = {
            "manifest": request["manifest"],
            "solution": request["solution"],
            "contract": request["manifest"],
        }
        self.assertEqual(sources, observed["sources"])
        directions = observed["directions"]
        self.assertEqual(
            ["manifest_contract", "manifest_solution", "contract_solution"],
            list(directions),
        )
        self.assertEqual(
            ["unresolved", "conflicting", "conflicting"],
            [row["status"] for row in directions.values()],
        )
        match = ("a", 2, 2, "matched")
        missing = ("m", 8, None, "unresolved")
        conflict = ("z", 1, 3, "conflicting")
        self.assertEqual(
            [
                [match, missing, ("z", 1, 1, "matched")],
                [match, missing, conflict],
                [match, conflict],
            ],
            [
                [
                    (fact["key"], fact["left"], fact["right"], fact["status"])
                    for fact in direction["facts"]
                ]
                for direction in directions.values()
            ],
        )

    def test_worker_classification_proof_rejects_swapped_branches(self):
        lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which("lean")
        if not lean:
            self.skipTest("Lean unavailable")
        worker = json.loads(_ASSETS.read_text())["worker"]
        digest = (
            "ecd51442045a764fe51a9bceb74f248d4b86c48b5d6d800cc8fe909e5a3276b6"
        )
        self.assertEqual(digest, hashlib.sha256(worker.encode()).hexdigest())
        branch = 'then "matched" else "conflicting"'
        self.assertEqual(1, worker.count(branch))
        proof = """
theorem matching (key value : String) (right : List (String × String))
    (found : String × String)
    (h : right.find? (fun item => item.1 == key) = some found)
    (eqv : sameValue found.2 value = true) :
    compare [(key,value)] right = ["matched"] := by
  unfold _root_.compare
  simp [h, eqv]
theorem conflicting (key value : String) (right : List (String × String))
    (found : String × String)
    (h : right.find? (fun item => item.1 == key) = some found)
    (neq : sameValue found.2 value = false) :
    compare [(key,value)] right = ["conflicting"] := by
  unfold _root_.compare
  simp [h, neq]
"""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "Worker.lean"
            mutant = worker.replace(
                branch, 'then "conflicting" else "matched"'
            )
            for source, expected in ((worker, True), (mutant, False)):
                path.write_text(source + proof, encoding="utf-8")
                result = subprocess.run(
                    [lean, "-DwarningAsError=true", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                output = result.stdout + result.stderr
                self.assertEqual(expected, result.returncode == 0, output)
                if not expected:
                    self.assertEqual(2, output.count("unsolved goals"), output)
