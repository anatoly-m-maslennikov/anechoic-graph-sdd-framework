"""Save one SQL record under its canonical UUID."""

from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict


class _SavedQueryRow(BaseModel):
    model_config = ConfigDict(
        strict=True, extra="forbid", hide_input_in_errors=True
    )

    saved_query_id: str
    kind: Literal["query", "view", "worksheet"]
    sql: str
    saved_at: str
    name: str | None = None


def _is_uuid7(value: str) -> bool:
    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return False
    return parsed.version == 7 and str(parsed) == value
