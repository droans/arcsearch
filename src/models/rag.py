"""Models for RAG components."""

from googleapiclient.model import BaseModel
from pydantic import HttpUrl


class EmbedderSettings(BaseModel):
    """Model for the embedder config."""

    model_name: str
    url: HttpUrl
    api_key: str | None = None
    dimensions: int

    # See https://www.meilisearch.com/docs/capabilities/hybrid_search/how_to/configure_rest_embedder
    request: dict
    response: dict
    document_template: str


class MeilisearchConfig(BaseModel):
    """Model for Meilisearch config."""
