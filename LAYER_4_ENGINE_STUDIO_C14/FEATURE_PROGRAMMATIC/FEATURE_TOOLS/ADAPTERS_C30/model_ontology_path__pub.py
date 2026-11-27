"""Locate authoritative C9 Model sources within the native Component tree."""

from pathlib import PurePosixPath
import re


_COMPONENT = re.compile(r'(?!__)[^/]+_C[0-9]+')


def component_path(relative, component_id):
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or '\\' in str(path):
        return None
    for index, part in enumerate(path.parts):
        if _COMPONENT.fullmatch(part) is None:
            return None
        if part.endswith('_' + component_id):
            return PurePosixPath(*path.parts[:index + 1])
    return None


def ontology_component_path(relative):
    return component_path(relative, 'C9')


def is_ontology_model_source(relative):
    path = PurePosixPath(relative)
    component = ontology_component_path(path)
    if component is None or path.suffix != '.md':
        return False
    parts = path.relative_to(component).parts
    return (len(parts) == 1 or (len(parts) == 2 and parts[0] in {'_SPEC', '_DES'})
            or (len(parts) == 3 and parts[:2] == ('_DOM', 'CONT')))


def find_ontology_component(control):
    if not control.exists():
        return None
    pending = [control]
    ontology = None
    while pending:
        for path in pending.pop().iterdir():
            if _COMPONENT.fullmatch(path.name) is None:
                continue
            is_ontology = path.name.endswith('_C9')
            if path.is_symlink():
                if is_ontology:
                    raise ValueError(f'Unsafe Meta-ontology Component path: {path}')
                continue
            if not path.is_dir():
                continue
            if is_ontology:
                if ontology is not None:
                    raise ValueError('Duplicate Meta-ontology Component C9 directories')
                ontology = path
            pending.append(path)
    return ontology
