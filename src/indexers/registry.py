"""Indexer registration."""

from typing import cast

from meilisearch import Client

from src.exceptions import IndexerRegistryEntryError, IndexRegistrationError
from src.models import ConfigModel
from src.models.indexers import (
    BaseIndexerConfigModel,
    IndexerRegistryEntry,
    RegisteredIndexerRegistryEntry,
)

from . import sms

INDEXER_MODULES = [
    sms,
]


class IndexerRegistry:
    """Registry for indexer classes."""

    def __init__(
        self,
        config: ConfigModel,
        meilisearch_client: Client,
    ) -> None:
        """Initialize class."""
        self._config = config
        self.all_indexer_entries: dict[str, IndexerRegistryEntry] = {}
        self.indices: dict[str, IndexerRegistryEntry] = {}
        self.registered_indexers: dict[str, RegisteredIndexerRegistryEntry] = {}
        self.registered_indicies: dict[str, RegisteredIndexerRegistryEntry] = {}
        self._client = meilisearch_client

    def register_indices(self) -> None:
        """Register indices."""
        for module in INDEXER_MODULES:
            entry = getattr(module, "REGISTRY_ENTRY", None)

            if not entry:
                msg = f"No indexer entry found for module at {module.__path__}"
                raise IndexerRegistryEntryError(msg)
            if not isinstance(entry, IndexerRegistryEntry):
                msg = f"Expected indexer entry to be an IndexerRegistryEntry, received {type(entry)}."
                raise IndexerRegistryEntryError(msg)

            entry = cast("IndexerRegistryEntry", entry)
            indexer_type = entry.indexer_type

            if indexer_type in self.all_indexer_entries:
                msg = f"Indexer type {indexer_type} is already registered"
                raise IndexerRegistryEntryError(msg)

            indices = entry.indices

            for index in indices:
                if index in self.indices:
                    msg = f"Index {index} for entry {entry.indexer_name} is already defined elsewhere."
                    raise IndexerRegistryEntryError(msg)
                self.indices[index] = entry
            self.all_indexer_entries[entry.indexer_type] = entry

    def setup_all_indexers(self) -> None:
        """Setup all indexers in config."""
        indexers = self._config.indices
        for indexer in indexers:
            self.setup_indexer(indexer)

    def setup_indexer(self, entry: BaseIndexerConfigModel) -> RegisteredIndexerRegistryEntry:
        """Setup a single indexer."""
        indexer = self._get_unregistered_indexer_for_index(entry.type)
        if not indexer:
            msg = f"Could not find indexer for {entry.type}!"
            raise IndexRegistrationError(msg)
        indexer_type = indexer.indexer_type
        if indexer_type in self.registered_indexers:
            msg = f"Indexer type {indexer_type} is already set up."
            raise IndexRegistrationError(msg)

        index_already_registered = any(index in self.registered_indicies for index in indexer.indices)
        if index_already_registered:
            msg = (
                f"{indexer.indexer_name} uses one or more indices "
                f"which are already registered (Got {', '.join(indexer.indices)})."
            )
            raise IndexerRegistryEntryError(msg)

        cls = indexer.indexer_class
        instance = cls(config=entry, meilisearch_client=self._client)

        dumped = indexer.model_dump()
        dumped["instance"] = instance
        model = RegisteredIndexerRegistryEntry.model_validate(dumped)

        self.registered_indexers[entry.type] = model
        for index in indexer.indices:
            self.registered_indicies[index] = model
        return model

    def _get_unregistered_indexer_for_index(self, indexer_type: str) -> IndexerRegistryEntry | None:
        """Get the unregistered indexer entry for a given indexer type."""
        return self.all_indexer_entries.get(indexer_type)

    def get_indexer_for_index(self, index: str) -> RegisteredIndexerRegistryEntry | None:
        """Get the registered indexer entry for a given index."""
        return self.registered_indicies.get(index)

    def get_indexer_by_type(self, indexer_type: str) -> RegisteredIndexerRegistryEntry | None:
        """Get the registered indexer entry for a given indexer type."""
        return self.registered_indexers.get(indexer_type)
