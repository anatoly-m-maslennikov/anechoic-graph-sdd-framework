"""Lower a pinned formal specification chain to Lean declarations."""

import json

from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared import normalize_spec
from .framing_lean__pub import framing_to_lean
from .lean_values__pub import lean_string
from .shape_lean__pub import shape_to_lean


def _lean_declaration(role, source, payload):
    value = {'source': source, 'claim': payload}
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=False)
    return f'def {role} : Except String Lean.Json := Lean.Json.parse {lean_string(encoded)}'


def compile_lean(model):
    """Return Lean source, normalized claims and source-linked gaps."""
    normalized = normalize_spec(model)
    claims = normalized['claims']
    declarations = [_lean_declaration(role, model[role]['source'], claim)
                    for role, claim in claims.items()]
    framing_models = []
    for role in ('contract', 'solution'):
        if role not in claims:
            continue
        languages = [language for language, _ in model[role]['claims']]
        if languages == ['python shape']:
            framing_models.append(shape_to_lean(claims[role], role))
        if 'python framing' in languages:
            framing = claims[role]['framing'] if len(languages) > 1 else claims[role]
            framing_models.append(framing_to_lean(framing, role))
    lines = ['import Lean', '', 'namespace AnechoicSpec'] + declarations
    lines += ['end AnechoicSpec', ''] + framing_models + ['']
    return {**normalized, 'lean': '\n'.join(lines), 'compiled_roles': list(claims)}
