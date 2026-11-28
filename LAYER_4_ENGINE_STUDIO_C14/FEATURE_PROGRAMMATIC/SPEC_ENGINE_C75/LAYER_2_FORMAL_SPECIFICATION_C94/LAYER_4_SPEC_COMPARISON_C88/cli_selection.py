from .cli_facts import _package__shared as _implementation


def _cli_profiles(claims, interface, *, action=None):
    return _implementation._cli_profiles(claims, interface, action=action)


def _initial_trigger(claim):
    return _implementation._initial_trigger(claim)


def _manifest_endpoint(manifest, interface):
    return _implementation._manifest_endpoint(manifest, interface)
