"""Parse specialized Tool API Contracts and general HTTP Contracts."""

import ast
import json

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

from .contract_literals import _call, _call_expression, _checks, _literal_string
from .trace_contract import TRACE_FIELDS, trace_profile
from .trace_manifest__pub import HTTP_BINDING_INPUTS, http_binding

_TOOL_OUTCOMES = {
    'success': (200, 'result'),
    'invalid_input': (400, 'typed_error'),
    'internal_error': (500, 'typed_error'),
}
_RESERVED_STATUSES = {'invalid_input': 400, 'internal_error': 500}
HTTP_CHECKS = {
    'interface.protocol': ('request', 'protocol', str),
    'interface.request_format': ('request', 'request_format', str),
    'interface.response_format': ('response', 'response_format', str),
    'input_format.fields': ('request', 'request_fields', list),
}
_TOOL_CHECKS = HTTP_CHECKS.keys() | {
    'interface.transport', 'interface.cli_required',
    'input_format.name', 'input_format.arguments', 'input_format.nullable_strings',
    'output_format.result_fields', 'output_format.value', 'output_format.text',
    'error_handling.error_fields', 'error_handling.internal_message',
    'preconditions.project_binding', 'preconditions.tool',
    'guarantees.query', 'guarantees.query_output',
    'effects.invalid_input_dispatch', 'effects.query_result', 'effects.bookmark',
}


def _tool_rows(args):
    operation = _literal_string(args['operation'])
    if operation != 'POST /tools' or not isinstance(args['outcomes'], ast.Dict):
        raise ValueError('unsupported operation or outcomes')
    rows = []
    try:
        for key, value in zip(args['outcomes'].keys, args['outcomes'].values):
            name, row = _literal_string(key), ast.literal_eval(value)
            if (type(row) is not tuple or len(row) != 2 or type(row[0]) is not int
                    or row != _TOOL_OUTCOMES.get(name)):
                raise ValueError('unsupported Tool API outcome')
            rows.append((name, row[0], row[1]))
    except (ValueError, TypeError) as error:
        raise ValueError('invalid outcome literal') from error
    if {row[0] for row in rows} != _TOOL_OUTCOMES.keys() or len(rows) != len(_TOOL_OUTCOMES):
        raise ValueError('outcomes must have unique keys')
    return rows


def _response_type(status, envelope):
    if type(status) is not int or not 200 <= status <= 599:
        return False
    if status in (204, 205, 304):
        return envelope == 'empty'
    return ((status == 200 and envelope == 'typed_error')
            or (status < 300 and envelope in ('result', 'empty'))
            or (300 <= status < 400 and envelope == 'redirect')
            or (status >= 400 and envelope == 'typed_error'))


def _http_rows(node):
    if not isinstance(node, ast.Dict) or not node.keys:
        raise ValueError('expected named HTTP outcomes')
    rows = {}
    for key, value in zip(node.keys, node.values):
        name, row = _literal_string(key), ast.literal_eval(value)
        if not name.strip() or name in rows:
            raise ValueError('empty or duplicate HTTP outcome')
        if (not isinstance(row, tuple) or len(row) != 2 or not _response_type(*row)
                or (name in _RESERVED_STATUSES and row[0] != _RESERVED_STATUSES[name])):
            raise ValueError(f'invalid status or envelope for HTTP outcome {name!r}')
        rows[name] = row
    return [(name, *row) for name, row in rows.items()]


def _schema_literal(node):
    for item in ast.walk(node):
        if isinstance(item, (ast.Tuple, ast.Set)):
            raise ValueError('schemas require JSON values')
        if isinstance(item, ast.Dict):
            names = [_literal_string(key) for key in item.keys]
            if len(names) != len(set(names)):
                raise ValueError('duplicate schema key')
    return ast.literal_eval(node)


def _schemas(args, outcomes):
    keys = ('request_schema', 'response_schemas')
    present = args.keys() & set(keys)
    if not present:
        return {}
    if len(present) != len(keys):
        raise ValueError('request and response schemas must be declared together')
    try:
        request, responses = (_schema_literal(args[key]) for key in keys)
        json.dumps([request, responses], allow_nan=False)
        if (not isinstance(request, dict) or not isinstance(responses, dict)
                or responses.keys() != {name for name, _, _ in outcomes}
                or any(not isinstance(schema, dict) for schema in responses.values())):
            raise ValueError('schemas must cover every named outcome')
        for schema in (request, *responses.values()):
            Draft202012Validator.check_schema(schema)
    except (TypeError, SchemaError) as error:
        raise ValueError('invalid JSON Schema') from error
    return {'request_schema': request, 'response_schemas': responses}


def _http_contract(call):
    binding = {'interface', 'action'}
    optional = {'checks', 'request_schema', 'response_schemas'}
    args = _call(call, 'declare_http_contract', binding | {'outcomes'},
                 optional | TRACE_FIELDS | HTTP_BINDING_INPUTS)
    fields = {key: _literal_string(args[key]) for key in sorted(binding)}
    literals = {key: _literal_string(args[key]) for key in HTTP_BINDING_INPUTS & args.keys()}
    routes = http_binding(literals)
    if len(routes) != 2 or any(not value.strip() for value in fields.values()):
        raise ValueError('expected a complete HTTP interface binding')
    profile = trace_profile(args, fields['action'])
    facts = _checks(args, HTTP_CHECKS)
    if any(HTTP_CHECKS[key][2] is str and len(values) != 1 for key, values in facts):
        raise ValueError('expected one value for a scalar HTTP check')
    outcomes = _http_rows(args['outcomes'])
    schemas = _schemas(args, outcomes)
    return {**fields, **routes, **profile.pop('trace', {}), **profile, 'profile': 'http', 'transport': 'http',
            'outcomes': outcomes, 'facts': facts, **schemas}


def parse_contract(source):
    """Read a general HTTP Contract or the specialized Tool API profile."""
    call = _call_expression(source)
    name = call.func.id if isinstance(call.func, ast.Name) else None
    if name == 'declare_http_contract':
        return _http_contract(call)
    if name not in ('declare_tool_api_contract', 'declare_contract'):
        raise ValueError('unsupported HTTP Contract call')
    args = _call(call, name, {'operation', 'outcomes'}, {'checks'})
    claim = {'operation': _literal_string(args['operation']), 'outcomes': _tool_rows(args),
             'facts': _checks(args, _TOOL_CHECKS)}
    if name == 'declare_tool_api_contract':
        claim['profile'] = 'tool_api'
    return claim
