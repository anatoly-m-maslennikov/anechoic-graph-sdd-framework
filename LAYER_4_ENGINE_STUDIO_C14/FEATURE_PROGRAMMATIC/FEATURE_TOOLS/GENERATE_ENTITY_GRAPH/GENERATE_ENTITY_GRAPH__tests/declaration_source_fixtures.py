"""Supplied source carriers for Relation and Graph Rule declaration tests."""

from __future__ import annotations

import hashlib

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import get_profile


def relation_carrier(atom_id: str, subject: str, graph_scope: str, version: int = 1) -> dict:
    body = f"## Scope\n\n`{subject.split(': ')[-1]} Relation` in the **{graph_scope}**.\n\n## Claim\nText."
    raw_body = body + "\n"
    raw = (
        f"---\natom_id: {atom_id}\nversion: {version}\ncontent_role: Requirement\n"
        f"status: Active\n---\n{raw_body}"
    ).encode("utf-8")
    return {
        "source": {
            "atom_id": atom_id,
            "version": version,
            "path": f"{atom_id}.md",
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "metadata": {
            "atom_id": atom_id,
            "version": version,
            "content_role": "Requirement",
            "status": "Active",
        },
        "subjects": {"governs": subject},
        "body": body,
        "raw_body": raw_body,
        "raw": raw,
    }


def refresh_raw(carrier: dict) -> None:
    source = carrier["source"]
    metadata = carrier["metadata"]
    body = carrier["body"]
    raw_body = body if body.endswith("\n") else body + "\n"
    carrier["raw_body"] = raw_body
    raw = (
        f"---\natom_id: {source['atom_id']}\nversion: {source['version']}\n"
        f"content_role: {metadata['content_role']}\nstatus: {metadata['status']}\n---\n{raw_body}"
    ).encode("utf-8")
    source["sha256"] = hashlib.sha256(raw).hexdigest()
    carrier["raw"] = raw


def graph_rule_carrier(atom_id: str = "CA-R-901021", version: int = 3, yaml_type: str = "whitelist") -> dict:
    if yaml_type == "cardinality":
        yaml_block = (
            "```yaml\ngraph_rule_type: cardinality\napplies_to:\n"
            '  node: "Entity/Node/Continuant/Selection//Dependent Entity Occurrences"\n'
            "  relation_type: IS_BORNE_BY\n  direction: outgoing\ncondition:\n"
            "  other_endpoint: [Entity]\n  minimum: 0\n  maximum: null\n```\n"
        )
        summary = "Cardinality fixture."
    else:
        yaml_block = (
            "```yaml\ngraph_rule_type: " + yaml_type + "\napplies_to:\n"
            "  relation_type: evaluation_for\ncondition:\n"
            '  source: ["Entity/Node/Continuant/Atom/Content Role: Evaluation"]\n'
            '  target: ["Entity/Node/Continuant/Atom/Content Role: Requirement"]\n```\n'
        )
        summary = "Permit evaluation links."
    body = "# Summary\n\n" + summary + "\n\n" + yaml_block
    metadata = {
        "atom_id": atom_id,
        "version": version,
        "content_role": "Requirement",
        "type": "Graph Rule",
        "status": "Active",
    }
    raw = (
        f"---\natom_id: {atom_id}\nversion: {version}\ncontent_role: Requirement\n"
        f"type: Graph Rule\nstatus: Active\n---\n{body}"
    ).encode("utf-8")
    return {
        "source": {
            "atom_id": atom_id,
            "version": version,
            "path": f"{atom_id}.md",
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "metadata": metadata,
        "subjects": {"governs": "Entity/Node/Continuant/Atom.Relations"},
        "body": body,
        "raw_body": body,
        "raw": raw,
    }


def support_carriers() -> list[dict]:
    rows = []
    approvals = ("CA-R-2001", "CA-D-637", "CA-R-1996", *(pin.atom_id for pin in get_profile("approved").grammar_pins))
    role_by_code = {"C": "Concern", "A": "Analysis", "P": "Plan", "R": "Requirement", "M": "Method", "E": "Evaluation", "D": "Delivery", "O": "Operations"}
    for identifier in approvals:
        role_code = identifier.rsplit("-", 2)[1]
        version = 1
        text = f"Current support evidence for {identifier} at {version}."
        raw = text.encode("utf-8")
        rows.append(
            {
                "source": {
                    "atom_id": identifier,
                    "version": version,
                    "path": f"{identifier}.md",
                    "sha256": hashlib.sha256(raw).hexdigest(),
                },
                "metadata": {
                    "atom_id": identifier,
                    "version": version,
                    "content_role": role_by_code[role_code],
                    "status": "Active",
                },
                "raw": raw,
            }
        )
    return rows
