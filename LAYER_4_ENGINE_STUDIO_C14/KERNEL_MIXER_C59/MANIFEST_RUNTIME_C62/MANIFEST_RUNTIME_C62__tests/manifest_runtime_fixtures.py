"""Fixture setup for manifest runtime tests."""

import json
from pathlib import Path
import shutil
import subprocess
from threading import Event

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    resolve_native_project,
)
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.\
    model_host_CS2__shared import reviewed_native_model  # fmt: skip
from .kernel_probe import write_reviewed_declarations

ROOT = Path(__file__).resolve().parents[4]


ADMITTED_MODEL_PROBE = (
    "\n"
    "from pathlib import Path\n"
    "import sys\n"
    "from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_"
    "FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_"
    "MODEL_VALIDATION__shared import open_admitted_mode"
    "l\n"
    "generation, fingerprint, digest = Path.cwd(), *sys"
    ".argv[1:]\n"
    "with (open_admitted_model(generation, fingerprint,"
    " digest) as first,\n"
    "      open_admitted_model(generation, fingerprint,"
    " digest) as second):\n"
    "    assert {'Task', 'Subtask', 'Sub-epic', 'Epic',"
    " 'Version'} <= set(first.ticket_labels)\n"
    "    assert first._types['Component Manifest'] is n"
    "ot second._types['Component Manifest']\n"
    "assert not any('FEATURE_FORMAL_MODEL_GENERATOR' in"
    " name for name in sys.modules)\n"
)


def _copy_fixture_manifests(root, control, source, component, meta):
    shutil.copyfile(
        ROOT / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md",
        root / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md",
    )
    for relative in (
        component,
        Path(
            "01_TIER_1_ARCHITECTURE/AN-S-4909-SPEC-"
            "COMPONENT_MANIFEST--declare-ontology-score.md"
        ),
        meta,
    ):
        destination = control / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, destination)


def _runtime_fixture(root):
    control = root / "_anechoic_anechoic"
    source = ROOT / control.name
    owner = Path("ONTOLOGY_SCORE_C82")
    ontology = owner / "CONTINUANT_PITCHFORK_C9"
    component = Path(
        "01_TIER_1_ARCHITECTURE/AN-S-3039-SPEC-"
        "COMPONENT_MANIFEST--declare-engine-studio.md"
    )
    meta = owner / (
        "01_TIER_1_ARCHITECTURE/AN-S-3040-SPEC-"
        "COMPONENT_MANIFEST--declare-meta-ontology.md"
    )
    _copy_fixture_manifests(root, control, source, component, meta)
    write_reviewed_declarations(control, ROOT)
    (control / "LAYER_1_META_ONTOLOGY_C9").rename(control / ontology)
    meta = control / meta
    meta.write_text(
        meta.read_text(encoding="utf-8").replace(
            "relations:\n  CONTRIBUTES_TO:\n  - AN-S-3328\n", ""
        ),
        encoding="utf-8",
    )
    component = control / component
    original = component.read_text(encoding="utf-8")
    model = reviewed_native_model()
    selection = resolve_native_project(
        root,
        control.name,
        validate_manifest=model.validate_manifest,
        require_atom_state=model.requires_atom_state,
        require_atom_header=model.requires_atom_header,
    )
    return control, ontology, component, original, model, selection


def _runtime_observers():
    failed = Event()
    processes = []
    builders = []
    real_popen = subprocess.Popen

    def record_process(*args, **kwargs):
        process = real_popen(*args, **kwargs)
        command = args[0]
        if "-m" in command:
            module = command[command.index("-m") + 1]
            if module.endswith(
                (".model_host_CS2.host", ".structure_host_CS3.host")
            ):
                processes.append(process)
            if module == (
                "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub"
            ):
                builders.append(process)
                communicate = process.communicate

                def tracked_communicate(*args, **kwargs):
                    result = communicate(*args, **kwargs)
                    if process.returncode:
                        failed.set()
                    return result

                process.communicate = tracked_communicate
        return process

    return failed, processes, builders, record_process


def _tamper_recorder(target, generations):
    real_popen = subprocess.Popen

    def record_process(
        *args,
        _popen=real_popen,
        _generations=generations,
        _target=target,
        **kwargs,
    ):
        process = _popen(*args, **kwargs)
        command = args[0]
        if "--build-model" not in command:
            return process
        generation = Path(command[command.index("--build-model") - 1])
        _generations.append(generation)
        communicate = process.communicate

        def tamper(*args, bound_target=_target, **kwargs):
            stdout, stderr = communicate(*args, **kwargs)
            if bound_target in {"structure", "fingerprint"}:
                result = json.loads(stdout)
                if bound_target == "structure":
                    result["structure"]["components"] = []
                else:
                    result["structure"]["model_sha256"] = "b" * 64
                return json.dumps(result).encode(), stderr
            path = (
                generation / "model.json"
                if bound_target == "descriptor"
                else generation
                / "anechoic_runtime_model/component_manifest.py"
            )
            path.write_bytes(path.read_bytes() + b"\n")
            return stdout, stderr

        process.communicate = tamper
        return process

    return record_process
