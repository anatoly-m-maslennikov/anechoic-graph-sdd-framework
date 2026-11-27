"""Exercise ingested Model compilation through the compiler CLI."""

import json
import os
import subprocess
import sys
import unittest
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from unittest.mock import NonCallableMock

model_ingestion = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.model_ingestion"
)

ENGINE = Path(__file__).resolve().parents[6]
COMPILER = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub"
COMPILER_SHA256 = "a" * 64


def compile_structure(selection, model):
    return {}


def project(directory):
    root = Path(directory).resolve() / "project"
    (root / "_anechoic_anechoic").mkdir(parents=True)
    manifest = root / "AN-S-1-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
    manifest.write_text(
        "---\natom_family: SPEC\natom_id: AN-S-1\n"
        "container:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\n"
        "state:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n"
        "\n## Summary\n\nAnechoic\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', "
        "instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n"
    )
    return root, sha256(manifest.read_bytes()).hexdigest()


def compile_model(root, digest, stage, payload):
    stage = stage.resolve()
    stage.mkdir()
    command = [
        sys.executable,
        "-B",
        "-P",
        "-m",
        COMPILER,
        str(root),
        "_anechoic_anechoic",
        digest,
        str(stage),
        "--ingested-model",
        "--attest-model",
    ]
    return subprocess.run(
        command,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=ENGINE,
        env={**os.environ, "PYTHONPATH": str(ENGINE)},
        check=False,
    )


def model_args(stage, root, digest):
    return NonCallableMock(
        spec_set=[
            "generation",
            "project_root",
            "control_root",
            "project_manifest_sha256",
        ],
        generation=stage,
        project_root=root,
        control_root="_anechoic_anechoic",
        project_manifest_sha256=digest,
    )


class ModelIngestionFixture(unittest.TestCase):
    def prepare(self, tmp):
        root, digest = project(tmp)
        inputs = {
            "rows": [],
            "has_c9": False,
            "issues": [],
            "accepted_model": None,
            "compiler_sha256": COMPILER_SHA256,
        }
        return root, digest, inputs
