"""Check staged Model selection against both selector runtimes."""

import json
import os
import subprocess
import tempfile
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[7]
ENGINE = "LAYER_4_ENGINE_STUDIO_C14"
ONTOLOGY = "LAYER_1_META_ONTOLOGY_C9"
IMAGE_ID = "sha256:" + "a" * 64
stage = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_stage"
)
stage_model = stage.stage_model


def selected_sources(project):
    from hashlib import sha256

    component = project / ONTOLOGY
    cont = component / "_DOM" / "CONT"
    des = component / "_DES"
    cont.mkdir(parents=True)
    des.mkdir()
    files = {
        cont / "cont.md": source(
            "AN-S-1",
            "DOM/CONT",
            "manifest_node",
            "concern:\n  subject: Graph\n  path: Model\n"
            "  relation: is_contained_by\n",
        ),
        des / "property.md": source("AN-S-2", "DES", "manifest_property"),
        component / "legacy.md": source(
            "AN-S-3",
            "SPEC",
            "manifest_node",
            body="## Claim scope\n\nMODEL//ANECHOIC <+ Graph\n",
        ),
        des / "excluded.md": source("AN-S-4", "DES", "other"),
        cont / "inactive.md": source(
            "AN-S-5",
            "DOM/CONT",
            "manifest_node",
            "concern:\n  subject: Graph\n  path: Model\n"
            "  relation: is_contained_by\n",
        ).replace("status: active", "status: draft"),
    }
    for path, content in files.items():
        path.write_text(content)
    expected = sorted(
        [
            [p.name, sha256(content.encode()).hexdigest()]
            for p, content in files.items()
            if p.name not in {"excluded.md", "inactive.md"}
        ]
    )
    return component, expected


class Store:
    def replace(self, rows, *args, **kwargs):
        self.rows = rows

    def run(self, query, **kwargs):
        assert (
            '"header.status"' in query
            and '"header.subject" IS NOT NULL' in query
        )
        names = sorted(
            Path(row["source_path"]).name
            for row in self.rows
            if row["header_json"]["status"] == "active"
            and row["header_json"]["subject"] is not None
        )
        return {"rows": [(name,) for name in names], "has_more": False}

    def close(self):
        self.rows = []


def source(identifier, lens, template, concern="", body=""):
    return (
        f"---\natom_family: SPEC\natom_id: {identifier}\n{concern}"
        f"structure:\n  container:\n    component: C9\n  tier: 2\n"
        f"context:\n  lens: {lens}\n  template: {template}\n"
        f"state:\n  status: active\n  version: 1\n"
        f"  updated_at: 2026-11-20T00:00:00Z\n---\n{body}"
    )


def compile_model(command, **kwargs):
    staged = Path(command[-1]) / ONTOLOGY
    assert (staged / "_DOM" / "CONT" / "cont.md").exists()
    assert (staged / "_DES" / "property.md").exists()
    (staged.parent / "model.json").write_text(
        json.dumps(
            {
                "declarations": [
                    ["cont.md@1", "", ""],
                    ["cont.md@1", "", ""],
                    ["property.md@1", "", ""],
                    ["legacy.md@1", "", ""],
                ]
            }
        )
    )
    return subprocess.CompletedProcess(command, 0, "fingerprint\n")


def test_selector_and_staged_parity_for_continuant_and_typed_properties():
    from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND import (
        native_model_selector as selector,
    )

    with tempfile.TemporaryDirectory() as temporary:
        project = Path(temporary).resolve()
        (project / ".anechoic_tmp").mkdir()
        component, expected = selected_sources(project)
        types = (
            lambda rows: None,
            lambda *args: None,
            lambda *args: None,
            Store,
        )
        with (
            patch.object(selector, "ENGINE_ROOT", ROOT / ENGINE),
            patch.object(selector, "_workbench_types", return_value=types),
        ):
            assert selector.select_claims(component) == expected
        beta_engine = project / "beta_engine"
        (beta_engine / "KERNEL_MIXER_beta_C67").mkdir(parents=True)
        extensions = os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            str(ROOT / ".anechoic_tmp/workbench/extensions"),
        )
        with (
            patch.object(selector, "ENGINE_ROOT", beta_engine),
            patch.dict(
                os.environ,
                {"ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": extensions},
            ),
        ):
            assert selector.select_claims(component) == expected

        with (
            patch.object(stage, "previous_claims", return_value=expected),
            patch.object(subprocess, "run", side_effect=compile_model),
        ):
            assert stage_model(project, project, 5, IMAGE_ID) == "fingerprint"


def load_tests(loader, tests, pattern):
    tests.addTest(
        unittest.FunctionTestCase(
            test_selector_and_staged_parity_for_continuant_and_typed_properties
        )
    )
    return tests
