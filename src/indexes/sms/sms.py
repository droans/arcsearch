"""SMS Management."""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.indexes.sms import export_contacts, export_messages_and_conversations
from src.indexes.sms.const import (
    ATTACHMENT_DIR,
    INDEX_CONTACTS,
    INDEX_CONVERSATIONS,
    INDEX_SMS,
    TMP_CONTACTS_PATH,
    TMP_CONVERSATIONS_PATH,
    TMP_MESSAGES_PATH,
)
from src.models import ConfigModel

if TYPE_CHECKING:
    from meilisearch import Client


class TextMessageEngine:
    """Engine managing interactions with the sms index and data."""

    def __init__(self, config: ConfigModel, meilisearch_client: "Client") -> None:
        """Initialize class."""
        self._config = config
        self._meilisearch_client = meilisearch_client

    def create_indices(self) -> None:
        """Create Meilisearch indices."""
        self._meilisearch_client.create_index(INDEX_SMS, {"primaryKey": "timestamp"})
        self._meilisearch_client.create_index(INDEX_CONTACTS, {"primaryKey": "phone_number"})
        self._meilisearch_client.create_index(
            INDEX_CONVERSATIONS,
            {"primaryKey": "conversation_id"},
        )

        self._meilisearch_client.update_experimental_features({"foreignKeys": True})

        sms_idx = self._meilisearch_client.index(INDEX_SMS)
        contacts_idx = self._meilisearch_client.index(INDEX_CONTACTS)
        conversations_idx = self._meilisearch_client.index(INDEX_CONVERSATIONS)

        # Add filterable attributes
        sms_idx.update_filterable_attributes(["sender", "conversation_id", "timestamp", "type"])
        contacts_idx.update_filterable_attributes(["name", "phone_number"])
        conversations_idx.update_filterable_attributes(["recipients", "conversation_id"])
        # Add searchable attributes

        # Setup foreign keys
        sms_fk_settings = {
            "foreignKeys": [
                {
                    "fieldName": "conversation_id",
                    "foreignIndexUid": "conversations",
                },
            ],
        }
        conv_fk_settings = {
            "foreignKeys": [
                {
                    "fieldName": "recipients",
                    "foreignIndexUid": "contacts",
                },
            ],
        }
        sms_idx.update_settings(sms_fk_settings)
        conversations_idx.update_settings(conv_fk_settings)

    def setup_embedder(self) -> None:
        """Setup embedder for sms index."""
        embed_config = self._config.text_messages.embedder
        embed_settings = {
            embed_config.model_name: {
                "source": "rest",
                "url": embed_config.url,
                "apiKey": embed_config.api_key,
                "dimensions": embed_config.dimensions,
                "request": embed_config.request,
                "response": embed_config.response,
                "documentTemplate": embed_config.document_template,
            },
        }
        self._meilisearch_client.index(INDEX_SMS).update_embedders(embed_settings)

    def import_messages(self, message_file: str | Path) -> None:
        """Import messages into ArcSearch."""
        sms_config = self._config.text_messages
        export_messages_and_conversations(
            messages_xml_path=message_file,
            messages_save_path=TMP_MESSAGES_PATH,
            conversations_save_path=TMP_CONVERSATIONS_PATH,
            attachment_save_dir=ATTACHMENT_DIR,
            personal_phone_number=sms_config.personal_phone_numer,
            process_content_types=sms_config.save_attachment_types,
            process_content_type_prefixes=sms_config.save_attachment_type_prefixes,
        )
        with open(TMP_MESSAGES_PATH) as f:
            msg_data = json.loads(f.read())

        with open(TMP_CONVERSATIONS_PATH) as f:
            conv_data = json.loads(f.read())

        self._meilisearch_client.index(INDEX_SMS).add_documents(msg_data)
        self._meilisearch_client.index(INDEX_CONVERSATIONS).add_documents(conv_data)

    def import_contacts(self, contacts_file: str | Path) -> None:
        """Import contacts into ArcSearch."""
        export_contacts(
            vcard_path=contacts_file,
            export_path=TMP_CONTACTS_PATH,
        )
        with open(TMP_CONTACTS_PATH) as f:
            contacts_data = json.loads(f.read())

        self._meilisearch_client.index(INDEX_CONTACTS).add_documents(contacts_data)
