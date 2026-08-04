"""SMS Management."""

import json
from pathlib import Path

from src.models.arcsearch import AppModel, RuntimeData
from src.models.indexers import BaseIndexerClass
from src.util.meilisearch import update_index_embedder_config

from .const import (
    ATTACHMENT_DIR,
    INDEX_CONTACTS,
    INDEX_CONVERSATIONS,
    INDEX_SMS,
    TMP_CONTACTS_PATH,
    TMP_CONVERSATIONS_PATH,
    TMP_MESSAGES_PATH,
)
from .contacts import export_contacts
from .messages import ExportSMSMessages
from .models import SMSConfig


class TextMessageIndexer(BaseIndexerClass):
    """Indexer managing interactions with the sms index and data."""

    def __init__(
        self,
        app: AppModel,
        runtime_data: RuntimeData,
    ) -> None:
        """Initialize class."""
        self.app = app
        self.runtime_data = runtime_data

    def setup_embedder(self, **kwargs) -> None:  # noqa: ARG002
        """Setup embedder for sms index."""
        assert isinstance(self.runtime_data.config, SMSConfig)
        embed_config = self.runtime_data.config.embedder
        if embed_config.document_template is None:
            indices = self.runtime_data.manifest.indices
            email_conf = next(index for index in indices if index.index_uid == INDEX_SMS)
            assert email_conf.embedder
            document_template = email_conf.embedder.default_document_template
            embed_config.document_template = document_template

            update_index_embedder_config(
                idx=self.app.meilisearch_client.index(INDEX_SMS),
                embedder_config=embed_config,
            )

    def import_messages(
        self,
        message_file: str | Path,
        messages_save_path: str | Path = TMP_MESSAGES_PATH,
        conversations_save_path: str | Path = TMP_CONVERSATIONS_PATH,
        attachments_save_path: str | Path = ATTACHMENT_DIR,
    ) -> None:
        """Import messages into ArcSearch."""
        assert isinstance(self.runtime_data.config, SMSConfig)
        exporter = ExportSMSMessages(self.runtime_data.config)
        exporter.export_messages_and_conversations(
            messages_xml_path=message_file,
            messages_save_path=messages_save_path,
            conversations_save_path=conversations_save_path,
            attachment_save_dir=attachments_save_path,
        )
        with open(messages_save_path) as f:
            msg_data = json.loads(f.read())

        with open(conversations_save_path) as f:
            conv_data = json.loads(f.read())

        self.app.meilisearch_client.index(INDEX_SMS).add_documents(msg_data)
        self.app.meilisearch_client.index(INDEX_CONVERSATIONS).add_documents(conv_data)

    def import_contacts(self, contacts_file: str | Path) -> None:
        """Import contacts into ArcSearch."""
        export_contacts(
            vcard_path=contacts_file,
            export_path=TMP_CONTACTS_PATH,
        )
        with open(TMP_CONTACTS_PATH) as f:
            contacts_data = json.loads(f.read())

        self.app.meilisearch_client.index(INDEX_CONTACTS).add_documents(contacts_data)

    def add_documents(
        self,
        **kwargs,
    ) -> None:
        """Class implementation."""
        messages_xml_path = kwargs.get("messages_xml_path")
        assert isinstance(messages_xml_path, str)
        self.import_messages(messages_xml_path)
