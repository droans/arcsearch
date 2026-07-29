"""Models for index configuration."""

from pydantic import BaseModel

from src.const import DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES, DEFAULT_PROCESS_CONTENT_TYPES
from src.models.rag import EmbedderSettings


class BaseIndexConfigModel(BaseModel):
    """Base Model for index configuration."""

    type: str


class BaseMessageWithAttachmentConfig(
    BaseIndexConfigModel,
    arbitrary_types_allowed=True,
):
    """Base model for indices with messages and attachments."""

    embedder: EmbedderSettings
    save_attachment_types: list[str] = DEFAULT_PROCESS_CONTENT_TYPES
    save_attachment_type_prefixes: list[str] = DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES
