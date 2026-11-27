"""Evaluate resolved Package code access without parsing source files."""


def allows_import(entry, caller, provider, exports, *, inherited_imports=(),
                  marked_only=False, marker=None, ordered_layers=None):
    """Return whether a resolved import passes all applicable access rules.

    ``inherited_imports`` contains additive or closed selector rules.
    ``marker`` is the visibility of the resolved root Module.
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

    shared = caller['id'] == provider['parent'] or caller['parent'] == provider['parent']
    named = consumers is not None and (
        caller['id'] in consumers or
        ('parent' in consumers and caller['id'] == provider['parent']) or
        ('siblings' in consumers and caller['parent'] == provider['parent']))
    visible = mode == 'public' or (mode == 'shared' and shared) or named
    default_import = (provider['parent'] == caller['id'] or
                      provider['parent'] == caller['parent'] or mode == 'public')

    def matches(selectors):
        return (entry in selectors or provider['id'] in selectors or
                ('parent' in selectors and provider['id'] == caller['parent']) or
                ('siblings' in selectors and provider['parent'] == caller['parent']))

    rules = [rule for rule in inherited_imports if rule is not None]
    return (visible and
            (default_import or any(matches(selectors) for _, selectors in rules)) and
            all(matches(selectors) for closed, selectors in rules if closed))
