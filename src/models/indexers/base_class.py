"""Base indexer class."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from . import BaseIndexerConfigModel

if TYPE_CHECKING:
    from meilisearch import Client

    from src.models.arcsearch import RuntimeData


class BaseIndexerClass(ABC):
    """Base indexer class."""

    @abstractmethod
    def __init__(
        self,
        runtime_data: "RuntimeData",
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
