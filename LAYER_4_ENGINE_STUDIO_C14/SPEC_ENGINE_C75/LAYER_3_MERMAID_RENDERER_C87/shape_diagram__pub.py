


def shape_to_mermaid(claim):
    lines = ['classDiagram', f'    class {claim["record"]} {{']
    lines += [f'        {typ} {name}' for name, typ in claim['fields'].items()]
    lines += ['    }', f'    class {claim["subtype"]}']
    if claim['base']:
        lines.append(f'    {claim["base"]} <|-- {claim["subtype"]}')
    return '\n'.join(lines)
