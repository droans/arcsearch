"""ArcSearch Models."""

from pathlib import Path

from pydantic import BaseModel


class BaseRuntimeData(BaseModel):
    """Base model for runtime data."""


class RuntimeData(BaseModel):
    """Runtime data model, passed to indexers."""

    data_directory: Path
