"""Constants."""

from enum import Enum, StrEnum
from pathlib import Path

from src.models.indices import AddDocumentsKwargField, IndexerRegistryEntry

from .sms import TextMessageIndexer

RCS_CT_CLS = 135


class MessageType(StrEnum):
    """Enum for message type."""

    SMS = "sms"
    MMS = "mms"
    RCS = "rcs"


class MessageBox(Enum):
    """Enum for msg_box field."""

    Received = 1
    Sent = 2
    Draft = 3
    Outbox = 4


class AddressType(Enum):
    """Enum for addr's type field."""

    BCC = 129
    CC = 130
    From = 137
    To = 151


class SMSType(Enum):
    """Enum for sms's type field."""

    Received = 1
    Sent = 2


class SMSStatus(Enum):
    """Enum for sms's status field."""

    NoStatus = -1
    Complete = 0
    Pending = 32
    Failed = 64


CONTENT_TYPE_MESSAGE = "text/plain"

TMP_CONVERSATIONS_PATH = Path("tmp", "conversations.json")
TMP_CONTACTS_PATH = Path("tmp", "contacts.json")
TMP_MESSAGES_PATH = Path("tmp", "messages.json")
ATTACHMENT_DIR = Path(".", "out", "img")

INDEX_SMS = "sms"
INDEX_CONVERSATIONS = "sms_conversations"
INDEX_CONTACTS = "sms_contacts"

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
