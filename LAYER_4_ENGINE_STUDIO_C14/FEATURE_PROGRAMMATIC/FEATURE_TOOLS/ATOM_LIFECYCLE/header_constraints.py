
"""Compile a bounded subset of explicit Header property declarations.

Compile explicit property, direct-value and child cardinality and literal value domains.
"""
from dataclasses import dataclass
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.formal_claim__pub import iter_formal_claims
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.cardinality__pub import cardinality_bounds
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import GROUP_FIELDS, ROLE_FIELDS, header_value, path_value

_PATH = r'[A-Za-z][A-Za-z0-9_ ]*(?:\.[A-Za-z][A-Za-z0-9_ ]*)*'
_SELECTED = r'(?:"[^"\r\n]+"|[A-Za-z][A-Za-z0-9 &_-]*)'
_SELECTOR = (rf'(?:/\(\s*\.Header\.(?:Context\.)?(Role|Form)\s*'
             rf'((?::=|:)\s*{_SELECTED}|in\s*\(\s*{_SELECTED}\s*\))\s*\))?')


def _path(value):
    parts = [re.sub(r'\s+', '_', p.strip()).lower() for p in value.split('.')]
    if len(parts) > 1 and parts[0] in GROUP_FIELDS:
        group, leaf = parts[:2]
        if group == 'identity' and leaf == 'id':
            parts[:2] = ['atom_id']
        elif leaf in GROUP_FIELDS[group]:
            parts.pop(0)
        elif group == 'context' and len(parts) > 2 and parts[2] in ROLE_FIELDS.get(leaf, ()):
            parts = parts[2:]
    parts[0] = {'id': 'atom_id', 'carrier_destination': 'destination'}.get(parts[0], parts[0])
    return '.'.join(parts)


def _value(view, path):
    return header_value(view, _path(path))


def _group(metadata, name, fields):
    _, stored = path_value(metadata, tuple(name.split('.')))
    values = {_path(key): value for key, value in stored.items()} if isinstance(stored, dict) else {}
    for field in fields:
        address = f'{name}.{field}' if '.' in name else field
        present, value = header_value(metadata, address)
        if present:
            values[field] = value
    return values


def _logical_groups(metadata, role):
    projection = dict(metadata)
    for group, fields in GROUP_FIELDS.items():
        values = _group(metadata, group, fields)
        if values:
            projection[group] = values
    for group, fields in ROLE_FIELDS.items():
        if matches_named_value(role, group.capitalize()):
            values = _group(metadata, f'context.{group}', fields)
            if values:
                projection.setdefault('context', {})[group] = values
    return projection


def _selected(value):
    if value is None:
        return ''
    text = value.partition('(')[2][:-1] if value.startswith('in') else value.lstrip(':=')
    return text.strip().strip('"')


def _native_header_target(args, source):
    if args.get('relation_name') != 'IS_PROPERTY_OF':
        return None
    base, name = args.get('base_path'), args.get('entity_name')
    if not isinstance(base, str) or not isinstance(name, str):
        return None
    match = re.fullmatch(rf'Atom{_SELECTOR}\.Header(?:\.({_PATH}))?', base)
    if match is None:
        return None
    selector, selected, rest = match.groups()
    selector, selected = (selector.lower(), _selected(selected)) if selector else ('', '')
    roles = args.get('applies_to_entity_classes', ())
    if roles:
        if len(roles) != 1 or selector and (selector != 'role' or selected != roles[0]):
            raise ValueError(f'{source}: unsupported Header Entity selector')
        selector, selected = 'role', roles[0]
    return _path('.'.join(part for part in (rest, name) if part)), selector, selected


def _native_header_records(code, source):
    declaration = parse_native_model_claim(code)
    if declaration is None or declaration['kind'] != 'entity':
        return set()
    args = declaration['arguments']
    target = _native_header_target(args, source)
    if target is None:
        return set()
    path, selector, selected = target
    records = set()
    if (occurrence := args.get('property_occurrence_cardinality')) in (0, 1):
        records.add(('property', path, selector, selected, str(occurrence), source))
    if (cardinality := args.get('value_cardinality')) is not None:
        records.add(('value', path, selector, selected, cardinality_bounds(cardinality), source))
    if (children := args.get('allowed_dependent_property_names')):
        low, high = cardinality_bounds(args['dependent_property_cardinality'])
        if high is not None:
            names = tuple(sorted(_path(child) for child in children))
            records.add(('children', path, selector, selected, (low, high, *names), source))
    if (cardinality := args.get('dependent_property_value_cardinality')) is not None:
        records.add(('value', path + '.*', selector, selected, cardinality_bounds(cardinality), source))
    if path not in {'role', 'form', 'status'}:
        for value in args.get('allowed_values', ()):
            records.add(('domain', path, selector, selected, value, source))
    return records


def compile_header_constraints(rows):
    records = set()
    for row in rows:
        for block in iter_formal_claims(row['_content_bytes'].decode('utf-8')):
            records.update(_native_header_records(block, row['id']))
    keys = ('kind', 'path', 'selector', 'selected', 'value', 'source')
    return [dict(zip(keys, item)) for item in sorted(records, key=repr)]


@dataclass(frozen=True)
class HeaderConstraints:
    properties: tuple
    domains: tuple
    children: tuple = ()
    values: tuple = ()

    def validate(self, view, *, metadata=None):
        metadata = _logical_groups(view if metadata is None else metadata, view.get('role'))
        errors = []
        for path, selector, selected, count, source in self.properties:
            if selector and not matches_named_value(view.get(selector), selected):
                continue
            logical = _path(path)
            parent_path = logical.rpartition('.')[0]
            if parent_path and not isinstance(_value(metadata, parent_path)[1], dict):
                continue
            present, _ = _value(metadata, logical)
            if (count == '1' and not present) or (count == '0' and present):
                field = self._missing_field(view, logical) if not present else path
                errors.append((field, f'Header {path} requires property cardinality {count} ({source}).', None))
        for path, selector, selected, values, source in self.domains:
            if selector and not matches_named_value(view.get(selector), selected):
                continue
            present, current = _value(metadata, path)
            named = _path(path) in {'role', 'form', 'status'}
            actual = current if isinstance(current, list) else [current]
            if present and any(not isinstance(item, str) or not any(
                matches_named_value(item, value) if named else item == value for value in values
            ) for item in actual):
                errors.append((path, f'Header {path} must use a declared value ({source}).', values))
        errors.extend(self._validate_children(view, metadata))
        errors.extend(self._validate_values(view, metadata))
        return errors

    def _validate_values(self, view, metadata):
        for path, selector, selected, (low, high), source in self.values:
            if selector and not matches_named_value(view.get(selector), selected):
                continue
            wildcard = path.endswith('.*')
            present, value = _value(metadata, path[:-2] if wildcard else path)
            if not present:
                continue
            entries = value.items() if wildcard and isinstance(value, dict) else () if wildcard else ((None, value),)
            for child, item in entries:
                count = 0 if isinstance(item, dict) else len(item) if isinstance(item, list) else 1
                if count < low or (high is not None and count > high):
                    field = f'{path[:-2]}.{child}' if wildcard else path
                    expected = f'{low}+' if high is None else str(low) if low == high else f'{low}..{high}'
                    yield field, f'Header {field} requires value cardinality {expected} ({source}).', None

    def _missing_field(self, view, path):
        for group, selector, selected, bounds, _ in self.children:
            if (_path(group) == path and bounds[:2] == (1, 1) and len(bounds) == 3
                    and (not selector or matches_named_value(view.get(selector), selected))):
                return _path(f'{path}.{bounds[2]}')
        return path

    def _validate_children(self, view, metadata):
        for path, selector, selected, value, source in self.children:
            if selector and not matches_named_value(view.get(selector), selected):
                continue
            present, group = _value(metadata, path)
            if not present:
                continue
            low, high, *names = value
            keys = set(group) if isinstance(group, dict) else set()
            if not low <= len(keys) <= high or keys - set(names):
                yield path, f'Header {path} requires {low}..{high} children from {", ".join(names)} ({source}).', None


def load_header_constraints(records, source_ids):  # noqa: C901
    if not isinstance(records, list):
        raise ValueError('invalid Header constraint records')
    seen, properties, domains, children, values = set(), [], {}, [], []
    for row in records:
        if not isinstance(row, dict) or set(row) != {'kind', 'path', 'selector', 'selected', 'value', 'source'}:
            raise ValueError('invalid Header constraint record')
        kind, path, selector, selected, value, source = (row[k] for k in ('kind', 'path', 'selector', 'selected', 'value', 'source'))
        if (any(not isinstance(v, str) for v in (kind, path, selector, selected, source))
                or kind not in {'property', 'domain', 'children', 'value'}
                or not re.fullmatch(r'[a-z0-9_]+(?:\.[a-z0-9_]+)*(?:\.\*)?' if kind == 'value'
                                    else r'[a-z0-9_]+(?:\.[a-z0-9_]+)*', path)
                or selector not in {'', 'role', 'form'} or bool(selector) != bool(selected)
                or source not in source_ids):
            raise ValueError('invalid Header constraint record')
        if kind == 'value':
            if (not isinstance(value, (list, tuple)) or len(value) != 2 or type(value[0]) is not int
                    or value[0] < 0 or (value[1] is not None and
                        (type(value[1]) is not int or value[1] < value[0]))):
                raise ValueError('invalid Header value constraint')
            value = tuple(value)
        elif kind == 'children':
            if (not isinstance(value, (list, tuple)) or len(value) < 3
                    or any(type(bound) is not int for bound in value[:2]) or not 0 <= value[0] <= value[1]
                    or any(not isinstance(name, str) or not re.fullmatch(r'[a-z0-9_]+', name) for name in value[2:])):
                raise ValueError('invalid Header child constraint')
            value = tuple(value)
        elif not isinstance(value, str) or not value or (kind == 'property' and value not in {'0', '1'}):
            raise ValueError('invalid Header constraint value')
        key = (kind, path, selector, selected, value, source)
        if key in seen:
            raise ValueError('duplicate Header constraint record')
        seen.add(key)
        if kind == 'property':
            properties.append((path, selector, selected, value, source))
        elif kind == 'children':
            children.append((path, selector, selected, value, source))
        elif kind == 'value':
            values.append((path, selector, selected, value, source))
        else:
            domains.setdefault((path, selector, selected, source), set()).add(value)
    return HeaderConstraints(tuple(properties), tuple((*key[:3], frozenset(items), key[3]) for key, items in sorted(domains.items())), tuple(children), tuple(values))
