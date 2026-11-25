"""Read admitted Structure from the relational generation store."""

from ..DATABASE_SERVER_beta_C71.project_structure import structure_bytes


def read_structure(connection, lock):
    """Return (generation, canonical UTF-8 bytes), or None before admission."""
    with lock:
        row = connection.execute("SELECT id, structure_facts FROM ops_generation").fetchone()
        return (row[0], structure_bytes(connection, row[1])) if row else None
