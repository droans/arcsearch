"""Config Models."""

from googleapiclient.model import BaseModel

from src.models.indices import BaseIndexerConfigModel
from src.models.rag import MeilisearchConfig


class ConfigModel(BaseModel):
    """ArcSearch configuration model."""

    meilisearch: MeilisearchConfig
    indices: list[BaseIndexerConfigModel]
