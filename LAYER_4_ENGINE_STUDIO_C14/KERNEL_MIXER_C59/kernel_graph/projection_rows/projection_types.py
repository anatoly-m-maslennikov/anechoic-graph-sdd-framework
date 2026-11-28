"""Typed snapshots and change counts for public projections."""

from typing import Annotated, Any
from pydantic import ConfigDict, InstanceOf
from pydantic.dataclasses import dataclass
from ...graph_store import GraphState
from ...content_schema import ContentSchema
from ...header_columns import HeaderSchema


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class ProjectionSnapshot:
    atoms: Annotated[dict[tuple[str, str], dict[str, Any]], InstanceOf()]
    scopes: Annotated[dict[str, dict[str, Any]], InstanceOf()]
    graph: GraphState
    header_schema: HeaderSchema
    content_schema: ContentSchema
    atom_sources: Annotated[
        dict[tuple[str, str], dict[str, Any]], InstanceOf()
    ]


@dataclass(config=ConfigDict(strict=True, extra="forbid"), frozen=True)
class ProjectionChange:
    deleted_atoms: int
    deleted_scopes: int
    inserted_atoms: int
    inserted_scopes: int
    graph_rows: int
    reference: str | None
