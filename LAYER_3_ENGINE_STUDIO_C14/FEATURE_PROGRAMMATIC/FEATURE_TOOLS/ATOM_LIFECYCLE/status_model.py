
"""Build and load a bounded, source-bound Atom Status declaration asset."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Iterable


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import (
    StatusModelError, canonical_role_name, carrier_read_view, carrier_status_folder, matches_named_value,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import parse_carrier


def status_memberships(body):
    """Read Status values from native Property Declarations without translating them."""
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.formal_claim__pub import iter_formal_claims
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import parse_native_model_claim

    result = []
    for code in iter_formal_claims(body):
        declaration = parse_native_model_claim(code)
        if declaration is None or declaration['kind'] != 'entity':
            continue
        args = declaration['arguments']
        if (args.get('relation_name'), args.get('base_path'), args.get('entity_name')) != (
            'IS_PROPERTY_OF', 'Atom.Header.State', 'Status',
        ):
            continue
        roles = args.get('applies_to_entity_classes', ())
        if len(roles) > 1:
            raise StatusModelError('A Role-qualified Status Declaration requires one Role')
        role = args.get('applies_to_role', roles[0] if roles else None)
        forms = args.get('applies_to_forms', (None,))
        result.extend((role, form, value) for form in forms for value in args.get('allowed_values', ()))
    return result


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _validate(data: object) -> tuple[tuple[str | None, str | None, str], ...]:
    if not isinstance(data, dict) or set(data) != {'schema', 'sources', 'declarations'} or data['schema'] != 1 or type(data['schema']) is not int:
        raise StatusModelError('Invalid Status model schema')
    sources = data['sources']
    if not isinstance(sources, list) or not sources:
        raise StatusModelError('Status model requires sources')
    ids: set[str] = set()
    for source in sources:
        if (not isinstance(source, dict) or set(source) != {'atom_id', 'version'}
                or not _text(source['atom_id']) or type(source['version']) is not int or source['version'] < 1
                or source['atom_id'] in ids):
            raise StatusModelError('Invalid or duplicate Status source')
        ids.add(source['atom_id'])
    declarations = data['declarations']
    if not isinstance(declarations, list) or not declarations:
        raise StatusModelError('Status model requires declarations')
    rows = []
    seen = set()
    for row in declarations:
        if (not isinstance(row, dict) or set(row) != {'source', 'role', 'form', 'value'}
                or not _text(row['source']) or row['source'] not in ids or not _text(row['value'])
                or any(v is not None and not _text(v) for v in (row['role'], row['form']))):
            raise StatusModelError('Invalid Status declaration')
        key = (row['source'], row['role'], row['form'], row['value'])
        if key in seen:
            raise StatusModelError('Duplicate Status declaration')
        seen.add(key)
        rows.append((row['role'], row['form'], row['value']))
    if not any(role is None and form is None for role, form, _ in rows):
        raise StatusModelError('Status model requires base declarations')
    return tuple(rows)


@dataclass(frozen=True)
class StatusModel:
    _rows: tuple[tuple[str | None, str | None, str], ...]
    candidate_schema: object | None = None

    def allowed(self, role: str, form: str) -> frozenset[str]:
        if not _text(role) or not _text(form):
            raise StatusModelError('Role and Form must be nonempty exact strings')
        role = canonical_role_name(role)
        return frozenset(value for r, f, value in self._rows
                         if (r is None or canonical_role_name(r) == role) and (f is None or f == form))


def compile_status_model(paths: Iterable[Path]) -> bytes:
    """Compile only the supplied native current Declaration carriers."""
    sources = []
    declarations = []
    for supplied in paths:
        path = Path(supplied)
        try:
            carrier = parse_carrier(path.read_bytes(), path)
        except (OSError, ValueError) as error:
            raise StatusModelError(f'{path}: invalid source: {error}') from error
        meta = carrier_read_view(carrier.metadata)
        atom_id, version = meta.get('atom_id'), meta.get('version')
        if (not _text(atom_id) or type(version) is not int or version < 1
                or not matches_named_value(meta.get('role'), 'Requirement')
                or not matches_named_value(meta.get('form'), 'Declaration')
                or meta.get('status') not in {'Active', 'active'}):
            raise StatusModelError(f'{path}: expected an Active Requirement Declaration with ID and version')
        sources.append({'atom_id': atom_id, 'version': version})
        declarations.extend({'source': atom_id, 'role': role, 'form': form, 'value': value}
                            for role, form, value in status_memberships(carrier.body))
    sources.sort(key=lambda x: x['atom_id'])
    declarations.sort(key=lambda x: (x['source'], x['role'] or '', x['form'] or '', x['value']))
    data = {'schema': 1, 'sources': sources, 'declarations': declarations}
    _validate(data)
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def load_status_model(path: Path) -> StatusModel:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise StatusModelError('Duplicate JSON key in Status model')
            result[key] = value
        return result
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique)
        return StatusModel(_validate(data))
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError) as error:
        raise StatusModelError(f'Invalid Status model asset: {error}') from error


def _staged_declarations(root: Path) -> list[Path]:
    """Find current Status declarations solely in the supplied staged sources."""
    if not root.is_dir():
        raise StatusModelError(f'{root}: staged model root is not a directory')
    found = []
    for path in sorted(root.rglob('CA-R-*.md')):
        if any(carrier_status_folder(part) in {'archived', 'draft'} for part in path.relative_to(root).parts):
            continue
        try:
            carrier = parse_carrier(path.read_bytes(), path)
        except (OSError, ValueError) as error:
            raise StatusModelError(f'{path}: invalid staged source: {error}') from error
        meta = carrier_read_view(carrier.metadata)
        if (meta.get('status') not in {'Active', 'active'}
                or not matches_named_value(meta.get('role'), 'Requirement')
                or not matches_named_value(meta.get('form'), 'Declaration')):
            continue
        if status_memberships(carrier.body):
            found.append(path)
    if not found:
        raise StatusModelError(f'{root}: no current Status declarations in staged sources')
    return found


def _main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description='Compile Status declarations from staged model sources')
    parser.add_argument('--model-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        payload = compile_status_model(_staged_declarations(args.model_root))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Status model build failed: {error}\n')


if __name__ == '__main__':
    _main()
