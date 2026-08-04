"""Text Message Parsers."""

from src.const import IndexEmbedderSetupStatus, IndexerRegistrationStatus
from src.core.registry.indexer import IndexerRegistry
from src.indexers.sms.const import INDEX_SMS
from src.models.arcsearch import AppModel, RuntimeData, SetupIndexerEntry

from .contacts import export_contacts, parse_contacts
from .conversations import ExportSMSConversations
from .messages import ExportSMSMessages, generate_conversation_id, generate_message_unique_id
from .models import SMSConfig
from .sms import TextMessageIndexer


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
    assert isinstance(config, SMSConfig)
    indexer_domain = config.type
    for index in indices:
        if index.index_uid == INDEX_SMS:
            embedder_conf = index.embedder
            assert embedder_conf is not None
            if not config.embedder.document_template:
                config.embedder.document_template = embedder_conf.default_document_template
            embed_status = indexer_registry.setup_index_embedder(
                indexer_domain=indexer_domain,
                index_uid=INDEX_SMS,
                embedder_config=config.embedder,
                force_setup=True,
            )
            if embed_status not in (IndexEmbedderSetupStatus.OK, IndexEmbedderSetupStatus.ALREADY_SETUP):
                return SetupIndexerEntry(status=IndexerRegistrationStatus.SETUP_ERROR)

        indexer_registry.setup_index(indexer_domain=indexer_domain, index_config=index)
    return SetupIndexerEntry(status=IndexerRegistrationStatus.LOADED, instance=indexer)


__all__ = (
    "ExportSMSConversations",
    "ExportSMSMessages",
    "export_contacts",
    "generate_conversation_id",
    "generate_message_unique_id",
    "parse_contacts",
)
