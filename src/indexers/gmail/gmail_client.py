"""Client to interact with GMail."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.indexers.gmail.const import DataPaths
from src.indexers.gmail.filter_email_data_list import create_filter_string
from src.indexers.gmail.models import (
    EmailFilter,
    EmailFiltersRule,
    FailedItemModel,
    GmailMessage,
    ListMessagesResponse,
)
from src.indexers.gmail.process_email import process_email
from src.indexers.gmail.utils import (
    get_last_process_datetime_for_account_and_filters,
)

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource

    from src.indexers.gmail.models import (
        EmailModel,
        GMailAccountConfig,
        GMailConfig,
        MessageIdentifier,
    )
    from src.models.indexers import RuntimeData

logger = logging.getLogger(__name__)


class GmailClient:
    """Client to interact with GMail."""

    def __init__(
        self,
        runtime_data: RuntimeData,
        config: GMailConfig,
    ) -> None:
        """Initialize class."""
        self._runtime_data = runtime_data
        self._config = config

    def _create_client(self, account_name: str) -> GmailResource | None:
        """Create client for account."""
        account = self.get_account_by_name(account_name)
        if not account:
            return None
        creds = Credentials.from_authorized_user_file(filename=account.credentials_path)
        if creds.expired:
            creds.refresh(Request())

        return build(
            serviceName="gmail",
            version="v1",
            credentials=creds,
        )

    def get_account_by_name(self, account_name: str) -> GMailAccountConfig | None:
        """Get an account by the account name."""
        accounts = self._config.accounts
        for account in accounts:
            if account.account_name == account_name:
                return account
        return None

    def get_message_data_page(
        self,
        client: GmailResource,
        account_name: str,
        page_token: str | None = None,
        _filter: EmailFilter | None = None,
        reprocess: bool = False,
    ) -> ListMessagesResponse:
        """Retrieve a single page of message data.

        If `reprocess` is False, this function will use the filters and additionally ensure message
            data is only pulled for new emails since the last run.
        If `reprocess` is True, this function will only use the filters.
        """
        if not reprocess:
            if _filter is None:
                _filter = EmailFilter(unique_id="auto")
            if _filter.include is None:
                _filter.include = EmailFiltersRule()
            latest_ts = get_last_process_datetime_for_account_and_filters(
                data_directory=self._runtime_data.data_directory,
                account_name=account_name,
                filters=_filter,
            )
            msg = f"Not set to reprocess; using latest timestamp of {latest_ts}."
            logger.debug(msg)
            _filter.include.after = max(_filter.include.after, latest_ts) if _filter.include.after else latest_ts
        qry_filters = create_filter_string(_filter) if _filter else None
        if qry_filters:
            msg = f'Final query string: "{qry_filters}"'
            logger.debug(msg)
        response = (
            client.users()
            .messages()
            .list(
                userId="me",
                pageToken=page_token,
                q=qry_filters,
            )
            .execute()
        )
        return ListMessagesResponse.model_validate(response)

    def retrieve_message_data(
        self,
        client: GmailResource,
        account_name: str,
        _filter: EmailFilter,
        reprocess: bool = False,
    ) -> list[MessageIdentifier]:
        """Retrieve email data which matches the filter.

        If `reprocess` is False, this function will use the filters and additionally ensure message
            data is only pulled for new emails since the last run.
        If `reprocess` is True, this function will only use the filters.
        """
        next_page_token = None
        result: list[MessageIdentifier] = []
        msg = f"Retrieving messages for {account_name} using filters [{_filter.model_dump()}] (Reprocess: {reprocess})"
        logger.debug(msg)
        while True:
            tmp = self.get_message_data_page(
                client=client,
                account_name=account_name,
                page_token=next_page_token,
                _filter=_filter,
                reprocess=reprocess,
            )
            result.extend(tmp.messages)
            next_page_token = tmp.nextPageToken
            if not next_page_token:
                logger.debug("Received no new page token, assuming we have all our messages.")
                break
        return result

    def retrieve_single_message(
        self,
        client: GmailResource,
        message_data: MessageIdentifier,
    ) -> EmailModel:
        """Retrieve a single message."""
        msg_id = message_data.id
        msg = f"Retrieving message for ID {msg_id}"
        logger.debug(msg)
        data = client.users().messages().get(userId="me", id=msg_id).execute()
        try:
            parsed = GmailMessage.model_validate(data)
        except Exception as e:
            failed_data_path = DataPaths.FAILED_EMAIL_PROCESSING
            log_msg = f"Failed to parse {msg_id}, writing to {failed_data_path}"
            logger.exception(log_msg)
            data = FailedItemModel(
                exception=e,
                item=data,
            )
            self._write_to_failed_data_json(fail_file_path=failed_data_path, data=data)
            raise
        try:
            return process_email(parsed)
        except Exception as e:
            failed_data_path = DataPaths.FAILED_EMAIL_PROCESSING
            log_msg = f"Failed to process email {msg_id}, writing to {failed_data_path}"
            logger.exception(log_msg)
            data = FailedItemModel(
                exception=e,
                item=parsed,
            )
            self._write_to_failed_data_json(fail_file_path=failed_data_path, data=data)
            raise

    def retrieve_message_data_for_filters(
        self,
        client: GmailResource,
        account_name: str,
        message_filters: list[EmailFilter],
        reprocess: bool = False,
    ) -> list[MessageIdentifier]:
        """Retrieve all messages from account.

        If `reprocess` is False, this function will use the filters and additionally ensure message
            data is only pulled for new emails since the last run.
        If `reprocess` is True, this function will only use the filters.
        """
        result: list[MessageIdentifier] = []
        for _filter in message_filters:
            message_data = self.retrieve_message_data(
                client=client,
                account_name=account_name,
                _filter=_filter,
                reprocess=reprocess,
            )
            [result.append(msg_data) for msg_data in message_data if msg_data not in result]

        return result

    def retrieve_messages(
        self,
        client: GmailResource,
        account_name: str,
        message_data: list[MessageIdentifier],
    ) -> list[EmailModel]:
        """Retrieve emails from a list of message data."""
        result = []
        for msg_data in message_data:
            message = self.retrieve_single_message(client=client, message_data=msg_data)
            message.account_name = account_name
            result.append(message)
        return result

    def retrieve_all_messages_for_account(
        self,
        account_name: str,
        reprocess: bool = False,
        _filters: list[EmailFilter] | None = None,
    ) -> list[EmailModel]:
        """Retrieve all messages for a single account.

        If `reprocess` is False, this function will use the filters and additionally ensure message
            data is only pulled for new emails since the last run.
        If `reprocess` is True, this function will only use the filters.
        """
        client = self._create_client(account_name=account_name)
        account_conf = self.get_account_by_name(account_name=account_name)
        assert client
        assert account_conf
        msg = f"Retrieving all messages for {account_name} (Reprocess: {reprocess})."
        logger.info(msg)
        used_filters = _filters or account_conf.filters
        message_data = self.retrieve_message_data_for_filters(
            client=client,
            account_name=account_name,
            message_filters=used_filters,
            reprocess=reprocess,
        )
        return self.retrieve_messages(
            client=client,
            account_name=account_name,
            message_data=message_data,
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
