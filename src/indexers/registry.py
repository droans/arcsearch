"""Indexer registration."""

from pathlib import Path

from meilisearch import Client

from src.exceptions import IndexerRegistryEntryError, IndexRegistrationError
from src.models import ConfigModel
from src.models.arcsearch import BaseRuntimeData, RuntimeData
from src.models.indexers import (
    BaseIndexerConfigModel,
    IndexerRegistryEntry,
    RegisteredIndexerRegistryEntry,
)
from src.util.meilisearch import create_index, index_exists

from . import gmail, sms

INDEXER_MODULES = [
    sms,
    gmail,
]

BASE_DATA_DIR = Path("data")


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
        self.user_indexers: dict[str, RegisteredIndexerRegistryEntry] = {}
        self.user_indicies: dict[str, RegisteredIndexerRegistryEntry] = {}
        self._client = meilisearch_client
        self._base_runtime_data = BaseRuntimeData()

    def register_indices(self) -> None:
        """Register indices."""
        for module in INDEXER_MODULES:
            register_func = getattr(module, "register_indexer", None)

            if not register_func:
                msg = f"No indexer entry found for module at {module.__path__}"
                raise IndexerRegistryEntryError(msg)
            entry = register_func()
            if not isinstance(entry, IndexerRegistryEntry):
                msg = f"Expected indexer entry to be an IndexerRegistryEntry, received {type(entry)}."
                raise IndexerRegistryEntryError(msg)

            indexer_type = entry.manifest.indexer.type

            if indexer_type in self.all_indexer_entries:
                msg = f"Indexer type {indexer_type} is already registered"
                raise IndexerRegistryEntryError(msg)

            indices = entry.manifest.indices

            for index in indices:
                if index in self.indices:
                    msg = f"Index {index} for entry {entry.manifest.indexer.name} is already defined elsewhere."
                    raise IndexerRegistryEntryError(msg)
                self.indices[index.index_uid] = entry
            self.all_indexer_entries[entry.manifest.indexer.type] = entry

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
        manifest = indexer.manifest
        indexer_type = manifest.indexer.type
        if indexer_type in self.user_indexers:
            msg = f"Indexer type {indexer_type} is already set up."
            raise IndexRegistrationError(msg)

        index_already_setup = any(index in self.user_indicies for index in manifest.indices)
        if index_already_setup:
            indices = [index.index_uid for index in manifest.indices]
            msg = (
                f"{manifest.indexer.name} uses one or more index names "
                f"which are already set up (Got {', '.join(indices)})."
            )
            raise IndexerRegistryEntryError(msg)

        cls = indexer.indexer_class
        base_runtime_data = self._base_runtime_data.model_dump()
        base_runtime_data["data_directory"] = BASE_DATA_DIR.joinpath(indexer_type)
        runtime_data = RuntimeData.model_validate(base_runtime_data)
        instance = cls(runtime_data=runtime_data, config=entry, meilisearch_client=self._client)

        dumped = indexer.model_dump()
        dumped["instance"] = instance
        model = RegisteredIndexerRegistryEntry.model_validate(dumped)

        self.user_indexers[entry.type] = model
        for index in indexer.manifest.indices:
            self.user_indicies[index.index_uid] = model
            if not index_exists(client=self._client, index_uid=index.index_uid):
                create_index(client=self._client, index_config=index)
        return model

    def _get_unregistered_indexer_for_index(self, indexer_type: str) -> IndexerRegistryEntry | None:
        """Get the unregistered indexer entry for a given indexer type."""
        return self.all_indexer_entries.get(indexer_type)

    def get_indexer_for_index(self, index: str) -> RegisteredIndexerRegistryEntry | None:
        """Get the set up indexer entry for a given index."""
        return self.user_indicies.get(index)

    def get_indexer_by_type(self, indexer_type: str) -> RegisteredIndexerRegistryEntry | None:
        """Get the set up indexer entry for a given indexer type."""
        return self.user_indexers.get(indexer_type)
