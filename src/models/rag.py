"""Models for RAG components."""

from pydantic import BaseModel, HttpUrl, SecretStr


class EmbedderSettings(BaseModel):
    """Model for the embedder config."""

    model_name: str
    url: HttpUrl
    api_key: str | None = None
    dimensions: int

    # See https://www.meilisearch.com/docs/capabilities/hybrid_search/how_to/configure_rest_embedder
    request: dict
    response: dict
    document_template: str | None = None


class MeilisearchConfig(BaseModel):
    """Model for Meilisearch config."""

    url: HttpUrl
    api_key: SecretStr | None = None
