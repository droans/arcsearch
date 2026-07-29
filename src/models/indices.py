"""Models for index configuration."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

from src.const import DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES, DEFAULT_PROCESS_CONTENT_TYPES
from src.models.rag import EmbedderSettings

if TYPE_CHECKING:
    from meilisearch import Client


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


class BaseIndexClass(ABC):
    """Base index class."""

    @abstractmethod
    def __init__(
        self,
        config: BaseIndexConfigModel,
        meilisearch_client: "Client",
    ) -> None:
        """Initialize class."""

    @abstractmethod
    def add_documents(self, **kwargs) -> None:
        """Add documents to index."""

    @abstractmethod
    def create_index(self, **kwargs) -> None:
        """Create index in client."""

    @abstractmethod
    def setup_embedder(self, **kwargs) -> None:
        """Function implemented by children."""
