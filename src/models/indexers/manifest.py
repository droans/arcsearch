"""Model for indexer manifest."""

from pydantic import BaseModel

from src.models.indices import IndexConfig


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
    supports_adding_documents: bool = True
    supports_creating_indices: bool = True
    supports_embedding: bool = True


class IndexerManifest(BaseModel):
    """Model for the indexer manifest file."""

    indexer: IndexerManifestIndexerConfig
    indices: list[IndexConfig]
