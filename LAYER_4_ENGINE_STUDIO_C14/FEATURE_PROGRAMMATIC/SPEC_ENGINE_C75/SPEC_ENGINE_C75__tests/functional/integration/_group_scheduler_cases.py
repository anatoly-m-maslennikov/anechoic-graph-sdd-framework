import hashlib
import os
import tempfile
from pathlib import Path

from ....LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_4_SPEC_COMPARISON_C88._package__shared import (
    check_group_spec,
)  # fmt: skip

LEAN = (
    os.environ.get("ANECHOIC_TEST_LEAN")
    or os.environ.get("LEAN_BIN")
    or "lean"
)

ROOT = Path(__file__).resolve().parents[6]
TOOLS = (
    ROOT / "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/"
    "FEATURE_PROGRAMMATIC_C15/FEATURE_TOOLS_C16"
)
GROUP = TOOLS / "FEATURE_GROUP_SCHEDULERS_C32"
SCHEDULER_FILES = (
    (
        TOOLS
        / (
            "01_draft/AN-S-3070@4-draft-SPEC-COMPONENT_MANIFEST--"
            "declare-schedulers.md"
        ),
        "AN-S-3070",
        4,
        "draft",
        "C16",
        "91058117b53fa2bb5931a32a4599ff7dc3eceab7a6430f75594e874148147af2",
    ),
    (
        GROUP
        / (
            "01_draft/AN-S-5059@1-draft-DES-SOLUTION--"
            "group-batch-and-workflow-schedulers.md"
        ),
        "AN-S-5059",
        1,
        "draft",
        "C32",
        "98c484c9585c05400a856a3874aa1f643209f445e7809ef4a6ef149a0d89a863",
    ),
    (
        GROUP
        / (
            "01_TIER_1_ARCHITECTURE/AN-S-3074-SPEC-COMPONENT_MANIFEST--"
            "declare-batch-scheduler.md"
        ),
        "AN-S-3074",
        4,
        "active",
        "C32",
        "3f9afd6ba412be2fd31b218b258f86bf5eb7efc782c6ceebe551abf3a01777d6",
    ),
    (
        GROUP
        / (
            "01_TIER_1_ARCHITECTURE/AN-S-3075-SPEC-COMPONENT_MANIFEST--"
            "declare-workflow-scheduler.md"
        ),
        "AN-S-3075",
        4,
        "active",
        "C32",
        "574850878f00dbddf87ec3136e42ee6e05813c40f5d3328dccb28afe06eb5f9d",
    ),
)


def scheduler_inputs(root, *, swapped=False):
    pins = []
    for path, atom, version, status, owner, digest in SCHEDULER_FILES:
        content = path.read_bytes()
        if swapped and atom in ("AN-S-3070", "AN-S-5059"):
            content = content.replace(
                b"'batch_scheduler': 'C41', 'workflow_scheduler': 'C42'",
                b"'batch_scheduler': 'C42', 'workflow_scheduler': 'C41'",
            )
            digest = hashlib.sha256(content).hexdigest()
        (root / path.name).write_bytes(content)
        pins.append(
            {
                "path": path.name,
                "atom_id": atom,
                "version": version,
                "status": status,
                "container_component": owner,
                "sha256": digest,
            }
        )
    providers = {
        "batch_scheduler": {
            "component_id": "C41",
            "name": "BATCH_SCHEDULER",
            "manifest": pins[2],
        },
        "workflow_scheduler": {
            "component_id": "C42",
            "name": "WORKFLOW_SCHEDULER",
            "manifest": pins[3],
        },
    }
    return pins, providers


class GroupSchedulerCases:
    def test_reviewed_scheduler_role_witness(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins, providers = scheduler_inputs(root)
            args = (root, "C32", pins[0], None, pins[1])
            options = {"structure_children": ("C41", "C42"), "lean": LEAN}
            result = check_group_spec(
                *args, role_providers=providers, **options
            )
            self.assertEqual("matched", result["status"])
            self.assertEqual("complete", result["role_provider_coverage"])
            self.assertEqual(
                "matched", result["manifest_consistency"]["status"]
            )
            self.assertIn(
                {
                    "key": "entry_points",
                    "left": [],
                    "right": [],
                    "status": "matched",
                },
                result["directions"]["manifest_solution"]["facts"],
            )
            self.assertEqual(
                pins[2], result["role_provider_sources"]["batch_scheduler"]
            )
            legacy = check_group_spec(*args, **options)
            self.assertEqual("matched", legacy["status"])
            self.assertEqual("not_selected", legacy["role_provider_coverage"])
            partial = check_group_spec(
                *args,
                role_providers={
                    "batch_scheduler": providers["batch_scheduler"]
                },
                **options,
            )
            self.assertEqual("unresolved", partial["status"])
            self.assertEqual("partial", partial["role_provider_coverage"])
            self._check_swapped_roles(root, providers, options)

    def _check_swapped_roles(self, root, providers, options):
        pins, _ = scheduler_inputs(root, swapped=True)
        swapped = check_group_spec(
            root,
            "C32",
            pins[0],
            None,
            pins[1],
            role_providers=providers,
            **options,
        )
        self.assertEqual("conflicting", swapped["status"])
        self.assertEqual(
            "conflicting", swapped["manifest_consistency"]["status"]
        )
        facts = swapped["directions"]["manifest_solution"]["facts"]
        self.assertEqual(
            {"role.batch_scheduler", "role.workflow_scheduler"},
            {fact["key"] for fact in facts if fact["status"] == "conflicting"},
        )

    def test_role_witness_rejects_invalid_identity_and_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins, providers = scheduler_inputs(root)
            args = (root, "C32", pins[0], None, pins[1])
            batch = providers["batch_scheduler"]
            for replacement in (
                {**batch, "name": "WORKFLOW_SCHEDULER"},
                {**batch, "component_id": "C42"},
                {**batch, "component_id": "C99"},
                {
                    **batch,
                    "manifest": {
                        k: v for k, v in pins[2].items() if k != "sha256"
                    },
                },
                {**batch, "manifest": {**pins[2], "sha256": "0" * 64}},
                {
                    **batch,
                    "manifest": {**pins[2], "container_component": "C16"},
                },
            ):
                with (
                    self.subTest(replacement=replacement),
                    self.assertRaises(ValueError),
                ):
                    check_group_spec(
                        *args,
                        structure_children=("C41", "C42"),
                        role_providers={
                            **providers,
                            "batch_scheduler": replacement,
                        },
                        lean=LEAN,
                    )
            self._check_indirect_provider(root, pins, args, providers)

    def _check_indirect_provider(self, root, pins, args, providers):
        batch = providers["batch_scheduler"]
        path = root / pins[2]["path"]
        content = path.read_bytes().replace(
            b"component: C32", b"component: C16"
        )
        path.write_bytes(content)
        pin = {
            **pins[2],
            "container_component": "C16",
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        providers["batch_scheduler"] = {**batch, "manifest": pin}
        with self.assertRaisesRegex(ValueError, "not a direct child"):
            check_group_spec(
                *args,
                structure_children=("C41", "C42"),
                role_providers=providers,
                lean=LEAN,
            )
