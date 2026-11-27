"""Prepare a disposable native Project from its active declaration carriers."""

import os
from pathlib import Path
import shutil
import sys
import tempfile
import yaml

from .workbench_docker_support import (
    IMAGE_DEADLINES,
    defer_container_cleanup as defer_container_cleanup,
    docker_deadline_env as docker_deadline_env,
    image_deadline_mode,
    image_mcp_transport as image_mcp_transport,
    image_timeout as image_timeout,
    observing as observing,
    request as request,
    run_browser,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import WORKBENCH_PATH, select_runtime_project
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.packaged_image_fixture__pub import (
    packaged_identity_reader as packaged_identity_reader,
)

ROOT = Path(__file__).resolve().parents[4]
CONTROL = '_anechoic_anechoic'
ONTOLOGY = Path('ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9')


def project(root):
    source, control = ROOT / CONTROL, root / CONTROL
    control.mkdir()
    manifest = 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
    text = (ROOT / manifest).read_text(encoding='utf-8')
    (root / manifest).write_text(text.replace("'storage': 'disk'", "'storage': 'memory'")
                                 .replace("'journal': {'storage': 'duckdb'}", "'journal': {'storage': 'files'}"))
    for relative in ('01_TIER_1_ARCHITECTURE/AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md',
                     '01_TIER_1_ARCHITECTURE/AN-S-4909-SPEC-COMPONENT_MANIFEST--declare-ontology-score.md',
                     ONTOLOGY.parent / '01_TIER_1_ARCHITECTURE/AN-S-3040-SPEC-COMPONENT_MANIFEST--declare-meta-ontology.md'):
        dest = control / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, dest)
    for directory, pattern in ((ONTOLOGY, '*.md'), (ONTOLOGY / '_SPEC', '*.md'), (ONTOLOGY / '_DOM/CONT', '*.md'),
                               (ONTOLOGY / '_DES', '*-MANIFEST_PROPERTY--*.md'),
                               (Path('__PROJECT_CONFIG/CUSTOM_MODEL'), '*.md')):
        dest = control / directory
        dest.mkdir(parents=True, exist_ok=True)
        for path in (source / directory).glob(pattern):
            shutil.copy2(path, dest / path.name)
    (control / 'LAYER_4_ENGINE_STUDIO_C14').mkdir()
    selection = select_runtime_project(root, CONTROL)
    for relative in selection.parameters['runtime']['iwe_console']['import_graph'].get('python_roots', ()):
        (root / relative).mkdir(parents=True, exist_ok=True)
    return selection


def write_manifest(_case, control, *, name="Anechoic", prefix="AN", component="C00", parameters=None):
    path = control / f"{prefix}-S-001-PROJECT_MANIFEST--declare.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = {"identity": {"atom_id": f"{prefix}-S-001"},
              "context": {"container": {"component": component}, "tier": -1,
                          "template": "project_manifest"},
              "state": {"status": "active", "version": 1}}
    runtime = f", parameters={parameters!r}" if parameters is not None else ""
    path.write_text(f"---\n{yaml.safe_dump(header)}---\n\n## Claim\n\n### Formal Claim\n\n```python\n"
                    "from anechoic.formal_claims import declare_entity\n"
                    "from anechoic.model import ProjectManifest\n"
                    f"declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name={name!r}, "
                    f"prefix={prefix!r}{runtime}))\n```\n", encoding="utf-8")
    return path


def run_workbench_browser(case, selection=()):
    repository = Path(__file__).resolve().parents[4]
    frontend = Path(__file__).resolve().parents[3] / "IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND"
    environment = os.environ | {
        IMAGE_DEADLINES: image_deadline_mode(os.environ),
        "C46_FORMAL_PYTHON": sys.executable,
        "PYTHONDONTWRITEBYTECODE": "1",
        "WORKBENCH_LIFECYCLE_E2E": "1",
        "WORKBENCH_E2E_URL": f"{case.url}{WORKBENCH_PATH}/Anechoic",
        "PLAYWRIGHT_BROWSERS_PATH": str(repository / ".anechoic_tmp/workbench/playwright-browsers"),
    }
    launch = run_browser(
        case.container,
        ["node", str(frontend / "FEATURE_IWE_CONSOLE_FRONTEND__tests/pinned_chromium_probe.ts")],
        cwd=frontend, env=environment, bounded_timeout=None,
    )
    case.assertEqual(0, launch.returncode,
                     f"Pinned Chromium could not launch. Run the image tests in a host context that permits "
                     f"Chromium processes.\n{launch.stdout}{launch.stderr}")
    print(f"Pinned Chromium {launch.stdout.strip()}", flush=True)
    reports = repository / ".anechoic_tmp/test_reports"
    reports.mkdir(parents=True, exist_ok=True)
    output = tempfile.mkdtemp(prefix="workbench-browser-", dir=reports)
    command = ["node", "node_modules/@playwright/test/cli.js", "test", "--config",
               "FEATURE_IWE_CONSOLE_FRONTEND__tests/playwright.config.ts", "--output", output,
               "--trace", "retain-on-failure", *selection]
    if environment[IMAGE_DEADLINES] == "1":
        command.extend(("--global-timeout", "115000"))
    try:
        result = run_browser(case.container, command, cwd=frontend, env=environment)
    except Exception as error:
        error.add_note(f"Browser artifacts: {output}")
        raise
    case.assertEqual(0, result.returncode, f"{result.stdout}{result.stderr}\nBrowser artifacts: {output}")
