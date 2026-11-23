from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).resolve().parents[1] / "compile_applicable_methodology.py"
SPEC = importlib.util.spec_from_file_location("compile_applicable_methodology", TOOL)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import SETTINGS_PATH


def carrier(atom_id: str, version: int = 1, extra: str = "", body: str = "claim", relations: str = "{}") -> bytes:
    return (
        "---\n"
        f"atom_id: {atom_id}\n"
        "cce_version: cce_1\n"
        "cce_form: obligation\n"
        "status: Active\n"
        f"{extra}"
        f"version: {version}\n"
        "updated_at: 2026-08-27 00:00:00 +0400\n"
        f"relations: {relations}\n"
        "---\n"
        f"# {atom_id}\n\n{body}\n"
    ).encode()


def definition_carrier(atom_id: str, term: str, subject_path: str | None = None) -> bytes:
    governed = subject_path or term
    return (
        "---\n"
        f"atom_id: {atom_id}\n"
        "cce_version: cce_1\n"
        "cce_form: definition\n"
        "subjects:\n"
        "  governs:\n"
        "    continuant:\n"
        f"      - {json.dumps(governed)}\n"
        "  depends_on:\n"
        "    continuant: []\n"
        "status: Active\n"
        "version: 1\n"
        "updated_at: 2026-08-29 00:00:00 +0400\n"
        "relations: {}\n"
        "---\n"
        f"# Define {term}\n\n"
        f"{term} definition.\n"
    ).encode()


def term_definition_carrier(atom_id: str, subject: str) -> bytes:
    return (
        f"---\natom_id: {atom_id}\n"
        "context:\n  role: Method\n  form: Term Definition\n  topics:\n"
        f"    main_subject: {json.dumps(subject)}\n"
        "status: Active\nversion: 1\nrelations: {}\n---\n"
        f"# {atom_id}\n"
    ).encode()


class CompilerFixture(unittest.TestCase):
    def setUp(self) -> None:
        from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import write_scope_unit_declarations

        temporary = Path.cwd() / ".anechoic_tmp/compiler-tests"
        temporary.mkdir(parents=True, exist_ok=True)
        self.temp = Path(tempfile.mkdtemp(prefix="case-", dir=temporary))
        settings = self.temp / SETTINGS_PATH
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(
            '[project]\nname = "anechoic"\n[paths]\ncontrol_root = ".anechoic_anechoic"\n'
        )
        self.declarations = write_scope_unit_declarations(
            self.temp,
            (
                {"scope_unit_name": "METHODOLOGY_SOURCES", "parent": "PROJECT", "scope_unit_type": "Unordered"},
                {"scope_unit_name": "CORE_META_MODEL", "parent": "METHODOLOGY_SOURCES", "scope_unit_type": "Unordered"},
                {"scope_unit_name": "INSTALLED_EXTENSIONS", "parent": "METHODOLOGY_SOURCES", "scope_unit_type": "Unordered"},
                {"scope_unit_name": "PROJECT_CONFIGURATION", "parent": "METHODOLOGY_SOURCES", "scope_unit_type": "Unordered"},
            ),
        )
        self.source = Path(self.declarations["METHODOLOGY_SOURCES"]["authority_path"])
        self.output = Path(self.declarations["METHODOLOGY_SOURCES"]["delivery_path"])
        self.layers = {
            name: Path(self.declarations[name]["authority_path"])
            for name, _, _ in module.LAYERS
        }
        self.logical_layers = dict(zip(
            ("001_CORE_META_MODEL", "002_INSTALLED_EXTENSIONS", "003_PROJECT_CONFIGURATION"),
            ("CORE_META_MODEL", "INSTALLED_EXTENSIONS", "PROJECT_CONFIGURATION"),
            strict=True,
        ))
        for path in self.layers.values():
            path.mkdir(parents=True)
        (self.layers["INSTALLED_EXTENSIONS"] / ".gitkeep").write_text("")


    def tearDown(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)


    def write(self, layer: str, role: str, name: str, data: bytes) -> Path:
        path = self.layers[self.logical_layers.get(layer, layer)] / role / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


    def invoke(self, *arguments: str) -> tuple[int, dict[str, object]]:
        self.assertIn(arguments, {(), ("--apply",)})
        report, candidates, snapshot = module.compile_report(self.temp)
        if report["can_apply"] and arguments == ("--apply",):
            module.replace_outputs_atomically(self.temp, module.stage_outputs(self.temp, candidates, snapshot))
        return (0 if report["can_apply"] else 2), report


    def output_digest(self) -> dict[str, bytes]:
        output = self.temp / self.output
        return {
            path.relative_to(output).as_posix(): path.read_bytes()
            for path in sorted(output.rglob("*.md"))
        }
