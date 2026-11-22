"""Shared Graph Rule validation test inputs."""


class Recorder:
    def __init__(self) -> None:
        self.findings: list[tuple[str, str, str]] = []
        self.gaps: list[tuple[str, str]] = []

    def fail(self, code: str, field: str, reason: str) -> None:
        self.findings.append((code, field, reason))

    def gap(self, field: str, reason: str) -> None:
        self.gaps.append((field, reason))


CARDINALITY = '''# Summary
Check dependency counts.

```yaml
graph_rule_type: cardinality
applies_to:
  node: "Entity/Node/Continuant/Selection//Dependent Entity Occurrences"
  relation_type: IS_BORNE_BY
  direction: outgoing
condition:
  other_endpoint:
    - Entity
  minimum: 1
  maximum: 1
```
'''
