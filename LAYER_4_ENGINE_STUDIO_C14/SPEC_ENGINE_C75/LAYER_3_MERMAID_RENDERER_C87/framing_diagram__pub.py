from ..LAYER_2_FORMAL_MODEL_C85.carrier_framing__pub import _validate


def framing_to_mermaid(claim):
    """Show the solution scanner and its framing outcomes."""
    claim = _validate(claim, 'solution')
    opening = ', '.join(str(list(pattern)) for pattern in claim['opening_prefixes'])
    closing = ', '.join(str(list(pattern)) for pattern in claim['closing_prefixes'])
    return (f'flowchart TD\n  A[Raw bytes] --> B{{"Opening prefix: {opening}"}}\n'
            f'  B -->|matched| C["Scan from opening minus one: {closing}"]\n'
            '  B -->|missing| M[Missing delimiter]\n'
            '  C -->|first match| D[Bounds and unchanged body tail]\n'
            '  C -->|missing| M\n')
