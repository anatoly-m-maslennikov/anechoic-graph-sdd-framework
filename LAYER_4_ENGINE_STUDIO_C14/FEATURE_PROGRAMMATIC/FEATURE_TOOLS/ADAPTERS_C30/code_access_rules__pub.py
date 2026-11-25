"""Read declared code-access rules and module visibility marks."""

from collections.abc import Mapping


def module_visibility(stem):
    """Return the visibility of a marked Module filename stem."""
    if stem.endswith(('__shared', '__family_pub', '__internal')):
        return 'shared'
    if stem.endswith(('__pub', '__public')):
        return 'public'
    return None


def _selectors(value):
    if not isinstance(value, (list, tuple)) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError('selectors must be a list of nonempty strings')
    if len(value) != len(set(value)):
        raise ValueError('selectors must be unique')
    return set(value)


def parse_code_access(boundaries):
    """Normalize the authored Code Access rules for ``allows_import``."""
    if boundaries is None:
        return None
    if not isinstance(boundaries, Mapping) or set(boundaries) - {'code', 'process', 'state', 'io'}:
        raise ValueError('boundaries must map known boundary names')
    if 'process' in boundaries and not isinstance(boundaries['process'], Mapping):
        raise ValueError('process must be a mapping')
    access = boundaries.get('code')
    if access is None:
        return None
    if not isinstance(access, Mapping) or set(access) - {'imports'}:
        raise ValueError('code must contain only imports')

    imports = access.get('imports')
    if imports is not None:
        if isinstance(imports, Mapping):
            if set(imports) != {'only'}:
                raise ValueError('imports mapping must contain only only')
            imports = (True, _selectors(imports['only']))
        else:
            imports = (False, _selectors(imports))
    return imports
