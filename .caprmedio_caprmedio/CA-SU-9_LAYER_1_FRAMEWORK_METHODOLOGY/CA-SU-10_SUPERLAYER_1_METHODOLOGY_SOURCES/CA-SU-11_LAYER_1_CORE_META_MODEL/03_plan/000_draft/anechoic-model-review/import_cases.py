"""Explicit review fixtures, not a source-code import analyzer."""
import importlib
import sys
import tempfile
from pathlib import Path


def allowed(entry, caller, provider, exports, rules=(), marker=None, sidecar=None,
            filename_boundary=False):
    """exports=None means absent; an export maps an exact entry to (mode, consumers)."""
    caller_layer, provider_layer = caller.get('layer'), provider.get('layer')
    if (caller['id'] != provider['id'] and caller['parent'] == provider['parent']
            and caller_layer is not None and provider_layer is not None
            and provider_layer >= caller_layer):
        return False
    if exports is None:
        if marker is None and filename_boundary:
            return False
        mode, consumers = marker, None
    else:
        if entry not in exports:
            return False
        mode, consumers = exports[entry]
    # Sidecars trace implementation and never grant access.
    if consumers is not None:
        permitted = (caller['id'] in consumers or
                     ('parent' in consumers and caller['id'] == provider['parent']) or
                     ('siblings' in consumers and caller['parent'] == provider['parent']))
    elif mode == 'public':
        permitted = True
    else:
        permitted = (caller['id'] == provider['parent'] or
                     caller['parent'] == provider['parent'])
    return permitted and all(
        (allow is None or bool({entry, provider['id']} & allow)) and
        not ({entry, provider['id']} & deny)
        for allow, deny in rules
    )


def run():
    provider = {'id': 'billing', 'parent': 'root'}
    parent = {'id': 'root', 'parent': None}
    sibling = {'id': 'sales', 'parent': 'root'}
    outsider = {'id': 'C43', 'parent': 'elsewhere'}
    entry = 'billing.api.run'
    internal = {entry: (None, None)}
    public = {entry: ('public', None)}
    assert allowed(entry, parent, provider, internal)
    assert allowed(entry, sibling, provider, internal)
    assert not allowed(entry, outsider, provider, internal)
    assert not allowed(entry, sibling, provider, {entry: ('internal', {'parent'})})
    assert allowed(entry, sibling, provider, {entry: ('internal', {'siblings'})})
    assert not allowed(entry, parent, provider, {entry: ('internal', {'siblings'})})
    assert allowed(entry, outsider, provider, public)
    assert allowed(entry, outsider, provider, {entry: ('public', {'C43'})})
    assert not allowed(entry, sibling, provider, {entry: ('public', {'C43'})})
    assert not allowed(entry, outsider, provider, {})
    assert not allowed(entry, outsider, provider, None)
    assert allowed(entry, parent, provider, None)
    assert allowed(entry, sibling, provider, None)
    assert not allowed(entry, sibling, provider, None, filename_boundary=True)
    assert allowed(entry, outsider, provider, None, marker='public')
    assert not allowed(entry, outsider, provider, {}, marker='public')
    assert not allowed('billing.api', outsider, provider, public)
    assert allowed(entry, outsider, provider, public)
    assert not allowed(entry, outsider, provider, {}, sidecar={'implemented': entry})
    # Explicit inherited rules from two Component ancestors, then a nested package.
    inherited = [(None, {provider['id']}), (None, set()), (None, set())]
    assert not allowed(entry, outsider, provider, public, rules=inherited)
    assert not allowed(entry, outsider, provider, public, rules=[({'other'}, set())])
    assert allowed(entry, outsider, provider, public, rules=[({entry}, set())])
    upstream = provider | {'layer': 1}
    downstream = sibling | {'layer': 2}
    assert allowed(entry, downstream, upstream, public)
    assert not allowed(entry, downstream, upstream, {entry: ('internal', {'parent'})})
    downstream_entry = 'sales.api.run'
    assert not allowed(downstream_entry, upstream, downstream,
                       {downstream_entry: ('public', None)})
    assert not allowed(entry, sibling | {'layer': 1}, upstream, public)
    with tempfile.TemporaryDirectory() as tmp:
        package = Path(tmp) / 'billing'
        package.mkdir()
        (package / '__init__.py').write_text('')
        (package / 'orders__public.py').write_text('value = 7\n')
        sys.path.insert(0, tmp)
        try:
            module = importlib.import_module('billing.orders__public')
            assert module.value == 7
        finally:
            sys.path.remove(tmp)
            sys.modules.pop('billing.orders__public', None)
            sys.modules.pop('billing', None)
    print('import boundary review cases passed')


if __name__ == '__main__':
    run()
