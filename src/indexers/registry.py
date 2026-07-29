"""Indexer registration."""

from typing import cast

from src.exceptions import IndexerRegistryEntryError
from src.models import ConfigModel
from src.models.indices import IndexerRegistryEntry

from . import sms

INDEXER_MODULES = [
    sms,
]


class IndexerRegistry:
    """Registry for indexer classes."""

    def __init__(self, config: ConfigModel) -> None:
        """Initialize class."""
        self._config = config
        self.indexer_entries: dict[str, IndexerRegistryEntry] = {}
        self.indices: dict[str, IndexerRegistryEntry] = {}

    def register_indices(self) -> None:
        """Register indices."""
        for module in INDEXER_MODULES:
            entry = getattr(module, "REGISTRY_ENTRY", None)

            if not entry:
                msg = f"No indexer entry found for module at {module.__path__}"
                raise IndexerRegistryEntryError(msg)
            if not isinstance(entry, IndexerRegistryEntry):
                msg = (
                    f"Expected indexer entry to be an IndexerRegistryEntry, received {type(entry)}."
                )
                raise IndexerRegistryEntryError(msg)

            entry = cast("IndexerRegistryEntry", entry)
            indexer_type = entry.indexer_type

            if indexer_type in self.indexer_entries:
                msg = f"Indexer type {indexer_type} is already registered"
                raise IndexerRegistryEntryError(msg)

            indexers = entry.indices

            for indexer in indexers:
                if indexer in self.indices:
                    msg = f"Indexer {indexer} for entry {entry.indexer_name} is already defined elsewhere."
                    raise IndexerRegistryEntryError(msg)
                self.indices[indexer] = entry
            self.indexer_entries[entry.indexer_type]
