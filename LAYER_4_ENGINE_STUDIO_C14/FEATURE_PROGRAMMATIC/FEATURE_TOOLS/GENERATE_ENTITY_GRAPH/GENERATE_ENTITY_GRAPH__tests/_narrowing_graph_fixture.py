"""Narrowing graph carrier fixtures."""


def carrier(atom_id, active, *, form="Declaration", body=""):
    return {
        "source": {
            "atom_id": atom_id,
            "version": 1,
            "path": f"sources/{atom_id}.md",
        },
        "subjects": {"active": active, "passive": []},
        "body": body,
        "read_view": {"content_role": "Requirement", "type": form},
    }


def claim(expression):
    return f"## Claim\n\n```python\n{expression}\n```\n"


def event_record_claim():
    return """## Claim
### Formal Claim
```python
from anechoic.model import Continuant
from anechoic.formal_claims import declare_entity
class EventRecord(Continuant):
    pass
declare_entity(entity_name="Event Record", entity_class=EventRecord)
```
"""
