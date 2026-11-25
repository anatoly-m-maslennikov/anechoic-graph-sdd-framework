"""Compose the declared-only Current narrowing graph."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_narrowing_collect import NarrowingCollection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_narrowing_resolve import NarrowingResolution


class _Narrowing(NarrowingCollection, NarrowingResolution):
    pass


def compose_narrowing_graph(carriers):
    """Compose a declared-only IS_NARROWER_THAN tree from Current carriers."""
    graph = _Narrowing()
    graph.collect(carriers)
    graph.claim_edges()
    graph.native_edges()
    return graph.finish()
