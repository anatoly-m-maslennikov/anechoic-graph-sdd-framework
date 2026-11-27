"""Lifecycle source selection errors and bound query reader."""

from contextlib import contextmanager
from contextvars import ContextVar


class SourceSelectionError(ValueError):
    """A logical Atom source cannot be bound unambiguously and safely."""


class ArchiveNotLoadedError(SourceSelectionError):
    """The requested historical carrier has not been loaded into Workbench."""


_QUERY_READER = ContextVar("lifecycle_query_reader", default=None)


@contextmanager
def bind_query_reader(reader):
    token = _QUERY_READER.set(reader)
    try:
        yield
    finally:
        _QUERY_READER.reset(token)


def query_reader():
    return _QUERY_READER.get()
