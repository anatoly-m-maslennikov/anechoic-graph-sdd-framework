"""Evaluate resolved Package code access without parsing source files."""

from collections.abc import Mapping

_VISIBILITY_ALIASES = {'family_pub': 'internal', 'pub': 'public',
                       'internal': 'internal', 'public': 'public'}


def module_visibility(stem):
    """Return the visibility of a marked Module filename stem."""
    if stem.endswith(('__family_pub', '__internal')):
        return 'internal'
    if stem.endswith(('__pub', '__public')):
        return 'public'
    return None


def allows_import(entry, caller, provider, exports, *, inherited_imports=(),
                  marked_only=False, marker=None, ordered_layers=None):
    """Return whether a resolved import passes all applicable access rules.

    ``inherited_imports`` contains caller-side allowlists, with None meaning
    unrestricted. ``marker`` is the visibility of the resolved root Module.
    ``marked_only`` is accepted for compatibility. A Module without an export
    declaration or a marker is Package-local in both cases.
    """
    if caller['id'] == provider['id']:
        return True
    if ordered_layers is not None and ordered_layers[1] >= ordered_layers[0]:
        return False

    if exports is None:
        if marker is None:
            return False
        mode, consumers = marker, None
    elif entry in exports:
        mode, consumers = exports[entry]
    else:
        return False

    if consumers is None:
        visible = (mode == 'public' or caller['id'] == provider['parent'] or
                   caller['parent'] == provider['parent'])
    else:
        visible = (caller['id'] in consumers or
                   ('parent' in consumers and caller['id'] == provider['parent']) or
                   ('siblings' in consumers and caller['parent'] == provider['parent']))

    return visible and all(
        rule is None or entry in rule or provider['id'] in rule or
        ('parent' in rule and provider['id'] == caller['parent']) or
        ('siblings' in rule and provider['parent'] == caller['parent'])
        for rule in (inherited_imports or ())
    )


def _selectors(value):
    if not isinstance(value, (list, tuple)) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError('selectors must be a list of nonempty strings')
    if len(value) != len(set(value)):
        raise ValueError('selectors must be unique')
    return set(value)


def _export(entry, declaration):
    if not isinstance(entry, str) or not entry.strip():
        raise ValueError('export entries must be nonempty strings')
    mode, consumers = declaration, None
    if isinstance(declaration, Mapping):
        if len(declaration) != 1:
            raise ValueError('an export must declare one visibility')
        mode, value = next(iter(declaration.items()))
        if mode not in _VISIBILITY_ALIASES:
            raise ValueError('unknown export visibility')
        consumers = _selectors(value)
    if mode is not None and (not isinstance(mode, str) or mode not in _VISIBILITY_ALIASES):
        raise ValueError('unknown export visibility')
    return _VISIBILITY_ALIASES.get(mode), consumers


def parse_code_access(boundaries):
    """Normalize the authored Code Access rules for ``allows_import``."""
    if boundaries is None:
        return None, None
    if not isinstance(boundaries, Mapping) or set(boundaries) - {'code_access', 'shared_state', 'runtime_io'}:
        raise ValueError('boundaries must map known boundary names')
    access = boundaries.get('code_access')
    if access is None:
        return None, None
    if not isinstance(access, Mapping) or set(access) - {'imports', 'exports'}:
        raise ValueError('code_access must contain only imports and exports')

    imports = access.get('imports')
    if imports is not None:
        imports = _selectors(imports)
    exports = access.get('exports')
    if exports is not None:
        if not isinstance(exports, Mapping):
            raise ValueError('exports must be a mapping')
        exports = {entry: _export(entry, value) for entry, value in exports.items()}
    return imports, exports
