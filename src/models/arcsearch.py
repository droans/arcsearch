"""ArcSearch models."""

from pathlib import Path
from types import UnionType
from typing import Any, Callable, Type  # noqa: UP035

from pydantic import BaseModel

from src.models.indexers import BaseIndexerClass, IndexerManifest


class BaseRuntimeData(BaseModel):
    """Base model for runtime data."""


class RuntimeData(BaseModel):
    """Runtime data model, passed to indexers."""

    data_directory: Path
    manifest: IndexerManifest


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
