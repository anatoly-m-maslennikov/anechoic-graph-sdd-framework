"""Project admitted Model bindings and the latest Model attempt into DuckDB."""

import json
import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, FailFast, ValidationError, field_validator

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    NODE_LINK_PREFIX, canonical_model_address, model_class_target,
)

from .model_entity_properties import primary_entity_properties
from .model_entity_tree import model_tree_rows


def ensure_model_tables(connection):
    connection.execute('''CREATE TABLE IF NOT EXISTS mrt_model_entities (
        subject VARCHAR, entity_path VARCHAR, entity_name VARCHAR,
        parent_path VARCHAR, parent_operator VARCHAR, attributes JSON)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS mrt_model_properties (
        subject VARCHAR, declaring_node VARCHAR, property_path VARCHAR,
        entity_name VARCHAR, refinements JSON, attributes JSON)''')
    connection.execute('''CREATE TABLE IF NOT EXISTS mrt_model_tree (
        entity_path VARCHAR PRIMARY KEY, concern_path VARCHAR, entity_name VARCHAR,
        parent_path VARCHAR, parent_operator VARCHAR, reference_path VARCHAR)''')
    tree_columns = {row[1] for row in connection.execute("PRAGMA table_info('mrt_model_tree')").fetchall()}
    if "reference_path" not in tree_columns:
        connection.execute("ALTER TABLE mrt_model_tree ADD COLUMN reference_path VARCHAR")
    connection.execute('''CREATE TABLE IF NOT EXISTS mrt_model_primary_entities (
        entity_path VARCHAR PRIMARY KEY, concern_path VARCHAR, entity_name VARCHAR, properties JSON,
        axes JSON, node_rules JSON)''')
    columns = {row[1] for row in connection.execute("PRAGMA table_info('mrt_model_primary_entities')").fetchall()}
    if "classifications" in columns and "axes" not in columns:
        connection.execute("ALTER TABLE mrt_model_primary_entities RENAME COLUMN classifications TO axes")
        columns.add("axes")
    for column in ("axes", "node_rules"):
        if column not in columns:
            connection.execute(f"ALTER TABLE mrt_model_primary_entities ADD COLUMN {column} JSON")
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
              or args.get('allowed_axis_values', args.get('allowed_classification_values')) and ' >| ' in subject):
            properties.append((subject, args))
    return entities, properties, relations


def _property_rows(properties, normalize):
    property_rows = []
    for subject, args in properties:
        declared = canonical_model_address(subject)
        if ' >| ' in declared and args.get('allowed_axis_values', args.get('allowed_classification_values')):
            root, axis = declared.split(' >| ', 1)
            if axis not in args.get('allowed_axis_values', args.get('allowed_classification_values')):
                raise ValueError(f'Invalid Model axis subject: {subject}')
            property_rows.append((subject, normalize(root), declared, axis, _json([]), _json(args)))
            continue
        declared_root, separator, rest = declared.partition('.')
        owner = normalize(declared_root)
        path = owner + (separator + rest if separator else '')
        refinements = [normalize(item) for item in args.get('applies_to_entity_classes', [])]
        property_rows.append((subject, owner, path, args['entity_name'], _json(refinements), _json(args)))
    return property_rows


def _replace_primary_projections(connection, descriptor, entities, properties, normalize):
    bases = {cls['name']: cls['bases']
             for _, declaration in descriptor['bindings'].get('declarations', ())
             for cls in declaration.get('classes', ())}
    effective = primary_entity_properties(entities, properties, bases, normalize)
    tree = model_tree_rows(entities, descriptor.get('node_locations', {}), normalize)
    arguments = {path: args for _, path, args in entities}
    subjects = {subject: path for subject, path, _ in entities}
    subject_by_path = {path: subject for subject, path, _ in entities}
    display_paths = {path: concern for path, concern, _, _, _ in tree}
    metadata = {key: descriptor.get(key, {}) for key in ('node_parts', 'node_alternatives', 'node_aliases')}
    links = [(path + '//' + label, display_paths[path] + '//' + label, label, path, '//', target)
             for subject, items in metadata['node_parts'].items() if subject in subjects
             for path in (subjects[subject],)
             for label, target in items if label.startswith(NODE_LINK_PREFIX)]
    axis_values = {}
    for subject, args in properties:
        allowed = args.get('allowed_axis_values', args.get('allowed_classification_values'))
        declared = canonical_model_address(subject)
        if allowed and ' >| ' in declared:
            root, axis = declared.split(' >| ', 1)
            axis_values.setdefault(normalize(root), {})[axis] = allowed[axis]
    entity_fields = {'entity_name', 'entity_class', 'entity_kind', 'axes', 'classifications'}
    connection.execute('DELETE FROM mrt_model_tree')
    connection.execute('DELETE FROM mrt_model_primary_entities')
    if tree:
        connection.executemany('INSERT INTO mrt_model_tree VALUES (?, ?, ?, ?, ?, ?)',
                               [(*row, None) for row in tree] + links)
        connection.executemany('INSERT INTO mrt_model_primary_entities (entity_path, concern_path, entity_name, properties, axes, node_rules) VALUES (?, ?, ?, ?, ?, ?)',
            [(path, concern, name, _json(effective[path]),
              _json(arguments[path].get('axes', arguments[path].get('classifications', {}))),
              _json({key: value for key, value in arguments[path].items() if key not in entity_fields}
                    | {key: definitions[subject] for key, definitions in metadata.items() if subject in definitions}
                    | ({'allowed_axis_values': axis_values[path]} if path in axis_values else {})))
             for path, concern, name, _, _ in tree
             for subject in [subject_by_path[path]]])


def _entity_rows(entities, relations, paths, normalize):
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
    return entity_rows


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

    entity_rows = _entity_rows(entities, relations, paths, normalize)
    property_rows = _property_rows(properties, normalize)
    connection.execute('DELETE FROM mrt_model_entities')
    connection.execute('DELETE FROM mrt_model_properties')
    if entity_rows:
        connection.executemany('INSERT INTO mrt_model_entities VALUES (?, ?, ?, ?, ?, ?)', entity_rows)
    if property_rows:
        connection.executemany('INSERT INTO mrt_model_properties VALUES (?, ?, ?, ?, ?, ?)', property_rows)
    _replace_primary_projections(connection, descriptor, entities, properties, normalize)


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
