"""Models for index configuration."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Type  # noqa: UP035

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


class AddDocumentsKwargField(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Model for a single `kwarg` field."""

    # Type for argument
    type: type[...]

    # Default value to use
    default_value: Any = None

    # Example value to display
    example_value: Any = None

    # If True, the default value will always be used and the user will be unable to set it themselves.
    locked: bool = False

    # Validator needs to accept any type as the first argument and
    # return a True/False if argument is valid
    validate_func: Callable[[Any], bool] | None = None


class IndexRegistryEntry(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Model for registering an index and its class."""

    # Name used for index
    index_name: str

    # Key identifying index type
    index_type: str

    # Class used to manage index
    index_class: Type[BaseIndexClass]  # noqa: UP006

    # Arguments to pass when adding documents
    add_documents_kwargs: dict[str, AddDocumentsKwargField] = {}

    # Whether the index supports adding documents
    supports_adding_documents: bool = True

    # Whether the index supports creating indices
    supports_creating_indices: bool = True

    # Whether the index supports embedding
    supports_embedding: bool = True

    # Names for indices created by entry
    indices: list[str]
