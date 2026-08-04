"""Gmail Indexer."""

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from src.indexers.gmail.gmail_client import GmailClient
from src.indexers.gmail.index import GMailIndexer
from src.indexers.gmail.utils import (
    get_all_contacts,
    get_all_conversations,
    store_account_last_process_timestamp,
)
from src.models.arcsearch import AppModel, RuntimeData
from src.models.indexers import BaseIndexerClass

from .models import (
    EmailFilter,
    FailedItemModel,
    GMailAccountConfig,
    GMailConfig,
)

if TYPE_CHECKING:
    from meilisearch import Client


logger = logging.getLogger(__name__)


class GmailEmailIndexer(BaseIndexerClass):
    """Indexer managing interactions with the gmail_email index and data."""

    def __init__(
        self,
        app: AppModel,
        runtime_data: RuntimeData,
        meilisearch_client: "Client",
    ) -> None:
        """Initialize class."""
        self.app = app
        self.runtime_data = runtime_data
        self.meilisearch_client = meilisearch_client
        config = runtime_data.config
        assert isinstance(config, GMailConfig)
        self.config = config
        self.index_client = GMailIndexer(
            app=app,
            runtime_data=runtime_data,
            meilisearch_client=meilisearch_client,
        )
        self._gmail_client = GmailClient(app=app, runtime_data=runtime_data)

    def get_account_by_name(self, account_name: str) -> GMailAccountConfig | None:
        """Get an account by the account name."""
        account_ls = [account for account in self.config.accounts if account.account_name == account_name]
        if account_ls:
            return account_ls[0]
        return None

    def add_documents(
        self,
        account_names: list[str] | str | None = None,
        filters: list[EmailFilter] | None = None,
        reprocess: bool = False,
    ) -> None:
        """Import messages interface."""
        if not account_names:
            account_names = [account.account_name for account in self.config.accounts]
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
            self.index_client.import_messages_to_meilisearch(account_name=account_name, messages=messages)
            logger.debug("Imported all messages.")

            logger.debug("Importing all conversations.")
            self.index_client.import_conversations_to_meilisearch(
                account_name=account_name,
                conversations=conversations,
            )
            logger.debug("Imported all conversations.")

            logger.debug("Importing all contacts.")
            self.index_client.import_contacts_to_meilisearch(account_name=account_name, contacts=contacts)
            logger.debug("Imported all contacts.")

            store_account_last_process_timestamp(
                data_directory=self.runtime_data.data_directory,
                account_name=account_name,
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
        path = Path(self.runtime_data.data_directory, fail_file_path)
        if not path.exists():
            path.touch()
            with open(path, "w") as f:
                f.write("[]")
        return path
