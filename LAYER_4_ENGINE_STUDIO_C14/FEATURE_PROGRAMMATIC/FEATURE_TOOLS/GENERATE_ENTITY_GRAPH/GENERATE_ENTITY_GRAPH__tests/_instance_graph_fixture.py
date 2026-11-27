"""Source fixture for current instance graph tests."""

from importlib import import_module

compose_current_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
).compose_current_graph


def source(atom_id: str = "CA-R-2002", version: int = 1) -> dict[str, object]:
    return {
        "atom_id": atom_id,
        "version": version,
        "path": f"sources/{atom_id}.md",
        "sha256": "a" * 64,
    }


def graph_for(subject: str) -> tuple[dict, dict]:
    return compose_current_graph(
        [
            {
                "source": source(),
                "subjects": {"governs": subject, "depends_on": []},
            }
        ]
    )
