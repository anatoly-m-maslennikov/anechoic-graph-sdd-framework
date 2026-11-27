"""Render a normalized record shape as Mermaid."""


def shape_to_mermaid(claim):
    diagram = f'classDiagram\n    class ShapeRecord["{claim["record"]}"] {{'
    for name, typ in claim["fields"].items():
        diagram += f"\n        {typ} {name}"
    diagram += f'\n    }}\n    class ShapeSubtype["{claim["subtype"]}"]'
    if claim["base"]:
        diagram += "\n    ShapeRecord <|-- ShapeSubtype"
    return diagram
