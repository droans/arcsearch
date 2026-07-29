"""Text Message Parsers."""

from pathlib import Path

from src.models.indices import AddDocumentsKwargField, IndexerRegistryEntry

from .contacts import export_contacts, parse_contacts
from .conversations import ExportSMSConversations
from .messages import ExportSMSMessages, generate_conversation_id, generate_message_unique_id
from .models import SMSConfig
from .sms import TextMessageIndexer

INDEXER_CONFIG = SMSConfig

ADD_DOCUMENTS_KWARGS = {
    "messages_xml_path": AddDocumentsKwargField(
        type=str | Path,
        example_value="sms-20210101123456.xml",
        validate_func=lambda path: Path(path).exists(),
    ),
}

REGISTRY_ENTRY = IndexerRegistryEntry(
    indexer_name="SMS",
    indexer_type="sms",
    indexer_class=TextMessageIndexer,
    add_documents_kwargs=ADD_DOCUMENTS_KWARGS,
    indices=[
        "sms",
        "sms_conversations",
    ],
)

__all__ = (
    "INDEXER_CONFIG",
    "REGISTRY_ENTRY",
    "ExportSMSConversations",
    "ExportSMSMessages",
    "export_contacts",
    "export_conversations",
    "generate_conversation_id",
    "generate_message_unique_id",
    "parse_contacts",
)
