"""Utility Functions."""

import datetime
import json
import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from src.indexers.gmail.const import DataPaths
from src.indexers.gmail.models import (
    ConversationModel,
    EmailContact,
    EmailFilter,
    EmailModel,
    IndexedEmailContact,
)

logger = logging.getLogger(__name__)


def get_all_conversations(account_name: str, messages: list[EmailModel]) -> list[ConversationModel]:
    """Create lists of conversations."""
    all_threads: dict[str, list[EmailContact]] = {}
    for message in messages:
        thread_id = message.thread_id
        thread_participants = all_threads.get(thread_id, [])
        participants = [
            message.sender,
            *message.to,
            *message.cc,
            *message.bcc,
        ]
        msg = f"Message {message.id} participants: {participants}"
        logger.debug(msg)
        [
            thread_participants.append(participant)
            for participant in participants
            if participant not in thread_participants
        ]
        all_threads[thread_id] = thread_participants
    msg = f"Conversations found: {len(all_threads)}"
    logger.debug(msg)
    return [
        ConversationModel(thread_id=thread_id, participants=participants, account_name=account_name)
        for thread_id, participants in all_threads.items()
    ]


def get_all_contacts(account_name: str, messages: list[EmailModel]) -> list[IndexedEmailContact]:
    """Create list of all contacts."""
    all_contacts: list[EmailContact] = []
    for message in messages:
        participants = [message.sender, *message.to, *message.cc, *message.bcc]
        [
            all_contacts.append(participant)
            for participant in participants
            if participant not in all_contacts
        ]
    result = []
    for contact in all_contacts:
        dumped = contact.model_dump()
        dumped["id"] = hash(f"{contact.email_address}::{contact.name}")
        dumped["account_name"] = account_name
        result.append(IndexedEmailContact.model_validate(dumped))
    msg = f"Contacts found: {len(result)}"
    logger.debug(msg)
    return result


def store_account_last_process_timestamp(
    data_directory: Path,
    account_name: str,
    timestamp: int | None = None,
) -> None:
    """Store the timestamp for the last time the emails for an account were processed."""
    if timestamp is None:
        timestamp = int(datetime.datetime.now().timestamp())
    path = Path(data_directory, DataPaths.LAST_PROCESS_TS)
    msg = f"Storing last process timestamp ({timestamp}) for {account_name}."
    logger.debug(msg)
    if not path.exists():
        path.touch()
        with open(path, "w+") as f:
            f.write("{}")

    with open(path) as f:
        data: dict[str, int] = json.loads(f.read())
    data[account_name] = timestamp
    with open(path, "w+") as f:
        f.write(json.dumps(data))


def get_last_process_datetime_for_account_and_filters(
    data_directory: Path,
    account_name: str,
    filters: EmailFilter | None,
) -> datetime.datetime:
    """Retrieve the latest processing time for the given account and filters."""
    filter_id = filters.unique_id if filters else None
    path = Path(data_directory, DataPaths.LAST_PROCESS_TS)
    if not path.exists():
        path.touch()
        with open(path, "w") as f:
            f.write("{}")

    with open(path) as f:
        data: dict[str, dict[str, int]] = json.loads(f.read())

    account_data = data.get(account_name, {})
    filter_ts = account_data.get(filter_id, 0)
    return datetime.datetime.fromtimestamp(filter_ts)


def get_and_refresh_credentials(
    credentials_path: Path,
    save_refreshed_credentials: bool,
) -> Credentials | None:
    """Get and update stored credentials."""
    creds: Credentials = Credentials.from_authorized_user_file(filename=credentials_path)
    if not creds:
        return None
    if creds.expired:
        creds.refresh(Request())
        if save_refreshed_credentials:
            with open(credentials_path, "w") as f:
                f.write(creds.to_json())
    return creds
