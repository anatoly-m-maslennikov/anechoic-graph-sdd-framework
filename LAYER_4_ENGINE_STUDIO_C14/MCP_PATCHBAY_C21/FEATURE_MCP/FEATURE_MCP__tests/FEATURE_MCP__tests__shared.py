"""Prepare a disposable native Project from its active declaration carriers."""

from pathlib import Path
import shutil

from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import select_runtime_project
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import find_ontology_component

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
    ontology = find_ontology_component(source)
    assert ontology is not None
    for relative in ('_SPEC/AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md',
                     '_SPEC/AN-S-4909-SPEC-COMPONENT_MANIFEST--declare-ontology-score.md',
                     'ONTOLOGY_SCORE_C82/_SPEC/AN-S-3040-SPEC-COMPONENT_MANIFEST--declare-meta-ontology.md',
                     'ONTOLOGY_SCORE_C82/_SPEC/AN-S-3042-SPEC-COMPONENT_MANIFEST--declare-meta-methodology.md'):
        destination = control / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
    ontology = ontology.relative_to(source)
    for name in (ontology, ontology / '_SPEC', ontology / '_DES', '__PROJECT_CONFIG/CUSTOM_MODEL'):
        dest = control / name
        dest.mkdir(parents=True, exist_ok=True)
        for path in (source / name).glob('*.md'):
            shutil.copy2(path, dest / path.name)
    (control / 'LAYER_4_ENGINE_STUDIO_C14').mkdir()
    selection = select_runtime_project(root, CONTROL)
    for relative in selection.parameters['runtime']['workbench']['import_graph'].get('python_roots', ()):
        (root / relative).mkdir(parents=True, exist_ok=True)
    return selection
