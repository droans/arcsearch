"""Config Models."""

from pydantic import BaseModel

from src.models.indexers import BaseIndexerConfigModel
from src.models.rag import MeilisearchConfig


class ConfigModel(BaseModel):
    """ArcSearch configuration model."""

    meilisearch: MeilisearchConfig
    indices: list[BaseIndexerConfigModel]
