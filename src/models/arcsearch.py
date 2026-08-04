"""ArcSearch models."""

from collections.abc import Callable
from pathlib import Path
from types import UnionType
from typing import Any

from fastapi import FastAPI
from meilisearch import Client
from pydantic import BaseModel

from src.const import IndexerRegistrationStatus
from src.models import ConfigModel
from src.models.indexers import BaseIndexerConfigModel, IndexerManifest


class BaseRuntimeData(BaseModel):
    """Base model for runtime data."""


class AppModel(BaseModel, arbitrary_types_allowed=True):
    """Model for the app."""

    fastapi_app: FastAPI
    config: ConfigModel
    meilisearch_client: Client


class RuntimeData(BaseModel):
    """Runtime data model, passed to indexers."""

    data_directory: Path
    manifest: IndexerManifest
    config: BaseIndexerConfigModel | None = None


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


class SetupIndexerEntry(BaseModel):
    """Entry for a setup indexer, retrieved from running module.setup_indexer."""

    status: IndexerRegistrationStatus
    instance: object | None = None


class IndexFileModel(BaseModel):
    """Model representing a single index file."""

    file_name: str
    content_type: str
    src: str
