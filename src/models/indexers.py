"""Models for indexer configuration."""

from abc import ABC, abstractmethod
from types import UnionType
from typing import TYPE_CHECKING, Any, Callable, Type  # noqa: UP035

from pydantic import BaseModel

from src.const import DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES, DEFAULT_PROCESS_CONTENT_TYPES
from src.models.arcsearch import RuntimeData

from .rag import EmbedderSettings

if TYPE_CHECKING:
    from meilisearch import Client


class BaseIndexerConfigModel(BaseModel):
    """Base Model for indexer configuration."""

    type: str


class BaseMessageWithAttachmentConfig(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Base model for indices with messages and attachments."""

    embedder: EmbedderSettings
    save_attachment_types: list[str] = DEFAULT_PROCESS_CONTENT_TYPES
    save_attachment_type_prefixes: list[str] = DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES


class BaseIndexerClass(ABC):
    """Base indexer class."""

    @abstractmethod
    def __init__(
        self,
        runtime_data: RuntimeData,
        config: BaseIndexerConfigModel,
        meilisearch_client: "Client",
    ) -> None:
        """Initialize class."""

    @abstractmethod
    def add_documents(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Add documents to index."""
        ...

    @abstractmethod
    def create_index(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Create index in client."""
        ...

    @abstractmethod
    def setup_embedder(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Function implemented by children."""
        ...


class AddDocumentsKwargField(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Model for a single `kwarg` field."""

    # Type for argument
    type: UnionType | type

    # Default value to use
    default_value: Any = None

    # Example value to display
    example_value: Any = None

    # If True, the default value will always be used and
    #  the user will be unable to set it themselves.
    locked: bool = False

    # Validator needs to accept any type as the first argument and
    # return a True/False if argument is valid
    validate_func: Callable[[Any], bool] | None = None


class IndexerRegistryEntry(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Model for registering an indexer and its class."""

    # Name used for indexer
    indexer_name: str

    # Key identifying indexer type
    indexer_type: str

    # Class used to manage indexer
    indexer_class: Type[BaseIndexerClass]  # noqa: UP006

    # Arguments to pass when adding documents
    add_documents_kwargs: dict[str, AddDocumentsKwargField] = {}

    # Whether the indexer supports adding documents
    supports_adding_documents: bool = True

    # Whether the indexer supports creating indices
    supports_creating_indices: bool = True

    # Whether the indexer supports embedding
    supports_embedding: bool = True

    # Names for indices created by entry
    indices: list[str]


class RegisteredIndexerRegistryEntry(
    IndexerRegistryEntry,
    arbitrary_types_allowed=True,
):
    """Model for a registered indexer."""

    instance: object
