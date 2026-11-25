"""Relational storage for the admitted Project Structure."""

import json


def ensure_structure_table(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS mrt_project_structure (
        component_id VARCHAR PRIMARY KEY, parent VARCHAR, source_path VARCHAR,
        ref VARCHAR, sha256 VARCHAR, fields VARCHAR, component_extra VARCHAR, present_keys VARCHAR)""")


def replace_structure(connection, structure):
    document = json.loads(structure) if isinstance(structure, str) else structure
    components = document["components"]
    project = document["project"]
    facts = {key: value for key, value in document.items() if key != "components"}
    facts["project"] = {key: value for key, value in project.items() if key not in ("ref", "sha256")}
    connection.execute("DELETE FROM mrt_project_structure")
    connection.execute("INSERT INTO mrt_project_structure VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       ["C00", None, None, project.get("ref"), project.get("sha256"), None, None, None])
    for component_id, item in components.items():
        if not isinstance(item, dict) or component_id == "C00":
            raise ValueError("Invalid Project Structure Component")
        connection.execute("INSERT INTO mrt_project_structure VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           [component_id, item.get("parent"), item.get("source_path"), item.get("ref"),
                            item.get("sha256"), json.dumps(item.get("fields")),
                            json.dumps({key: value for key, value in item.items()
                                        if key not in ("parent", "source_path", "ref", "sha256", "fields")}),
                            json.dumps(list(item))])
    return json.dumps(facts, sort_keys=True, separators=(",", ":"))


def structure_document(connection, facts):
    document = json.loads(facts)
    project_ref, project_hash = connection.execute(
        "SELECT ref, sha256 FROM mrt_project_structure WHERE component_id = 'C00'"
    ).fetchone()
    document["project"].update({"ref": project_ref, "sha256": project_hash})
    components = {}
    for component_id, parent, source_path, ref, digest, fields, extra, present in connection.execute(
        "SELECT component_id, parent, source_path, ref, sha256, fields, component_extra, present_keys "
        "FROM mrt_project_structure WHERE component_id <> 'C00'"
    ).fetchall():
        values = {"parent": parent, "source_path": source_path, "ref": ref,
                  "sha256": digest, "fields": json.loads(fields)} | json.loads(extra)
        components[component_id] = {key: values[key] for key in json.loads(present)}
    document["components"] = components
    return document


def structure_bytes(connection, facts):
    return json.dumps(structure_document(connection, facts), sort_keys=True, separators=(",", ":")).encode()


def component_ids(connection):
    return {row[0] for row in connection.execute("SELECT component_id FROM mrt_project_structure").fetchall()}
