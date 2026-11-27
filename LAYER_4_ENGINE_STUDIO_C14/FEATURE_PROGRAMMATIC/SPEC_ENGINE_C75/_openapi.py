"""Export the pinned HTTP Action schemas in a parsed Component Manifest."""

import json
from copy import deepcopy

from .LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import (
    http_routes,
    normalize_claim,
)


def _http_claim(manifest, action):
    carrier = manifest.get('contract')
    if not carrier:
        raise ValueError('Expected a declared HTTP Contract')
    model, error = normalize_claim(
        'contract', carrier, manifest['fields']['component_id']
    )
    if error:
        raise ValueError(error)
    operations = model.get('operations', {'': model})
    candidates = [claim for claim in operations.values()
                  if claim.get('profile') == 'http'
                  and 'request_schema' in claim
                  and (action is None or action == claim['action'])]
    if len(candidates) != 1:
        raise ValueError('Select one declared HTTP Action with schemas')
    return candidates[0]


def _endpoint(fields, claim):
    name = claim['interface']
    try:
        interface = fields['boundaries']['io']['server'][name]
    except (KeyError, TypeError) as error:
        message = f'Manifest must declare HTTP server {name!r}'
        raise ValueError(message) from error
    endpoint, route_name = claim['endpoint'], claim['route_name']
    if (
        not isinstance(interface, dict)
        or interface.get('transport') != 'http'
        or http_routes(interface.get('routes', {})).get(endpoint) != route_name
    ):
        raise ValueError(f'Expected declared route {route_name!r} on {endpoint}')
    method, path = endpoint.split(' ', 1)
    supported = ('GET', 'PUT', 'POST', 'DELETE',
                 'OPTIONS', 'HEAD', 'PATCH', 'TRACE')
    if method not in supported:
        raise ValueError(f'OpenAPI does not support HTTP method {method!r}')
    return method.lower(), path


def _content(schema):
    return {'application/json': {'schema': deepcopy(schema)}}


def _responses(claim):
    by_status = {}
    for name, status, _ in claim['outcomes']:
        schema = claim['response_schemas'][name]
        by_status.setdefault(str(status), {})[name] = schema
    responses = {}
    for status, outcomes in by_status.items():
        distinct = {json.dumps(schema, sort_keys=True): schema
                    for schema in outcomes.values()}
        schemas = list(distinct.values())
        schema = schemas[0] if len(schemas) == 1 else {'oneOf': schemas}
        responses[status] = {'description': ', '.join(outcomes),
                             'content': _content(schema)}
    return responses


def export_openapi(manifest, *, action=None):
    """Export one declared HTTP Action and its payload schemas."""
    fields = manifest['fields']
    claim = _http_claim(manifest, action)
    method, path = _endpoint(fields, claim)
    request = claim['request_schema']
    name = request.get('properties', {}).get('name')
    if (not isinstance(name, dict) or name.get('const') != claim['action']
            or 'name' not in request.get('required', [])):
        raise ValueError('Request schema must select the declared Action')
    operation = {
        'operationId': claim['action'],
        'requestBody': {'required': True, 'content': _content(request)},
        'responses': _responses(claim),
    }
    info = {'title': fields['name'],
            'version': str(manifest['source']['version'])}
    return {'openapi': '3.1.0', 'info': info,
            'paths': {path: {method: operation}}}
