"""Index registration."""

from typing import cast

from src.exceptions import IndexRegistryEntryError
from src.models import ConfigModel
from src.models.indices import IndexRegistryEntry

from . import sms

INDEX_MODULES = [
    sms,
]


class IndexRegistry:
    """Registry for index classes."""

    def __init__(self, config: ConfigModel) -> None:
        """Initialize class."""
        self._config = config
        self.index_entries: dict[str, IndexRegistryEntry] = {}
        self.indices: dict[str, IndexRegistryEntry] = {}

    def register_indices(self) -> None:
        """Register indices."""
        for module in INDEX_MODULES:
            entry = getattr(module, "REGISTRY_ENTRY", None)

            if not entry:
                msg = f"No index entry found for module at {module.__path__}"
                raise IndexRegistryEntryError(msg)
            if not isinstance(entry, IndexRegistryEntry):
                msg = f"Expected index entry to be an IndexRegistryEntry, received {type(entry)}."
                raise IndexRegistryEntryError(msg)

            entry = cast("IndexRegistryEntry", entry)
            index_type = entry.index_type

            if index_type in self.index_entries:
                msg = f"Index type {index_type} is already registered"
                raise IndexRegistryEntryError(msg)

            indices = entry.indices

            for index in indices:
                if index in self.indices:
                    msg = (
                        f"Index {index} for entry {entry.index_name} is already defined elsewhere."
                    )
                    raise IndexRegistryEntryError(msg)
                self.indices[index] = entry
            self.index_entries[entry.index_type]
