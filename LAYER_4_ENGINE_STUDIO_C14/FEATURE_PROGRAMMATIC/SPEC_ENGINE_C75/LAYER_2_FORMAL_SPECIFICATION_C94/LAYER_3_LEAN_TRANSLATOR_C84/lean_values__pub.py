import json


def lean_string(value):
    if not value or value.isprintable():
        return json.dumps(value, ensure_ascii=False)
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise ValueError('Lean strings require Unicode scalar values')
    return '(String.ofList [' + ', '.join(f'Char.ofNat {ord(char)}' for char in value) + '])'
