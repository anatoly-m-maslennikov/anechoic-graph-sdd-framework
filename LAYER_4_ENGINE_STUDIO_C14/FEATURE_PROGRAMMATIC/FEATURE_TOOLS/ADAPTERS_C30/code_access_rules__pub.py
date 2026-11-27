"""Read declared code-access rules and module visibility marks."""

from collections.abc import Mapping


_VISIBILITY_ALIASES = {'shared': 'shared', 'private': 'private', 'public': 'public'}


def module_visibility(stem):
    """Return the visibility of a marked Module filename stem."""
    if stem.endswith(('__shared', '__family_pub', '__internal')):
        return 'shared'
    if stem.endswith('__public'):
        return 'public'
    return None


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
    return ('shared' if mode is None else _VISIBILITY_ALIASES[mode]), consumers


def parse_code_access(boundaries):
    """Normalize the authored Code Access rules for ``allows_import``."""
    if boundaries is None:
        return None, None
    if not isinstance(boundaries, Mapping) or set(boundaries) - {'code', 'process', 'state', 'io'}:
        raise ValueError('boundaries must map known boundary names')
    access = boundaries.get('code')
    if access is None:
        return None, None
    if not isinstance(access, Mapping) or set(access) - {'imports', 'exports'}:
        raise ValueError('code must contain only imports and exports')

    imports = access.get('imports')
    if imports is not None:
        if isinstance(imports, Mapping):
            if set(imports) != {'only'}:
                raise ValueError('imports mapping must contain only only')
            imports = (True, _selectors(imports['only']))
        else:
            imports = (False, _selectors(imports))
    exports = access.get('exports')
    if exports is not None:
        if not isinstance(exports, Mapping):
            raise ValueError('exports must be a mapping')
        exports = {entry: _export(entry, value) for entry, value in exports.items()}
    return imports, exports
