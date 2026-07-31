"""Text Message Parsers."""

from pathlib import Path

from src.models.indexers import AddDocumentsKwargField, IndexerRegistryEntry
from src.util.indexers import load_index_manifest

from .contacts import export_contacts, parse_contacts
from .conversations import ExportSMSConversations
from .messages import ExportSMSMessages, generate_conversation_id, generate_message_unique_id
from .models import SMSConfig
from .sms import TextMessageIndexer


def register_indexer() -> IndexerRegistryEntry:
    """Register index."""
    manifest = load_index_manifest("manifest.yaml")

    add_documents_kwargs = {
        "messages_xml_path": AddDocumentsKwargField(
            type=str | Path,
            example_value="sms-20210101123456.xml",
            validate_func=lambda path: Path(path).exists(),
        ),
    }

    return IndexerRegistryEntry(
        manifest=manifest,
        indexer_class=TextMessageIndexer,
        add_documents_kwargs=add_documents_kwargs,
        config_schema=SMSConfig,
    )


__all__ = (
    "ExportSMSConversations",
    "ExportSMSMessages",
    "export_contacts",
    "generate_conversation_id",
    "generate_message_unique_id",
    "parse_contacts",
)
