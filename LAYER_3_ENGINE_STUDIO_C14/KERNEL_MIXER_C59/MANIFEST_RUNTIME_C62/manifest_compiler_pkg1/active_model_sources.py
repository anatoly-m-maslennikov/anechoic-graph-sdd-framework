"""Select active native Model Claims from the Meta-ontology and Project Config."""

import os
from pathlib import Path
import re

import subject_notation as notation
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.markdown_content import parse_content
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import (
    _check_relation_references, _native_claim, _native_claim_text,
)
from native_carrier_header import native_header_view
from native_carrier_placement import CUSTOM_MODEL_DIRECTORY, PROJECT_CONFIG_DIRECTORY
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
    return _valid_subject(scopes[0].strip(), source)


def _valid_subject(subject: str, source: str) -> str:
    try:
        expression = notation.parse_subject_expression(subject, subject_profile='approved').expression
    except notation.SubjectNotationError as error:
        raise ValueError(f'{source}: invalid Model Claim scope') from error
    if notation.render_subject(expression) != subject or not subject.startswith('MODEL//ANECHOIC <+ '):
        raise ValueError(f'{source}: invalid Model Claim scope')
    return subject


def _custom_claims(body: str, source: str):
    sections = parse_content(body)
    manifests = [s for s in sections if s['property_path'] == ['formal_manifest']]
    declarations = [s for s in sections if s['property_path'][:1] == ['formal_manifest']
                    and len(s['property_path']) == 2]
    if (len(manifests) != 1 or manifests[0]['heading_level'] != 2
            or manifests[0]['direct_markdown'] or not declarations
            or any(s['heading_level'] != 3 for s in declarations)
            or any(len(s['property_path']) > 2 for s in sections if s['property_path'][:1] == ['formal_manifest'])):
        raise ValueError(f'{source}: expected Formal Manifest with direct declaration subsections')
    result = []
    for declaration in declarations:
        text = declaration['direct_markdown'] or ''
        subject, separator, claim = text.strip().partition('\n')
        if not separator:
            raise ValueError(f'{source}: expected Model scope and Python fence')
        subject = _valid_subject(subject.strip(), source)
        result.append((subject, _native_claim_text(claim, source, subject)))
    return result


def read_active_model_sources(control_root: Path, component_root: Path) -> tuple[tuple[str, str, str], ...]:
    control = Path(os.path.abspath(control_root))
    component = Path(os.path.abspath(component_root))
    if component.parent != control or not component.name.endswith('_C9'):
        raise ValueError('Meta-ontology Component must be a direct C9 child of the control root')
    reader = ReadContext([str(control)], dict(CEILINGS))
    records, identifiers, subjects = [], set(), set()
    custom = control / PROJECT_CONFIG_DIRECTORY / CUSTOM_MODEL_DIRECTORY
    paths = [(path, False) for path in reader.inventory_shallow(component)] if component.exists() or component.is_symlink() else []
    if custom.exists() or custom.is_symlink():
        paths.extend((path, True) for path in reader.inventory_shallow(custom))
    for path, is_custom in paths:
        carrier = parse_carrier(reader.read(path), path)
        header = native_header_view(carrier.metadata)
        context, state = header.get('context'), header.get('state')
        if not isinstance(context, dict) or not isinstance(state, dict):
            continue
        if state.get('status') != 'active':
            continue
        if is_custom:
            if (header.get('atom_family') != 'PROJECT_CONFIG' or context.get('template') != 'model_manifest'
                    or context.get('container') != {'component': 'C00'}):
                continue
        elif context.get('lens') != 'SPEC' or context.get('container') != {'component': 'C9'}:
            continue
        source = str(path.relative_to(control))
        subject = None if is_custom else _claim_subject(carrier.body, source)
        if not is_custom and subject is None:
            continue
        identity = header.get('identity')
        identifier = identity.get('atom_id') if isinstance(identity, dict) else None
        version = state.get('version')
        if (not isinstance(identifier, str) or not re.fullmatch(r'[A-Z]+-C-[0-9]+' if is_custom else r'[A-Z]+-S-[0-9]+', identifier)
                or (is_custom and not path.name.startswith(identifier + '-'))
                or ('atom_family' not in carrier.metadata and not re.fullmatch(re.escape(identifier) + r'-SPEC(?:-[A-Z_]+)?--.+\.md', path.name))
                or type(version) is not int or version < 1):
            raise ValueError(f'{source}: invalid Model source identity, filename or version')
        if identifier in identifiers:
            raise ValueError(f'{source}: duplicate Model source ID')
        identifiers.add(identifier)
        source = f'{source}@{version}'
        claims = _custom_claims(carrier.body, source) if is_custom else [(subject, _native_claim(carrier.body, source, subject))]
        for subject, claim in claims:
            if subject in subjects:
                raise ValueError(f'{source}: duplicate Model Subject')
            subjects.add(subject)
            records.append((source, subject, claim))
    if component.exists() or component.is_symlink():
        if not records:
            raise ValueError('No active Model Claims were selected')
        _check_relation_references(records)
    if reader.currentness()['state'] != 'unchanged':
        raise ValueError('Model source inputs changed during selection')
    return tuple(records)
