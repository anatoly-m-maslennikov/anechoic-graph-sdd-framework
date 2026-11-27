def lean_string(value):
    escaped = ['"']
    for char in value:
        code = ord(char)
        if 0xD800 <= code <= 0xDFFF:
            raise ValueError("Lean strings require Unicode scalar values")
        if char in ('"', "\\"):
            escaped.append("\\" + char)
        elif code < 0x20 or 0x7F <= code <= 0x9F:
            escaped.append(f"\\x{code:02x}")
        else:
            escaped.append(char)
    escaped.append('"')
    return "".join(escaped)
