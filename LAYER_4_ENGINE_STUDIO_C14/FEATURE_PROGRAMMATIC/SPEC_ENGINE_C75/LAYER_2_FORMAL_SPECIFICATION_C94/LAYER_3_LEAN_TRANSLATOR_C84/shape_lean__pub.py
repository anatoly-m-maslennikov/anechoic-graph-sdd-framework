def _quoted(kind, name):
    return f"«{kind}_{name}»"


def shape_to_lean(claim, role):
    q = _quoted
    types = sorted(set(claim["fields"].values()))
    params = "".join(f" ({q('T', t)} : Type)" for t in types)
    args = "".join(f" {q('T', t)}" for t in types)
    lines = [
        f"namespace Shape_{role}",
        f"structure {q('R', claim['record'])}{params} where",
    ]
    lines += [
        f"  {q('f', name)} : {q('T', typ)}"
        for name, typ in claim["fields"].items()
    ]
    if claim["base"] == claim["record"]:
        lines.append(
            (
                "structure "
                f"{q('S', claim['subtype'])}"
                f"{params}"
                " extends "
                f"{q('R', claim['record'])}"
                f"{args}"
                " where"
            )
        )
    else:
        lines.append(f"structure {q('S', claim['subtype'])} where")
    lines.append(f"end Shape_{role}")
    return "\n".join(lines)
