"""Models."""

from pydantic import BaseModel, HttpUrl

from src.indexes.sms.const import (
    DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES,
    DEFAULT_PROCESS_CONTENT_TYPES,
)


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


class SMSConfig(BaseModel):
    """Model for SMS configuration."""

    embedder: EmbedderSettings
    save_attachment_types: list[str] = DEFAULT_PROCESS_CONTENT_TYPES
    save_attachment_type_prefixes: list[str] = DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES
    personal_phone_numer: str


class MeilisearchConfig(BaseModel):
    """Model for Meilisearch config."""


class ConfigModel(BaseModel):
    """ArcSearch configuration model."""

    meilisearch: MeilisearchConfig
    text_messages: SMSConfig
