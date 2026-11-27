"""Build and attach the shared projection of delivered Framework Atoms."""

from hashlib import sha256
import os
from pathlib import Path
import tempfile

from .carrier_read__pub import parse_carrier
from .source_row__pub import canonical


LAYERS = ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")
_SOURCE = Path(__file__).resolve().parents[4]


def _inputs(source: Path):
    digest = sha256(b"framework-atoms-v1\0")
    records = []
    for layer in LAYERS:
        paths = sorted((source / layer).rglob("*.md"))
        if not paths:
            raise ValueError(f"Missing delivered Framework Atoms in {layer}")
        for path in paths:
            relative = path.relative_to(source).as_posix()
            raw = path.read_bytes()
            digest.update(
                relative.encode("utf-8") + b"\0" + sha256(raw).digest()
            )
            records.append((relative, raw))
    return digest.hexdigest(), records


def _current(database: Path, digest: str) -> bool:
    import duckdb

    if not database.is_file():
        return False
    try:
        with duckdb.connect(str(database), read_only=True) as connection:
            return connection.execute(
                "SELECT digest FROM source_version"
            ).fetchall() == [(digest,)]
    except duckdb.Error:
        return False


def _atom(relative: str, raw: bytes) -> tuple:
    carrier = parse_carrier(raw, Path(relative))
    header = carrier.metadata
    state = header.get("state")
    if (
        header.get("atom_family") != "SPEC"
        or not isinstance(state, dict)
        or state.get("status") != "active"
        or type(state.get("version")) is not int
    ):
        raise ValueError(f"{relative}: expected a delivered Active SPEC Atom")
    return (
        relative,
        header["atom_id"],
        state["version"],
        header.get("tier"),
        canonical(header),
        carrier.body,
    )


def _publish(database: Path, digest: str, records) -> None:
    import duckdb

    with tempfile.TemporaryDirectory(
        prefix="framework-", dir=database.parent
    ) as staging:
        candidate = Path(staging) / database.name
        with duckdb.connect(
            str(candidate), config={"temp_directory": ""}
        ) as connection:
            connection.execute(
                "CREATE TABLE atoms (source_path VARCHAR NOT NULL, atom_id VARCHAR PRIMARY KEY, "
                "version BIGINT NOT NULL, tier BIGINT, header JSON NOT NULL, markdown VARCHAR NOT NULL)"
            )
            connection.executemany(
                "INSERT INTO atoms VALUES (?, ?, ?, ?, ?, ?)",
                [_atom(relative, raw) for relative, raw in records],
            )
            connection.execute(
                "CREATE TABLE source_version AS SELECT ?::VARCHAR AS digest",
                [digest],
            )
        candidate.replace(database)


def attach_framework(connection, *, source: Path = _SOURCE) -> None:
    """Attach a read-only Framework database before disabling external access."""
    value = os.environ.get("ANECHOIC_FRAMEWORK_DB_ROOT")
    if not value:
        return
    import fcntl

    directory = Path(value)
    if (
        not directory.is_absolute()
        or directory.resolve(strict=True) != directory
    ):
        raise ValueError(
            "Framework database requires an absolute runtime directory"
        )
    database = directory / "framework.duckdb"
    descriptor = os.open(
        directory / "framework.lock",
        os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
        0o600,
    )
    with os.fdopen(descriptor, "a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if database.is_symlink():
            raise ValueError("Framework database must be a regular file")
        digest, records = _inputs(source)
        if not _current(database, digest):
            _publish(database, digest, records)
        escaped = str(database).replace("'", "''")
        connection.execute(f"ATTACH '{escaped}' AS framework (READ_ONLY)")
