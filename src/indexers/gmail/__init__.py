"""Email indexer functions."""

from src.const import IndexEmbedderSetupStatus, IndexerRegistrationStatus
from src.core.registry.indexer import IndexerRegistry
from src.indexers.gmail.const import INDEX_EMAILS
from src.indexers.gmail.models import GMailConfig
from src.indexers.sms.sms import TextMessageIndexer
from src.models.arcsearch import AppModel, RuntimeData, SetupIndexerEntry


def setup_indexer(
    app: AppModel,
    runtime_data: RuntimeData,
    indexer_registry: IndexerRegistry,
) -> SetupIndexerEntry:
    """Register the indexer."""
    indexer = TextMessageIndexer(
        app=app,
        runtime_data=runtime_data,
    )
    indices = runtime_data.manifest.indices
    config = runtime_data.config
    assert isinstance(config, GMailConfig)
    indexer_domain = config.type
    for index in indices:
        if index.index_uid == INDEX_EMAILS:
            embedder_conf = index.embedder
            assert embedder_conf is not None
            if not config.embedder.document_template:
                config.embedder.document_template = embedder_conf.default_document_template
            embed_status = indexer_registry.setup_index_embedder(
                indexer_domain=indexer_domain,
                index_uid=INDEX_EMAILS,
                embedder_config=config.embedder,
                force_setup=True,
            )
            if embed_status not in (IndexEmbedderSetupStatus.OK, IndexEmbedderSetupStatus.ALREADY_SETUP):
                return SetupIndexerEntry(status=IndexerRegistrationStatus.SETUP_ERROR)

        indexer_registry.setup_index(indexer_domain=indexer_domain, index_config=index)
    return SetupIndexerEntry(status=IndexerRegistrationStatus.LOADED, instance=indexer)
