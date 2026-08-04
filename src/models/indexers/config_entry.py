"""User config entry for an indexer."""

from pydantic import BaseModel


class BaseIndexerConfigModel(BaseModel):
    """Base Model for indexer configuration."""

    type: str
