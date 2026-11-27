"""Source-linked findings and verdicts."""


def finding(source, field, message):
    return {"source": source, "field": field, "message": message}


def verdict(statuses):
    return (
        "conflicting"
        if "conflicting" in statuses
        else "unresolved"
        if not statuses or "unresolved" in statuses
        else "matched"
    )
