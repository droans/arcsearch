"""Utility Functions."""

import logging

from src.indexers.gmail.models import (
    ConversationModel,
    EmailContact,
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
        participants = list(
            {
                message.sender,
                *message.to,
                *message.cc,
                *message.bcc,
            },
        )
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
    return result
