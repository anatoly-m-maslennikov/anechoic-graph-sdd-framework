"""Build graph views from Current Atom carriers."""

from pathlib import Path
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared \
    import (
        read_current_carriers,
        read_current_model_carriers,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    current_subject_graph \
    import compose_current_graph  # fmt: skip


def build_current_graph(
    source_root: Path, repository: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    "Discover current carriers afresh, then pass only their data to the pure core."
    return compose_current_graph(
        read_current_carriers(source_root, repository)
    )


def build_enhanced_current_graph(
    source_root: Path, repository: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    "Discover current carriers and add diagnostic-only model and Claim records."

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
        current_subject_graph \
        import compose_enhanced_current_graph  # fmt: skip

    return compose_enhanced_current_graph(
        read_current_carriers(source_root, repository)
    )


def build_current_model_graph(
    source_root: Path, repository: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the bounded Current model view from its Declaration frontier."""

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
        current_subject_graph \
        import compose_enhanced_current_graph  # fmt: skip

    return compose_enhanced_current_graph(
        read_current_model_carriers(source_root, repository)
    )


def build_current_contract_graph(
    source_root: Path,
    repository: Path,
) -> dict[str, Any]:
    "Build the source-bound contract view from one explicit Current selection."

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
        contract_graph \
        import compose_contract_graph  # fmt: skip

    return compose_contract_graph(
        read_current_carriers(source_root, repository)
    )
