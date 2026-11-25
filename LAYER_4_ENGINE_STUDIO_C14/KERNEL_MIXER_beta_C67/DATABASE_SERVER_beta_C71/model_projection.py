"""Project admitted Model bindings and the latest Model attempt into DuckDB."""

import json
import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, FailFast, ValidationError, field_validator

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    canonical_model_address, model_class_target,
)


def ensure_model_tables(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS mrt_model_entities (
        subject VARCHAR, entity_path VARCHAR, entity_name VARCHAR,
        parent_path VARCHAR, parent_operator VARCHAR, attributes JSON)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS mrt_model_properties (
        subject VARCHAR, declaring_node VARCHAR, property_path VARCHAR,
        entity_name VARCHAR, refinements JSON, attributes JSON)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS mrt_diag_model_manifests (
        attempt_id VARCHAR, accepted_generation VARCHAR, severity VARCHAR,
        code VARCHAR, message VARCHAR, atom_ref VARCHAR, source_path VARCHAR,
        subject VARCHAR)''')


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _classify_declarations(descriptor):
    declarations = descriptor['bindings'].get('declarations', [])
    entities, properties, relations = [], [], []
    for subject, declaration in declarations:
        args = declaration['arguments']
        if declaration['kind'] == 'relation':
            relations.append((subject, args))
            continue
        if declaration['kind'] != 'entity':
            continue
        if 'entity_class' in args:
            target = model_class_target(subject, args['entity_name'])
            if target is None:
                raise ValueError(f'Invalid Model entity subject: {subject}')
            entities.append((subject, target, args))
        elif (args.get('entity_kind') == 'Property' or args.get('relation_name') == 'IS_PROPERTY_OF'
              or args.get('allowed_classification_values') and ' >| ' in subject):
            properties.append((subject, args))
    return entities, properties, relations


def _property_rows(properties, normalize):
    property_rows = []
    for subject, args in properties:
        declared = canonical_model_address(subject)
        if ' >| ' in declared and args.get('allowed_classification_values'):
            root, axis = declared.split(' >| ', 1)
            if axis not in args['allowed_classification_values']:
                raise ValueError(f'Invalid Model classification subject: {subject}')
            property_rows.append((subject, normalize(root), declared, axis, _json([]), _json(args)))
            continue
        declared_root, separator, rest = declared.partition('.')
        owner = normalize(declared_root)
        path = owner + (separator + rest if separator else '')
        refinements = [normalize(item) for item in args.get('applies_to_entity_classes', [])]
        property_rows.append((subject, owner, path, args['entity_name'], _json(refinements), _json(args)))
    return property_rows


def replace_model_projection(connection, descriptor):
    """Replace Model tables from the validated descriptor in the caller's transaction."""
    entities, properties, relations = _classify_declarations(descriptor)
    paths = {target for _, target, _ in entities}
    names = {}
    for path in paths:
        names.setdefault(re.split(r'/+', path)[-1], set()).add(path)

    def normalize(path):
        if path in paths:
            return path
        matches = {candidate for candidate in paths if candidate.endswith('/' + path)}
        if len(matches) == 1:
            return next(iter(matches))
        matches = names.get(re.split(r'/+', path)[-1], set())
        return next(iter(matches)) if len(matches) == 1 else path

    entity_rows = []
    for subject, target, args in entities:
        parts = re.split(r'(//|/)', target)
        parent = normalize(''.join(parts[:-2])) if len(parts) > 1 else None
        operator = parts[-2] if len(parts) > 1 else None
        entity_rows.append((subject, target, args['entity_name'], parent, operator, _json(args)))
    for subject, args in relations:
        declared = canonical_model_address(subject)
        parent, operator, name = declared.rpartition('//')
        if operator and name == args.get('relation_name'):
            parent = normalize(parent)
            if parent in paths:
                entity_rows.append((subject, parent + operator + name, name, parent, operator, _json(args)))
    property_rows = _property_rows(properties, normalize)
    connection.execute('DELETE FROM mrt_model_entities')
    connection.execute('DELETE FROM mrt_model_properties')
    if entity_rows:
        connection.executemany('INSERT INTO mrt_model_entities VALUES (?, ?, ?, ?, ?, ?)', entity_rows)
    if property_rows:
        connection.executemany('INSERT INTO mrt_model_properties VALUES (?, ?, ?, ?, ?, ?)', property_rows)


def replace_model_diagnostics(connection, rows):
    """Replace the latest attempt; callers manage its transaction and generation identity."""
    fields = ('attempt_id', 'accepted_generation', 'severity', 'code', 'message',
              'atom_ref', 'source_path', 'subject')
    values = [tuple(row.get(field) for field in fields) for row in rows]
    connection.execute('DELETE FROM mrt_diag_model_manifests')
    if values:
        connection.executemany('INSERT INTO mrt_diag_model_manifests VALUES (?, ?, ?, ?, ?, ?, ?, ?)', values)


class _ModelDiagnostic(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    attempt_id: str
    accepted_generation: str | None
    severity: str
    code: str
    message: str
    atom_ref: str | None
    source_path: str | None
    subject: str | None

    @field_validator("attempt_id", "severity", "code", "message")
    @classmethod
    def nonempty(cls, value: str) -> str:
        if not value:
            raise ValueError("Diagnostic text cannot be empty")
        return value


class _Diagnostics(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    rows: Annotated[list[_ModelDiagnostic], FailFast()]


def validate_model_diagnostics(rows, model_sha256):
    try:
        batch = _Diagnostics.model_validate({"rows": rows})
    except ValidationError:
        raise ValueError("Invalid Model diagnostics") from None
    return [row.model_dump() | {"accepted_generation": model_sha256} for row in batch.rows]
