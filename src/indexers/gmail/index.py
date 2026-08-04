"""Manage indexing."""

from typing import TYPE_CHECKING

from src.indexers.gmail.const import INDEX_CONTACTS, INDEX_CONVERSATIONS, INDEX_EMAILS
from src.indexers.gmail.models import ConversationModel, EmailModel, GMailConfig, IndexedEmailContact
from src.models.arcsearch import AppModel, RuntimeData
from src.util.meilisearch import update_index_embedder_config

if TYPE_CHECKING:
    from meilisearch import Client


class GMailIndexer:
    """Class to manage the Meilisearch indexer."""

    def __init__(
        self,
        app: AppModel,
        runtime_data: RuntimeData,
        meilisearch_client: "Client",
    ) -> None:
        """Initialize class."""
        self.app = app
        self.runtime_data = runtime_data
        config = runtime_data.config
        assert isinstance(config, GMailConfig)
        self.config = config
        self.meilisearch_client = meilisearch_client

    def setup_embedder(self) -> None:
        """Setup embedder."""
        embed_config = self.config.embedder
        if embed_config.document_template is None:
            indices = self.runtime_data.manifest.indices
            email_conf = next(index for index in indices if index.index_uid == INDEX_EMAILS)
            embedder_conf = email_conf.embedder
            assert embedder_conf is not None
            document_template = embedder_conf.default_document_template
            embed_config.document_template = document_template

            update_index_embedder_config(
                idx=self.meilisearch_client.index(INDEX_EMAILS),
                embedder_config=embed_config,
            )

    def import_messages_to_meilisearch(self, account_name: str, messages: list[EmailModel]) -> None:
        """Import messages into Meilisearch."""
        for message in messages:
            message.account_name = account_name
        self.meilisearch_client.index(INDEX_EMAILS).add_documents(
            [message.model_dump() for message in messages],
        )

    def import_contacts_to_meilisearch(
        self,
        account_name: str,
        contacts: list[IndexedEmailContact],
    ) -> None:
        """Import contacts into Meilisearch."""
        for contact in contacts:
            contact.account_name = account_name
        self.meilisearch_client.index(INDEX_CONTACTS).add_documents(
            [contact.model_dump() for contact in contacts],
        )

    def import_conversations_to_meilisearch(
        self,
        account_name: str,
        conversations: list[ConversationModel],
    ) -> None:
        """Import conversations into Meilisearch."""
        for conversation in conversations:
            conversation.account_name = account_name
        self.meilisearch_client.index(INDEX_CONVERSATIONS).add_documents(
            [conversation.model_dump() for conversation in conversations],
        )
