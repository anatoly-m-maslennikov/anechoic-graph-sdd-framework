"""Fixtures for the Beta worker CLI tests."""

from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
from runpy import run_module
from subprocess import CompletedProcess
import sys
from unittest.mock import patch


def generation_fixture(directory):
    root = Path(directory).resolve() / "project"
    control = root / "_anechoic_anechoic"
    control.mkdir(parents=True)
    manifest = root / "AN-S-1-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
    manifest.write_text(
        "---\natom_family: SPEC\natom_id: AN-S-1\ncontainer:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nAnechoic\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\n"
        "from anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Anechoic', prefix='AN'))\n```\n",
    )
    output = Path(directory).resolve() / "generation"
    output.mkdir()
    return (
        {
            "root": str(root),
            "control_root": control.name,
            "manifest_path": manifest.name,
            "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
            "project_prefix": "AN",
        },
        output,
        manifest,
    )


def command_with_fixture(module, payload, *arguments):
    """Run the command entry point while its external peers can be replaced by fixtures."""
    stdout, stderr = StringIO(), StringIO()
    argv = [module, *arguments]
    with (
        patch.object(sys, "argv", argv),
        patch.object(sys, "stdin", StringIO(json.dumps(payload))),
        patch.object(sys, "dont_write_bytecode", True),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
    ):
        try:
            run_module(module, run_name="__main__")
        except SystemExit as exit_requested:
            status = exit_requested.code
        else:
            status = 0
    return CompletedProcess(argv, status, stdout.getvalue(), stderr.getvalue())
