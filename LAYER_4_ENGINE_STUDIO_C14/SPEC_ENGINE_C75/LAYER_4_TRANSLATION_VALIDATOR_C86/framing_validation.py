"""Build finite framing witnesses from normalized claims, independent of the emitter."""


def _patterns(claim, role):
    if role == 'contract':
        groups = ([claim['delimiter']], claim['line_endings'])
    elif role == 'solution':
        groups = (claim['opening_prefixes'], claim['closing_prefixes'])
    else:
        raise ValueError('invalid framing role')
    if any(len(group) > 8 for group in groups):
        raise ValueError('framing witness budget exceeded')
    lengths = [[len(pattern) for pattern in group] for group in groups]
    if any(length > 32 for group in lengths for length in group) or sum(map(sum, lengths)) > 128:
        raise ValueError('framing witness budget exceeded')
    if role == 'contract':
        delimiter = lengths[0][0]
        openings = [delimiter + ending for ending in lengths[1]]
        closings = [before + delimiter + after for before in lengths[1] for after in lengths[1]]
    else:
        openings, closings = lengths
    budget = (2 + sum(length + 1 for length in openings + closings)
              + sum(6 + 2 * close + min(opening, close)
                    for opening in openings for close in closings))
    if budget > 512:
        raise ValueError('framing witness budget exceeded')
    if role == 'contract':
        delimiter = bytes(claim['delimiter'])
        endings = [bytes(value) for value in claim['line_endings']]
        return ([delimiter + ending for ending in endings],
                [before + delimiter + after for before in endings for after in endings])
    if role == 'solution':
        return ([bytes(value) for value in claim['opening_prefixes']],
                [bytes(value) for value in claim['closing_prefixes']])
    raise ValueError('invalid framing role')


def _expected(raw, claim, role):
    openings, closings = _patterns(claim, role)
    opening = next((len(value) for value in openings if raw.startswith(value)), None)
    if opening is None:
        return None, None
    for pos in range(opening - 1, len(raw)):
        if role == 'contract':
            endings = [bytes(value) for value in claim['line_endings']]
            delimiter = bytes(claim['delimiter'])
            before = next((value for value in endings if raw.startswith(value, pos)), None)
            if before is None or not raw.startswith(delimiter, pos + len(before)):
                continue
            end = pos + len(before) + len(delimiter)
            after = next((value for value in endings if raw.startswith(value, end)), None)
            stop = end + len(after) if after is not None else None
        else:
            close = next((value for value in closings if raw.startswith(value, pos)), None)
            stop = pos + len(close) if close is not None else None
        if stop is not None:
            return (opening, pos, stop), raw[stop:]
    return None, None


def _witnesses(claim, role):
    openings, closings = _patterns(claim, role)
    cases = {b'', b'\x00', *openings, *closings}
    for pattern in openings + closings:
        cases.update(pattern[:i] for i in range(len(pattern)))
    for opening in openings:
        for closing in closings:
            for middle in (b'', b'\x00'):
                base = opening + middle + closing
                cases.update((base, base + b'\x00\xff', base + closing + b'\xff'))
                cases.update(base[:len(opening) + len(middle) + i]
                             for i in range(len(closing)))
            for overlap in range(1, min(len(opening), len(closing)) + 1):
                if opening[-overlap:] == closing[:overlap]:
                    cases.add(opening + closing[overlap:] + b'\xff')
    return sorted(cases)


def framing_checks(claim, role):
    """Return finite Lean Boolean checks for the role's bounds and body projections."""
    namespace = {'contract': 'CarrierBodyContract', 'solution': 'CarrierBodySolution'}[role]
    checks = []
    for raw in _witnesses(claim, role):
        bounds, body = _expected(raw, claim, role)
        bound_form = 'none' if bounds is None else f'some {bounds}'
        outcome = 'missingDelimiter' if body is None else f'body {list(body)}'
        checks.append(f'({namespace}.bounds {list(raw)} == {bound_form})')
        checks.append(f'({namespace}.body {list(raw)} == {namespace}.Outcome.{outcome})')
    return checks
