"""Select the active Model Claims directly owned by the Meta-ontology Component."""

import os
from pathlib import Path
import re

import subject_notation as notation
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.markdown_content import parse_content
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import (
    _check_relation_references, _native_claim,
)
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier
from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
from VALIDATE_ATOMS.validate_atoms_workers.settings import CEILINGS


def _claim_subject(body: str, source: str) -> str | None:
    sections = parse_content(body, tolerate_duplicate_siblings=True)
    scopes = [s['direct_markdown'] for s in sections if s['property_path'] == ['claim_scope']]
    if not any(isinstance(scope, str) and 'MODEL//ANECHOIC' in scope for scope in scopes):
        return None
    if len(scopes) != 1 or not isinstance(scopes[0], str):
        raise ValueError(f'{source}: expected one Model Claim scope')
    subject = scopes[0].strip()
    try:
        expression = notation.parse_subject_expression(subject, subject_profile='approved').expression
    except notation.SubjectNotationError as error:
        raise ValueError(f'{source}: invalid Model Claim scope') from error
    if notation.render_subject(expression) != subject or not subject.startswith('MODEL//ANECHOIC <+ '):
        raise ValueError(f'{source}: invalid Model Claim scope')
    return subject


def read_active_model_sources(control_root: Path, component_root: Path) -> tuple[tuple[str, str, str], ...]:
    control = Path(os.path.abspath(control_root))
    component = Path(os.path.abspath(component_root))
    if component.parent != control or not component.name.endswith('_C9'):
        raise ValueError('Meta-ontology Component must be a direct C9 child of the control root')
    reader = ReadContext([str(control)], dict(CEILINGS))
    records, identifiers, subjects = [], set(), set()
    for path in reader.inventory_shallow(component):
        carrier = parse_carrier(reader.read(path), path)
        header = carrier.metadata
        context, state = header.get('context'), header.get('state')
        if not isinstance(context, dict) or not isinstance(state, dict):
            continue
        if state.get('status') != 'active' or context.get('lens') != 'SPEC' or context.get('container') != {'component': 'C9'}:
            continue
        source = str(path.relative_to(control))
        subject = _claim_subject(carrier.body, source)
        if subject is None:
            continue
        identity = header.get('identity')
        identifier = identity.get('atom_id') if isinstance(identity, dict) else None
        version = state.get('version')
        if (not isinstance(identifier, str) or not re.fullmatch(r'[A-Z]+-S-[0-9]+', identifier)
                or not re.fullmatch(re.escape(identifier) + r'-SPEC(?:-[A-Z_]+)?--.+\.md', path.name)
                or type(version) is not int or version < 1):
            raise ValueError(f'{source}: invalid Model source identity, filename or version')
        if identifier in identifiers or subject in subjects:
            raise ValueError(f'{source}: duplicate Model source ID or Subject')
        identifiers.add(identifier)
        subjects.add(subject)
        source = f'{source}@{version}'
        records.append((source, subject, _native_claim(carrier.body, source, subject)))
    if not records:
        raise ValueError('No active Model Claims were selected')
    _check_relation_references(records)
    if reader.currentness()['state'] != 'unchanged':
        raise ValueError('Model source inputs changed during selection')
    return tuple(records)
