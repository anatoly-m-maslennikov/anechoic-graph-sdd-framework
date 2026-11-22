
"""Immutable compiled placement bindings for lifecycle operations."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import PurePosixPath
from types import MappingProxyType
import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import canonical_role_name, named_value_token
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.placement_claim__pub import parse_placement_claim
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_layout__pub import role_folders_from_orders


def _name(value):
    token = named_value_token(canonical_role_name(value)) if isinstance(value, str) else None
    if not token:
        raise ValueError('Invalid placement Role or Status name')
    return token.casefold()


def _folder(value, *, empty=False):
    if not isinstance(value, str) or (not value and not empty):
        raise ValueError('Invalid placement folder')
    if not value:
        return value
    path = PurePosixPath(value)
    if (path.is_absolute() or '\\' in value or any(part in ('', '.', '..') for part in value.split('/'))
            or str(path) != value or '\x00' in value):
        raise ValueError('Unsafe placement folder')
    return value


@dataclass(frozen=True)
class PlacementRules:
    role_folders: object
    _placements: object
    _archive_aliases: object
    sources: tuple

    def role_folder(self, role):
        try:
            return self.role_folders[_name(role)]
        except KeyError as error:
            raise ValueError('No declared Role folder') from error

    def placement(self, role, status):
        key = (_name(role), _name(status))
        try:
            return self._placements[key]
        except KeyError:
            if key[1] in {'draft', 'archived', 'active'}:
                raise ValueError('Required explicit Status placement is missing') from None
            try:
                base, folder = self._placements[(key[0], '*')]
                return base, key[1] if folder == '<lowercase status>' else folder
            except KeyError as error:
                raise ValueError('No declared Role and Status placement') from error

    def archive_folders(self, role):
        base, folder = self.placement(role, 'Archived')
        if base != 'role' or not folder:
            raise ValueError('Archived placement must be Role-owned')
        return (folder, *self._archive_aliases.get(_name(role), ()))



def _load_pins(sources):
    ids = set()
    pins = []
    for pin in sources:
        if (not isinstance(pin, dict) or set(pin) != {'atom_id', 'version', 'sha256', 'source_path'}
                or not isinstance(pin['atom_id'], str) or not re.fullmatch(r'[A-Za-z0-9]+-[RD]-[0-9]+', pin['atom_id'])
                or type(pin['version']) is not int or pin['version'] < 1
                or not isinstance(pin['sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', pin['sha256'])):
            raise ValueError('Invalid placement source pin')
        _folder(pin['source_path'])
        if pin['atom_id'] in ids:
            raise ValueError('Duplicate placement source pin')
        ids.add(pin['atom_id'])
        pins.append(MappingProxyType(dict(pin)))
    return ids, pins


def _load_folders(entries, ids):
    folders = {}
    if not isinstance(entries, list) or not entries:
        raise ValueError('Placement requires Role folders')
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'role', 'folder', 'source'} or entry['source'] not in ids:
            raise ValueError('Invalid Role folder binding')
        role = _name(entry['role'])
        folder = _folder(entry['folder'])
        if '/' in folder or role in folders or folder in folders.values():
            raise ValueError('Duplicate or invalid Role folder binding')
        folders[role] = folder
    return folders


def _load_status_placements(records, ids, folders):
    placements = {}
    if not isinstance(records, list) or not records:
        raise ValueError('Placement requires Status bindings')
    for record in records:
        if (not isinstance(record, dict) or set(record) != {'role', 'status', 'base', 'folder', 'source'}
                or record['source'] not in ids or record['base'] not in {'role', 'container'}):
            raise ValueError('Invalid Status placement binding')
        role = _name(record['role'])
        status = '*' if record['status'] == '*' else _name(record['status'])
        key = (role, status)
        if role not in folders or key in placements:
            raise ValueError('Ambiguous Status placement binding')
        folder = record['folder']
        if folder == '<lowercase status>':
            if status != '*' or record['base'] != 'container':
                raise ValueError('Invalid Status-derived folder')
        else:
            _folder(folder, empty=True)
        placements[key] = (record['base'], folder)
    for role in folders:
        if any((role, status) not in placements for status in ('draft', 'archived', 'active')):
            raise ValueError('Incomplete Role placement bindings')
    return placements

def load_placement(payload):  # noqa: C901
    if not isinstance(payload, dict) or set(payload) != {'sources', 'role_folders', 'placements', 'archive_aliases'}:
        raise ValueError('Invalid placement asset')
    sources = payload['sources']
    if not isinstance(sources, list) or not sources:
        raise ValueError('Placement requires pinned sources')
    ids, pins = _load_pins(sources)
    folders = _load_folders(payload['role_folders'], ids)
    placements = _load_status_placements(payload['placements'], ids, folders)
    aliases = {}
    records = payload['archive_aliases']
    if not isinstance(records, list):
        raise ValueError('Invalid archive aliases')
    for record in records:
        if not isinstance(record, dict) or set(record) != {'role', 'folder', 'source'} or record['source'] not in ids:
            raise ValueError('Invalid archive alias')
        role = _name(record['role'])
        folder = _folder(record['folder'])
        if role not in folders or folder in aliases.get(role, []):
            raise ValueError('Duplicate or unknown archive alias')
        aliases.setdefault(role, []).append(folder)
    for role, values in aliases.items():
        target = placements.get((role, 'archived')) or placements.get((role, '*'))
        if target is None or target[0] != 'role' or target[1] in values:
            raise ValueError('Archive alias conflicts with declared placement')
    return PlacementRules(MappingProxyType(folders), MappingProxyType(placements),
                          MappingProxyType({role: tuple(values) for role, values in aliases.items()}), tuple(pins))


def _declared_orders(requirement_rows):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.formal_claim__pub import iter_formal_claims
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import parse_native_model_claim

    role_orders, status_folders, status_numbers = [], {}, set()
    for row in requirement_rows:
        source = row['id']
        for code in iter_formal_claims(row['_content_bytes'].decode('utf-8')):
            claim = parse_native_model_claim(code)
            if not claim or claim['kind'] != 'entity':
                continue
            args = claim['arguments']
            if args.get('qualification_property_path') == 'Atom.Header.Context.Role':
                order = args.get('classifications', {}).get('Role Order Number')
                if order is not None:
                    role_orders.append((args['entity_name'], order, source))
            for name, order in args.get('status_order_numbers', {}).items():
                status = _name(name)
                if status in status_folders or order in status_numbers:
                    raise ValueError(f'{source}: ambiguous Status order binding')
                status_folders[status] = (f'{order:03d}_{status}', source)
                status_numbers.add(order)
    return role_folders_from_orders(role_orders), status_folders



def _compile_placement_records(folders, rules, sources, requirement_rows, required_statuses, status_folders):
    records = []
    by_id = {row['id']: row for row in requirement_rows}
    for role, entry in folders.items():
        statuses = {status for selected_role, status in rules if selected_role in (None, role)}
        expected = {_name(status) for status in required_statuses.get(role, ())} if required_statuses is not None else set()
        if (None, '*') in rules and rules[(None, '*')][1] == '<status folder>':
            if not expected:
                raise ValueError(f"{entry['role']}: Current Status domain is missing")
            statuses.remove('*')
            statuses.update(expected - {'draft', 'archived'})
        if required_statuses is not None and '*' not in statuses:
            if not expected or not expected.issubset(statuses):
                raise ValueError(f"{entry['role']}: incomplete Status placement declarations")
        for status in sorted(statuses):
            binding = rules.get((role, status), rules.get((None, status)))
            if binding is None and status not in {'draft', 'archived'}:
                binding = rules.get((None, '*'))
            if binding is None:
                raise ValueError(f"{entry['role']}: Status placement is missing")
            base, folder, source = binding
            if folder == '<status folder>':
                if status not in status_folders:
                    raise ValueError(f"{entry['role']}: Status order is missing for {status}")
                folder, order_source = status_folders[status]
                sources[order_source] = by_id[order_source]
            records.append({'role': entry['role'], 'status': status, 'base': base, 'folder': folder, 'source': source})
    return records

def compile_placement(rows, requirement_rows=(), declared_roles=None, required_statuses=None):  # noqa: C901
    """Compile native Delivery and model placement Declarations."""
    folders, rules, sources = {}, {}, {}
    role_folders, status_folders = _declared_orders(requirement_rows)
    generic_source = None
    for row in rows:
        body = row['_content_bytes'].decode('utf-8')
        for rule in parse_placement_claim(body) or ():
            source = row['id']
            if rule['kind'] == 'role_root':
                if generic_source is not None:
                    raise ValueError('Duplicate generic Role placement template')
                generic_source = source
                sources[source] = row
                continue
            role = None if rule['role'] is None else _name(rule['role'])
            status = '*' if rule['status'] == '*' else _name(rule['status'])
            if (role, status) in rules:
                raise ValueError(f'{source}: duplicate placement binding')
            rules[(role, status)] = (rule['base'], rule['folder'], source)
            sources[source] = row
    if generic_source is not None:
        if not role_folders or (declared_roles is not None and
                {_name(role) for role in role_folders} != {_name(role) for role in declared_roles}):
            raise ValueError('Role order declarations are incomplete')
        by_id = {row['id']: row for row in requirement_rows}
        for role, (folder, source) in role_folders.items():
            folders[_name(role)] = {'role': role, 'folder': folder, 'source': source}
            sources[source] = by_id[source]
    elif role_folders:
        raise ValueError('Generic Role placement template is missing')
    if not sources:
        return None
    if not folders:
        raise ValueError('Placement Role folder declarations are missing')
    records = _compile_placement_records(folders, rules, sources, requirement_rows,
                                         required_statuses, status_folders)
    payload = {'sources': [{'atom_id': row['id'], 'version': row['version'], 'sha256': row['_sha256'],
                            'source_path': row['source_path']} for row in sources.values()],
               'role_folders': list(folders.values()), 'placements': records, 'archive_aliases': []}
    load_placement(payload)
    return payload


_CURRENT = ContextVar('lifecycle_placement', default=None)


@contextmanager
def bind_placement(rules):
    if not isinstance(rules, PlacementRules):
        raise ValueError('Compiled placement rules required')
    token = _CURRENT.set(rules)
    try:
        yield rules
    finally:
        _CURRENT.reset(token)


def active_placement():
    rules = _CURRENT.get()
    if rules is None:
        raise ValueError('Lifecycle placement rules are not bound')
    return rules
