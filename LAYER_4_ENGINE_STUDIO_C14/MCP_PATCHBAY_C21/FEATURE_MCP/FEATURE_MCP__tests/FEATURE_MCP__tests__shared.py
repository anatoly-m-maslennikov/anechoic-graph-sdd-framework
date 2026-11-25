"""Prepare a disposable native Project from its active declaration carriers."""

from pathlib import Path
import shutil
import yaml

from .workbench_docker_support import (
    defer_container_cleanup as defer_container_cleanup,
    docker_deadline_env as docker_deadline_env,
    image_mcp_transport as image_mcp_transport,
    image_timeout as image_timeout,
    observing as observing,
    request as request,
)

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import select_runtime_project
from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__tests.packaged_image_fixture__pub import (
    packaged_identity_reader as packaged_identity_reader,
)

ROOT = Path(__file__).resolve().parents[4]
CONTROL = '_anechoic_anechoic'


def project(root):
    source, control = ROOT / CONTROL, root / CONTROL
    control.mkdir()
    manifest = 'AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md'
    text = (ROOT / manifest).read_text(encoding='utf-8')
    (root / manifest).write_text(text.replace("'storage': 'disk'", "'storage': 'memory'")
                                 .replace("'journal': {'storage': 'duckdb'}", "'journal': {'storage': 'files'}"))
    (control / '_SPEC').mkdir()
    for name in ('AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md',
                 'AN-S-3040-SPEC-COMPONENT_MANIFEST--declare-meta-ontology.md'):
        shutil.copy2(source / '_SPEC' / name, control / '_SPEC' / name)
    for name in ('LAYER_1_META_ONTOLOGY_C9', 'LAYER_1_META_ONTOLOGY_C9/_SPEC', '__PROJECT_CONFIG/CUSTOM_MODEL'):
        dest = control / name
        dest.mkdir(parents=True, exist_ok=True)
        for path in (source / name).glob('*.md'):
            shutil.copy2(path, dest / path.name)
    (control / 'LAYER_4_ENGINE_STUDIO_C14').mkdir()
    selection = select_runtime_project(root, CONTROL)
    for relative in selection.parameters['runtime']['workbench']['import_graph'].get('python_roots', ()):
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
