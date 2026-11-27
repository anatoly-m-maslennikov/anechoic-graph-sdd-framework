"""Select the CLI entry and workflow from a normalized specification."""

from .trace_spec__pub import _operation_claims


def _initial_trigger(claim):
    initial = next(state for state in claim['states'] if state['name'] == claim['initial'])
    triggers = [transition for transition in initial['transitions'] if transition['expect']['kind'] == 'trigger']
    return triggers[0] if len(triggers) == 1 else None


def _manifest_endpoint(manifest, interface):
    boundaries = manifest.get('boundaries') or {}
    io = boundaries.get('io')
    server = io.get('server') if isinstance(io, dict) else None
    return server.get(interface) if isinstance(server, dict) else None


def _cli_profiles(claims, interface, *, action=None):
    contract, workflow = (claims.get(role, {}) for role in ('contract', 'solution'))
    if action is not None:
        contract, workflow = (_operation_claims(claim).get(action, {}) for claim in (contract, workflow))
        if contract.get('transport') != 'cli' or contract.get('interface') != interface:
            raise ValueError(f'No CLI Contract for Action {action!r} on interface {interface!r}')
        return contract, workflow
    if 'operations' in contract:
        matches = [profile for profile in contract['operations'].values()
                   if profile.get('transport') == 'cli' and profile.get('interface') == interface]
        contract = matches[0] if len(matches) == 1 else {}
    elif contract.get('transport') != 'cli' or contract.get('interface') != interface:
        contract = {}
    if 'operations' in workflow:
        operations = workflow['operations']
        matches = [profile for profile in operations.values()
                   if (trigger := _initial_trigger(profile)) is not None
                   and trigger['expect'].get('target') == interface
                   and trigger['expect'].get('detail', {}).get('transport') == 'cli']
        workflow = operations.get(contract.get('action'), matches[0] if len(matches) == 1 else {})
    return contract, workflow
