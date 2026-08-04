"""Config Models."""

from pydantic import BaseModel

from src.models.indexers import BaseIndexerConfigModel
from src.models.rag import MeilisearchConfig


class APIConfig(BaseModel):
    """ArcSearch API Config."""

    host: str = "127.0.0.1"
    port: int = 8000
    allowed_origins: list[str] = ["*"]


class ConfigModel(BaseModel):
    """ArcSearch configuration model."""

    api: APIConfig
    meilisearch: MeilisearchConfig
    indexers: list[BaseIndexerConfigModel]
