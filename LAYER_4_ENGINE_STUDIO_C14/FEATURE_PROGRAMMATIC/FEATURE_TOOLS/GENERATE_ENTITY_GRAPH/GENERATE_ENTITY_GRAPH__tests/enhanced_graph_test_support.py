"""Bounded model/CFEL view preserves legacy graph behavior and evidence."""

from __future__ import annotations

from pathlib import Path
import sys


TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import extract_claim_constraints  # noqa: E402


def source(atom_id: str) -> dict[str, object]:
    return {"atom_id": atom_id, "version": 1, "path": f"sources/{atom_id}.md", "sha256": "a" * 64}

def carrier(
    atom_id: str, subjects: dict, body: str = "", *, declaration: bool = False,
    role: str = "Requirement", form: str = "Declaration",
) -> dict[str, object]:
    row = {"source": source(atom_id), "subjects": subjects, "body": body}
    if declaration:
        row["read_view"] = {"content_role": role, "type": form}
    return row

def property_population_records():
    records, diagnostics = extract_claim_constraints(carrier("CA-R-1001", {}, """## Claim
```CFEL
Bare:;
Bare{:1}:;
Name: [string]{:0..1};
Name{:1}: [string]{:0..1};
Name{:0..1}: [string]{:0..1};
Name{:2}: [string]{:0..1};
Required: [string]{:1};
Child: {:0..1};
Child{:0..1}: {:0..1};
Forbidden{:0}: [string]{:1};
Step.Content.Claim.Mermaid Scheme{::0..1} :: [markdown]{::1};
Step.Content.Claim.Mermaid Scheme.*[]{::0};
Node.**: [markdown];
Node.**[string]{:0+};
# Instances
Node.**//{:1};
PrimaryKind//$x{:1}
```
"""))
    return records, diagnostics

def fenced_scope_records():
    records, diagnostics = extract_claim_constraints(carrier("CA-R-1001", {}, """## Claim
````markdown
```CFEL
Outside: [string]{:1}
```
````
```CFEL
A{:1}: [int]{:1};
Atom/(.Role := Requirement)/(.Form := Rule);
IF(A) THEN(B ((RUN)) C);
Journal >| (Container == yes);
Node >| Container: yes;
Node {:0}((*));
Label: 'a;b';
FENCED_LABELS(Atom.Content.Claim): [in (CFEL)]{:0..1};
A + B{:1}
```
## Details
```CFEL
Details: [string]{:1}
```
"""))
    return records, diagnostics
