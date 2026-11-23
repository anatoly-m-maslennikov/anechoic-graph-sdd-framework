"""Read accepted Structure bytes from the Kernel generation store."""


def read_structure(connection, lock):
    """Return (generation, exact UTF-8 bytes), or None before admission."""
    with lock:
        row = connection.execute("SELECT id, structure FROM ops_generation").fetchone()
    return (row[0], row[1].encode("utf-8")) if row else None
