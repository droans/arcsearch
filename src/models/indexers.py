"""Models for indexer configuration."""

from abc import ABC, abstractmethod
from types import UnionType
from typing import TYPE_CHECKING, Any, Callable, Type  # noqa: UP035

from pydantic import BaseModel

from src.const import DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES, DEFAULT_PROCESS_CONTENT_TYPES
from src.models.arcsearch import RuntimeData

from .indices.index import IndexConfig
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

    description: str | None = None

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


class IndexerManifestIndexerConfig(BaseModel):
    """Model for indexer section of indexer config."""

    # Name of indexer
    name: str
    # Description of indexer
    description: str

    # Unique type for indexer, used when defining in user configs
    type: str

    # Support options
    supports_adding_documents: bool = True
    supports_creating_indices: bool = True
    supports_embedding: bool = True


class IndexerManifest(BaseModel):
    """Model for the indexer manifest file."""

    indexer: IndexerManifestIndexerConfig
    indices: list[IndexConfig]


class IndexerRegistryEntry(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Model for registering an indexer and its class."""

    manifest: IndexerManifest
    # Class used to manage indexer
    indexer_class: Type[BaseIndexerClass]  # noqa: UP006

    # Arguments to pass when adding documents
    add_documents_kwargs: dict[str, AddDocumentsKwargField] = {}

    # Configuration schema for users setting up the indexer
    config_schema: type[BaseModel]


class RegisteredIndexerRegistryEntry(
    IndexerRegistryEntry,
    arbitrary_types_allowed=True,
):
    """Model for a registered indexer."""

    instance: object
