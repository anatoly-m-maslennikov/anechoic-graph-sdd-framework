"""Fold admitted startup hash changes during the database server's lifetime."""

import asyncio
from contextlib import asynccontextmanager, suppress
import logging

import duckdb

from .carrier_checkpoint import checkpoint_changes_pending, fold_checkpoint


async def _maintain_checkpoint(connection, lock):
    try:
        while True:
            await asyncio.sleep(1)
            with lock:
                if not checkpoint_changes_pending(connection):
                    continue
                connection.begin()
                try:
                    fold_checkpoint(connection)
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
    except duckdb.Error:
        logging.getLogger("uvicorn.error").warning(
            "Startup hash checkpoint update failed"
        )


@asynccontextmanager
async def database_lifespan(connection, lock, history, _):
    maintenance = asyncio.create_task(_maintain_checkpoint(connection, lock))
    try:
        yield
    finally:
        maintenance.cancel()
        with suppress(asyncio.CancelledError):
            await maintenance
        if history is not None:
            history.close()
