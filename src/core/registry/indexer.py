"""Indexer registry."""

import importlib
from pathlib import Path

from src.const import IndexEmbedderSetupStatus, IndexerRegistrationStatus, IndexSetupStatus
from src.core.util.indexer import compare_embedder_settings, get_configs_for_index_embedders
from src.exceptions import IndexRegistrationError
from src.indexers import get_all_manifests
from src.models.arcsearch import AppModel, BaseRuntimeData, RuntimeData, SetupIndexerEntry
from src.models.indexers import BaseIndexerConfigModel
from src.models.indexers.manifest import RegisteredManifest
from src.models.indices import IndexConfig
from src.models.rag import EmbedderSettings
from src.util.meilisearch import create_index, index_exists, update_index_embedder_config

BASE_DATA_DIR = Path("data")


class IndexerRegistry:
    """Class for indexer registry."""

    def __init__(
        self,
        app: AppModel,
    ) -> None:
        """Initialie class."""
        self._app = app
        self._manifests: dict[str, RegisteredManifest] = {}
        self._indexers: dict[str, SetupIndexerEntry] = {}
        self._base_runtime_data = BaseRuntimeData()

    def register_manifests(self) -> None:
        """Register all manifests."""
        manifests = get_all_manifests()
        for manifest in manifests:
            domain = manifest.indexer.domain
            assert (domain) not in self._manifests
            self._manifests[domain] = manifest

    def get_indexer_manifest(self, indexer_domain: str) -> RegisteredManifest | None:
        """Return the manifest for an indexer."""
        return self._manifests.get(indexer_domain)

    def setup_indexer(self, indexer_config: BaseIndexerConfigModel) -> None:
        """Setup an indexer."""
        # Grab manifest
        manifest = self.get_indexer_manifest(indexer_domain=indexer_config.type)
        assert manifest is not None
        manifest = manifest.model_copy()

        # Import module from module name
        module = importlib.import_module(manifest.module_name)

        # Create data directory
        data_dir = BASE_DATA_DIR.joinpath(manifest.indexer.domain)
        if not data_dir.exists():
            data_dir.mkdir()

        # Get indexer registration func
        register_func = module.register_indexer

        # Generate runtime data and call register function
        rtd = RuntimeData(
            data_directory=data_dir,
            manifest=manifest,
            config=indexer_config,
            **self._base_runtime_data.model_dump(),
        )
        entry: SetupIndexerEntry = register_func(app=self._app, runtime_data=rtd, indexer_registry=self)
        if entry.status != IndexerRegistrationStatus.LOADED:
            msg = f"Could not register {manifest.indexer.name}, received status: {entry.status}"
            raise IndexRegistrationError(msg)
        if entry.instance is None:
            msg = f"Attempted to register {manifest.indexer.name} but did not receive an instance."
            raise IndexRegistrationError(msg)

        # Add to setup indexers
        self._indexers[indexer_config.type] = entry

    def setup_index(self, indexer_domain: str, index_config: IndexConfig) -> IndexSetupStatus:
        """Setup an indexer. Returns a bool representing status."""
        if not index_config.index_uid.startswith(f"{indexer_domain}_"):
            return IndexSetupStatus.INVALID_INDEX_PREFIX_FOR_DOMAIN
        if index_exists(client=self._app.meilisearch_client, index_uid=index_config.index_uid):
            return IndexSetupStatus.ALREADY_EXISTS
        create_index(client=self._app.meilisearch_client, index_config=index_config)
        return IndexSetupStatus.OK

    def setup_index_embedder(
        self,
        indexer_domain: str,
        index_uid: str,
        embedder_config: EmbedderSettings,
        force_setup: bool = True,
    ) -> IndexEmbedderSetupStatus:
        """Setup an embedder."""
        if not index_uid.startswith(f"{indexer_domain}_"):
            return IndexEmbedderSetupStatus.INVALID_INDEX_PREFIX_FOR_DOMAIN
        existing_embed_confs = get_configs_for_index_embedders(client=self._app.meilisearch_client, index_uid=index_uid)
        if existing_embed_confs:
            for embed_conf in existing_embed_confs:
                if (
                    compare_embedder_settings(embedder_settings=embedder_config, compare_settings=embed_conf)
                    and not force_setup
                ):
                    return IndexEmbedderSetupStatus.ALREADY_SETUP
        index = self._app.meilisearch_client.index(index_uid)
        update_index_embedder_config(idx=index, embedder_config=embedder_config)
        return IndexEmbedderSetupStatus.OK

    def get_indexer(self, indexer_name: str) -> SetupIndexerEntry | None:
        """Retrieve an indexer."""
        return self._indexers.get(indexer_name)
