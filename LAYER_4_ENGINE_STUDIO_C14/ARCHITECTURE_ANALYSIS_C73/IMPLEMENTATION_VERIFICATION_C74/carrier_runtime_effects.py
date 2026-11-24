"""Review only the pinned carrier pilot and its trusted CPython calls."""

import ast
import hashlib
import platform
import re

_REVIEWED_CPYTHON_3147_AST_SHA256 = {
    '9271064c91ab830ff7831cb5c0310106f67fd4508e1579a0d088049c0aae6fe9': 'old',
    'af06496100d137b474d0fd112c1437bd26294d47b5a0e0a1b8c8e4c30f73c8fd': 'fixed',
}
_RUNTIME = ('CPython', '3.14.7')


def check_effects(effects):
    """Classify reviewed effects; unrecognized effects cannot pass."""
    allowed = {'local', 'private_regex_cache'}
    forbidden = {'project_read', 'project_write', 'ambient', 'io'}
    effects = set(effects)
    if not effects:
        return 'unresolved'
    if effects & forbidden:
        return 'forbidden'
    if effects - allowed:
        return 'unresolved'
    return 'permitted'


def _binding(call):
    name = ast.unparse(call.func)
    if name == 'raw.startswith':
        return ('bytes.startswith', {'self': 'raw', 'prefix': 'literal bytes'})
    if name == 'len':
        return ('builtins.len', {'obj': 'literal bytes'})
    if name == 're.search':
        return ('re.search', {'pattern': 'literal bytes', 'string': 'raw', 'flags': 'opening_end - 1'})
    if name == '_CLOSING_DELIMITER.search':
        return ('re.Pattern.search', {'self': 'compiled pattern', 'string': 'raw', 'pos': 'opening_end - 1', 'endpos': 'default'})
    if name in ('closing.start', 'closing.end'):
        return ('re.Match.' + name.split('.')[1], {'self': 'closing', 'group': 0})
    if name == 'frontmatter_bounds':
        return ('carrier_body.frontmatter_bounds', {'raw': 'raw'})
    if name == 'ValueError':
        return ('builtins.ValueError', {'message': 'formatted path'})
    return None


def _function_effects(tree, variant, result):
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        calls = []
        for call in sorted((n for n in ast.walk(node) if isinstance(n, ast.Call)),
                           key=lambda n: (n.lineno, n.col_offset)):
            binding = _binding(call)
            if binding is None:
                return 'unresolved call at line ' + str(call.lineno)
            calls.append({'line': call.lineno, 'callable': binding[0], 'binding': binding[1]})
        effects = ['local']
        if variant == 'old' and node.name == 'frontmatter_bounds':
            effects.append('private_regex_cache')
        if node.name == 'source_body':
            effects = sorted(set(effects + result['functions']['frontmatter_bounds']['transitive_effects']))
        result['functions'][node.name] = {'line': node.lineno, 'calls': calls,
                                         'transitive_effects': effects,
                                         'status': check_effects(effects)}
    return None


def analyze_carrier(source):
    """Return a bounded call-time review, not a proof of Python execution."""
    runtime = (platform.python_implementation(), platform.python_version())
    result = {'runtime': list(runtime), 'status': 'unresolved', 'functions': {},
              'scope': 'known call effects only; not overall verification or a Python semantics proof',
              'import_effects': 'unresolved: import machinery runs before the function call and is outside its state/IO boundary',
              'assumptions': ['exact built-in bytes and concrete pathlib path',
                              'unmodified CPython builtins, re module and compiled pattern',
                              'no concurrent mutation of module bindings'],
              'analysis_limit': 'This ledger does not establish Code Analysis completeness or Lean/Python equivalence.',
              'provenance': {'python': 'CPython 3.14.7, Engine uv lock',
                             're_module': re.__file__,
                             'cache_evidence': 'CPython re module caches compiled regular expressions',
                             'native_effects': 'trusted runtime assumptions; C internals are not formally verified'},
              'unsupported': ['subclasses and modified runtime bindings',
                              'allocator, interpreter and operating-system internals',
                              'unmodeled operations and import-time effects']}
    if tuple(runtime) != _RUNTIME:
        result['reason'] = 'runtime is not pinned CPython 3.14.7'
        return result
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        result['reason'] = 'source cannot be parsed'
        return result
    digest = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
    variant = _REVIEWED_CPYTHON_3147_AST_SHA256.get(digest)
    result.update(ast_sha256=digest, variant=variant)
    if variant is None:
        result['reason'] = 'source shape is not reviewed'
        return result
    problem = _function_effects(tree, variant, result)
    if problem:
        result['reason'] = problem
        return result
    if variant == 'fixed':
        compile_call = next(n for n in ast.walk(tree) if isinstance(n, ast.Call) and ast.unparse(n.func) == 're.compile')
        result['import_call'] = {'line': compile_call.lineno, 'callable': 're.compile',
                                 'binding': {'pattern': 'literal bytes', 'flags': 0},
                                 'effects': ['local', 'private_regex_cache']}
    result['import_review'] = ('re.compile may mutate the private regex cache during module initialization'
                               if variant == 'fixed' else 're and pathlib imports are outside call-time review')
    result['implicit_operations'] = ['bytes slicing', 'Path formatting on error', 'exception construction']
    result['status'] = 'permitted' if all(v['status'] == 'permitted' for v in result['functions'].values()) else 'unresolved'
    return result
