"""Evaluate resolved Package code access without parsing source files."""


def allows_import(entry, caller, provider, *, inherited_imports=(), marker=None,
                  ordered_layers=None, provider_component=None, sibling=False, exact=False):
    """Apply caller imports, entry markers, and any sibling layer order."""
    if caller['id'] == provider['id']:
        return True
    if ordered_layers is not None and ordered_layers[1] >= ordered_layers[0]:
        return False

    def matches(selectors):
        return (entry in selectors or provider['id'] in selectors or
                provider_component in selectors or
                ('parent' in selectors and provider['id'] == caller['parent']) or
                ('siblings' in selectors and sibling))

    rules = [rule for rule in inherited_imports if rule is not None]
    granted = any(matches(selectors) for _, selectors in rules)
    visible = (exact or marker == 'public' or
               (marker == 'shared' and (sibling or granted)))
    return visible and all(matches(selectors) for closed, selectors in rules if closed)
