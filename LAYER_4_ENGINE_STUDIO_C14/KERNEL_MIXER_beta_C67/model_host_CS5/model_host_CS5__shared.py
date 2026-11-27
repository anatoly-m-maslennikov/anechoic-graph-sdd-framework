"""Read accepted Model bytes from the Kernel generation store."""


def reviewed_native_model(connection, lock):
    """Return (generation, exact UTF-8 bytes), or None before admission."""
    with lock:
        row = connection.execute(
            "SELECT id, model FROM ops_generation"
        ).fetchone()
    return (row[0], row[1].encode("utf-8")) if row else None
