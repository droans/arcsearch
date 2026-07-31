"""Index configuration models."""

from pydantic import BaseModel

from src.const import DEFAULT_STOP_WORDS
from src.models.indices.attributes import IndexAttributesConfig, IndexAttributesForeignKeyConfig
from src.models.indices.chat import IndexChatConfig


class IndexEmbedderConfig(BaseModel):
    """Config for index embedder."""

    default_document_template: str


class IndexConfig(BaseModel):
    """Model for an index."""

    index_uid: str
    primary_key: str
    embedder: IndexEmbedderConfig
    chat: IndexChatConfig
    foreign_keys: list[IndexAttributesForeignKeyConfig] | None = None
    attributes: IndexAttributesConfig
    stop_words: list[str] = DEFAULT_STOP_WORDS
