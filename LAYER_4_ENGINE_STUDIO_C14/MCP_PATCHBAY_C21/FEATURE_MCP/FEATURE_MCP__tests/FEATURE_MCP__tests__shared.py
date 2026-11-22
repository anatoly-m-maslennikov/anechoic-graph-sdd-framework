"""Prepare a disposable native Project from its active declaration carriers."""

from pathlib import Path
import shutil

from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project

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
