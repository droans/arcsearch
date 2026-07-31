"""Gmail Indexer."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.indexers.gmail.gmail_client import GmailClient
from src.indexers.gmail.utils import (
    get_all_contacts,
    get_all_conversations,
    store_account_last_process_timestamp,
)
from src.models.indexers import BaseIndexerClass, RuntimeData
from src.util.meilisearch import update_index_embedder_config

from .models import (
    ConversationModel,
    EmailFilter,
    EmailModel,
    FailedItemModel,
    GMailAccountConfig,
    GMailConfig,
    IndexedEmailContact,
)

if TYPE_CHECKING:
    from meilisearch import Client

INDEX_EMAILS = "gmail_emails"
INDEX_CONTACTS = "gmail_contacts"
INDEX_CONVERSATIONS = "gmail_conversations"

logger = logging.getLogger(__name__)


class GmailEmailIndexer(BaseIndexerClass):
    """Indexer managing interactions with the gmail_email index and data."""

    def __init__(
        self,
        runtime_data: RuntimeData,
        config: GMailConfig,
        meilisearch_client: "Client",
    ) -> None:
        """Initialize class."""
        self._runtime_data = runtime_data
        self._config = config
        self._meilisearch_client = meilisearch_client
        self._gmail_client = GmailClient(runtime_data=runtime_data, config=config)

    def get_account_by_name(self, account_name: str) -> GMailAccountConfig | None:
        """Get an account by the account name."""
        account_ls = [account for account in self._config.accounts if account.account_name == account_name]
        if account_ls:
            return account_ls[0]
        return None

    def import_messages_to_meilisearch(self, account_name: str, messages: list[EmailModel]) -> None:
        """Import messages into Meilisearch."""
        for message in messages:
            message.account_name = account_name
        self._meilisearch_client.index(INDEX_EMAILS).add_documents(
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
        self._meilisearch_client.index(INDEX_CONTACTS).add_documents(
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
        with open("wtf.json", "w") as f:
            f.write(json.dumps([conversation.model_dump() for conversation in conversations]))
        self._meilisearch_client.index(INDEX_CONVERSATIONS).add_documents(
            [conversation.model_dump() for conversation in conversations],
        )

    def add_documents(
        self,
        account_names: list[str] | str | None = None,
        filters: list[EmailFilter] | None = None,
        reprocess: bool = False,
    ) -> None:
        """Import messages interface."""
        if not account_names:
            account_names = [account.account_name for account in self._config.accounts]
        if isinstance(account_names, str):
            account_names = [account_names]
        for account_name in account_names:
            msg = f"Retrieving messages for {account_name}"
            logger.info(msg)
            messages = self._gmail_client.retrieve_all_messages_for_account(
                account_name=account_name,
                reprocess=reprocess,
                _filters=filters,
            )
            msg = f"Found {len(messages)} messages."
            logger.info(msg)
            conversations = get_all_conversations(account_name=account_name, messages=messages)
            contacts = get_all_contacts(account_name=account_name, messages=messages)

            logger.debug("Importing all messages.")
            self.import_messages_to_meilisearch(account_name=account_name, messages=messages)
            logger.debug("Imported all messages.")

            logger.debug("Importing all conversations.")
            self.import_conversations_to_meilisearch(
                account_name=account_name,
                conversations=conversations,
            )
            logger.debug("Imported all conversations.")

            logger.debug("Importing all contacts.")
            self.import_contacts_to_meilisearch(account_name=account_name, contacts=contacts)
            logger.debug("Imported all contacts.")

            store_account_last_process_timestamp(
                data_directory=self._runtime_data.data_directory,
                account_name=account_name,
            )

    def setup_embedder(self) -> None:
        """Setup embedder."""
        embed_config = self._config.embedder
        if embed_config.document_template is None:
            indices = self._runtime_data.manifest.indices
            email_conf = next(index for index in indices if index.index_uid == INDEX_EMAILS)
            document_template = email_conf.embedder.default_document_template
            embed_config.document_template = document_template

            update_index_embedder_config(
                idx=self._meilisearch_client.index(INDEX_EMAILS),
                embedder_config=embed_config,
            )

    def _write_to_failed_data_json(self, fail_file_path: Path, data: FailedItemModel) -> None:
        """Record failed email processes to the failed data path."""
        path = self._get_or_create_failed_data_json(fail_file_path=fail_file_path)
        dumped = data.model_dump()
        exc = dumped.pop("exception", None)
        if isinstance(exc, Exception):
            dumped["exception"] = f"{exc.__class__.__name__} - {exc}"
        with open(path, "w+") as f:
            file_data: list = json.loads(f.read())
            file_data.append(dumped)
            f.write(json.dumps(file_data))

    def _get_or_create_failed_data_json(self, fail_file_path: Path) -> Path:
        """Get or create the file for storing a failed message log."""
        path = Path(self._runtime_data.data_directory, fail_file_path)
        if not path.exists():
            path.touch()
            with open(path, "w") as f:
                f.write("[]")
        return path
