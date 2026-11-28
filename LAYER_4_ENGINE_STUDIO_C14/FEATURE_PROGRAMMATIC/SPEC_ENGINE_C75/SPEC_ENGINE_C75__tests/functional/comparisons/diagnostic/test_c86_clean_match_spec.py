import copy
import os
import re
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.components.components__shared import (
    parse_component_manifest,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    parse_trace_contract,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    outcome_cases,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    SPECIFICATION_MODEL_C85._package__shared import (
    normalize_workflow,
    parse_workflow,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    _package__shared import (
    compare_trace_workflow,
)  # fmt: skip


def _matched_framing():
    root = next(
        path
        for path in Path(__file__).resolve().parents
        if (path / "_anechoic_anechoic").is_dir()
    )
    drafts = (
        root / "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/"
        "FEATURE_PROGRAMMATIC_C15/SPEC_ENGINE_C75"
    )
    active = list((drafts / "_SPEC").glob("AN-S-4933-*.md"))
    (manifest_path,) = active or list(drafts.rglob("AN-S-4933@1-draft-*.md"))
    manifest = manifest_path.read_text()
    contract, solution = [
        next(drafts.rglob(f"AN-S-{number}@1-draft-*.md")).read_text()
        for number in (4960, 4961)
    ]
    fields, _ = parse_component_manifest(manifest)
    cases, _ = outcome_cases(fields["boundaries"])
    manifest_match = next(
        case for case in cases if case["output"] == "matched"
    )
    source = re.search(
        r"```python trace\n(.*?)\n```", contract, re.DOTALL
    ).group(1)
    contract_match = parse_trace_contract(source)
    source = re.search(r"```python\n(.*?)\n```", solution, re.DOTALL).group(1)
    return manifest_match, contract_match, parse_workflow(source)


class CleanMatchSpecTests(unittest.TestCase):
    def test_findings_cannot_precede_a_matched_return(self):
        manifest_match, contract_match, workflow = _matched_framing()
        invalid = copy.deepcopy(workflow)
        states = invalid["machine"]["states"]
        edge = copy.deepcopy(states["checking"]["on"]["unresolved_effect"])
        edge["target"] = "known_unresolved"
        states["checking"]["on"]["unresolved_is_present"] = edge
        states["known_unresolved"] = {
            "on": {
                "acknowledge_validation": copy.deepcopy(
                    states["checking"]["on"]["matched_effect"]
                )
            }
        }
        lean = (
            os.environ.get("ANECHOIC_TEST_LEAN")
            or os.environ.get("LEAN_BIN")
            or "lean"
        )
        for case in (manifest_match, contract_match):
            for candidate, expected in (
                (workflow, "matched"),
                (invalid, "conflicting"),
            ):
                normalized = {
                    "action": candidate["action"],
                    **normalize_workflow(candidate["machine"]),
                }
                result = compare_trace_workflow(case, normalized, lean=lean)
                self.assertEqual(expected, result["status"], result)
