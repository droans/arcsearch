"""Model for indexer manifest."""

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel

from src.models.indices import IndexConfig


class IndexerFeature(StrEnum):
    """Supported indexer features."""

    ADD_DOCUMENTS = "add_documents"
    CREATE_INDICES = "create_indices"
    EMBEDDING = "embeddings"


class IndexerManifestIndexerConfig(BaseModel):
    """Model for indexer section of indexer config."""

    # Name of indexer
    name: str
    # Description of indexer
    description: str

    # Unique domain for indexer, used in user configs using the key `type`
    domain: str
    requirements: list[str] = []
    system_requirements: list[str] = []

    # Support options
    supported_features: list[IndexerFeature]


class IndexerManifest(BaseModel):
    """Model for the indexer manifest file."""

    indexer: IndexerManifestIndexerConfig
    indices: list[IndexConfig]
    module_path: Path
    module_name: str


class RegisteredManifest(IndexerManifest, arbitrary_types_allowed=True):
    """Model for a registered indexer manifest."""

    instance: object | None = None
