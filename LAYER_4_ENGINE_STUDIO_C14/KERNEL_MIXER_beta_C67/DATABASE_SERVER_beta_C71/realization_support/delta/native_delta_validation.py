"""Validate and stage addressed native delta data."""

from collections import Counter
import json
from pathlib import PurePosixPath
import re

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation__shared import _digest
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.ingestion_issues import duplicate_dependencies
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.native.native__shared import stage_atom_rows, validate_native_snapshot


_CARRIER = re.compile(
    r"([A-Z][A-Z0-9]*-[STPC]-[0-9]+)(@[1-9][0-9]*(?:-draft)?)?[-.].*\.md\Z"
)

_EDGE = (
    "source_kind",
    "source_ref",
    "target_kind",
    "target_ref",
    "relation_type",
    "derived",
)


class DeltaReconciliationRequired(ValueError):
    """The retained state cannot safely receive a bounded delta."""


def _paths(value):
    if not isinstance(value, list) or not value or len(value) > 1024:
        raise ValueError("Native delta requires Ticket paths")
    result = set()
    for item in value:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or any(not isinstance(part, str) for part in item)
        ):
            raise ValueError("Invalid Ticket path")
        parent, filename = item
        path = PurePosixPath(parent)
        if (
            path.is_absolute()
            or str(path) != parent
            or ".." in path.parts
            or "\\" in parent
            or not _CARRIER.fullmatch(filename)
            or "/" in filename
            or "\\" in filename
        ):
            raise ValueError("Invalid Ticket path")
        result.add((parent, filename))
    if len(result) != len(value):
        raise ValueError("Duplicate Ticket path")
    return result


def _inverse(bindings, relation_types):
    endpoints = bindings.get("endpoints")
    if not isinstance(endpoints, dict) or set(endpoints) != set(
        relation_types
    ):
        raise ValueError(
            "Snapshot relation types differ from the admitted Model"
        )
    inverse = {}
    for name, entry in endpoints.items():
        if (
            not isinstance(entry, list)
            or len(entry) != 2
            or not isinstance(entry[0], dict)
            or type(entry[1]) is not bool
        ):
            raise ValueError("Invalid Model relation binding")
        if not entry[1] and "inverse_alias" in entry[0]:
            target = entry[0]["inverse_alias"]
            if (
                not isinstance(target, str)
                or target == name
                or target not in endpoints
                or name in inverse
                or target in inverse
            ):
                raise ValueError("Ambiguous Model inverse binding")
            inverse[name], inverse[target] = target, name
    return inverse


def _validate_edges(rows, inverse):
    direct = Counter(tuple(row) for row in rows if not row[5])
    derived = Counter(tuple(row) for row in rows if row[5])
    expected = Counter()
    for (
        source_kind,
        source,
        target_kind,
        target,
        relation,
        _,
    ), count in direct.items():
        if relation in inverse:
            expected[
                (
                    target_kind,
                    target,
                    source_kind,
                    source,
                    inverse[relation],
                    True,
                )
            ] += count
    if derived != expected:
        raise DeltaReconciliationRequired(
            "Ambiguous native relation ownership; full reconciliation required"
        )


def _stage(connection, table, rows, width):
    for offset in range(0, len(rows), 256):
        batch = rows[offset : offset + 256]
        placeholders = ", ".join(
            ["(" + ", ".join(["?"] * width) + ")"] * len(batch)
        )
        connection.execute(
            f"INSERT INTO {table} VALUES {placeholders}",
            [value for row in batch for value in row],
        )


def _old_rows(connection, paths, *, archive=False):
    connection.execute(
        (
            "CREATE TEMP TABLE int_delta_paths (relative_path VARCHAR, filena"
            "me VARCHAR)"
        )
    )
    _stage(connection, "int_delta_paths", list(paths), 2)
    rows = connection.execute("""SELECT n.reference, n.exact_ref,
        n.relative_path, n.filename, n.status_group
        FROM main.mrt_atom_references n JOIN int_delta_paths p USING
            (relative_path, filename)""").fetchall()
    if (
        len({(row[2], row[3]) for row in rows}) != len(rows)
        or len({row[0] for row in rows}) != len(rows)
        or len({row[1] for row in rows}) != len(rows)
    ):
        raise DeltaReconciliationRequired(
            "Ambiguous Ticket path or identities; full reconciliation required"
        )
    if archive and any(row[4] != "Archived" for row in rows):
        raise ValueError("Archive delta cannot replace live Atoms")
    return [(row[0], row[1]) for row in rows]


def _validate_atom_paths(atoms, paths):
    for atom in atoms:
        path = (atom.relative_path, atom.filename)
        match = _CARRIER.fullmatch(atom.filename)
        if (
            path not in paths
            or not match
            or match.group(1) != atom.reference.split("@")[0]
            or match.group(2)
            and match.group(1) + match.group(2) != atom.exact_ref
        ):
            raise ValueError(
                "Atom does not belong to an addressed native path"
            )


def _check_conflicts(connection):
    conflict = connection.execute("""SELECT 1 FROM (
        SELECT relative_path, filename FROM main.mrt_atom_references WHERE
            reference IN (SELECT reference FROM int_admission_atoms)
        UNION ALL
        SELECT relative_path, filename FROM main.mrt_atom_references WHERE
            exact_ref IN (SELECT exact_ref FROM int_admission_atoms)
        ) n WHERE NOT EXISTS (SELECT 1 FROM int_delta_paths p
            WHERE p.relative_path = n.relative_path AND p.filename =
                n.filename) LIMIT 1""").fetchone()
    if conflict:
        raise DeltaReconciliationRequired(
            (
                "Ticket identity was admitted at another path; reconcile both"
                " paths"
            )
        )


def _validate_delta(
    connection, data, model, manifest_sha256, *, archive=False
):
    paths = _paths(data["paths"])
    snapshot = data["snapshot"]
    digest_data = {"paths": data["paths"], "snapshot": snapshot}
    if "carrier_hashes" in data:
        digest_data["carrier_hashes"] = data["carrier_hashes"]
    if _digest(digest_data) != data["snapshot_sha256"]:
        raise ValueError("Native delta digest mismatch")
    bindings = json.loads(model)["bindings"]
    atoms, relations = validate_native_snapshot(
        snapshot, manifest_sha256, bindings
    )
    _validate_delta_issues(connection, snapshot, paths)
    if archive and (
        any(
            "09_archived" not in PurePosixPath(parent).parts
            for parent, _ in paths
        )
        or any(atom.status_group != "Archived" for atom in atoms)
        or snapshot.get("spec_sizes")
        or snapshot.get("lifecycle_lenses")
    ):
        raise ValueError("Archive delta requires canonical Archived carriers")
    inverse = _inverse(bindings, snapshot["relation_types"])
    _validate_atom_paths(atoms, paths)
    old = _old_rows(connection, paths, archive=archive)
    stage_atom_rows(connection, snapshot["atoms"])
    _check_conflicts(connection)
    new_edges = [
        tuple(getattr(edge, key) for key in _EDGE) for edge in relations
    ]
    _validate_edges(new_edges, inverse)
    return snapshot, old, new_edges, inverse


def _validate_delta_issues(connection, snapshot, paths):
    addressed = {str(PurePosixPath(parent) / name) for parent, name in paths}
    issues = snapshot.get("ingestion_issues", [])
    if any(
        issue["relative_path"] not in addressed
        or not addressed.issuperset(issue["related_paths"])
        for issue in issues
    ):
        raise ValueError(
            "Ingestion issue is outside the addressed native paths"
        )
    if any(
        issue["code"] in {"duplicate_revision", "duplicate_current"}
        for issue in issues
    ) or duplicate_dependencies(connection, snapshot, addressed):
        raise DeltaReconciliationRequired(
            "Duplicate Atom group requires full reconciliation"
        )
