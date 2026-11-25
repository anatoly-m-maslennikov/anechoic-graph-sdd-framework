import json


def lean_string(value):
    if not value or value.isprintable():
        return json.dumps(value, ensure_ascii=False)
    return 'String.ofList [' + ', '.join(f'Char.ofNat {ord(char)}' for char in value) + ']'
