"""GMail Models."""

import datetime
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, EmailStr, FilePath

from src.const import DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES, DEFAULT_PROCESS_CONTENT_TYPES
from src.models.indexers import BaseIndexerConfigModel
from src.models.rag import EmbedderSettings


def _str_to_list(val: str | list[str]) -> list[str]:
    if isinstance(val, list):
        return val
    return [val]


StringOrListString = Annotated[
    str | list[str],
    BeforeValidator(_str_to_list),
]


class EmailFiltersRule(BaseModel):
    """Rule for filtering emails selected."""

    before: datetime.datetime | None = None
    after: datetime.datetime | None = None
    sender: StringOrListString | None = None
    participants: StringOrListString | None = None
    to: StringOrListString | None = None
    cc: StringOrListString | None = None
    bcc: StringOrListString | None = None
    label_ids: list[str] | None = None
    has_attachment: bool | None = None


class EmailFilter(BaseModel):
    """Include/Exclude rules for managing emails."""

    unique_id: str
    include: EmailFiltersRule | None = None
    exclude: EmailFiltersRule | None = None


class GMailAccountConfig(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Model for the configuration for a single gmail account."""

    credentials_path: FilePath
    account_name: str
    save_attachment_types: list[str] | None = None
    save_attachment_type_prefixes: list[str] | None = None
    filters: list[EmailFilter] = []


class GMailConfig(BaseIndexerConfigModel):
    """Model for gmail configuration."""

    type: Literal["gmail"]
    accounts: list[GMailAccountConfig]
    embedder: EmbedderSettings
    save_attachment_types: list[str] = DEFAULT_PROCESS_CONTENT_TYPES
    save_attachment_type_prefixes: list[str] = DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES


class EmailContact(BaseModel):
    """Model for an email contact."""

    email_address: EmailStr | None
    name: str | None = None


class IndexedEmailContact(EmailContact):
    """Model for an email contact used in Meilisearch."""

    id: int
    account_name: str


class ConversationModel(BaseModel):
    """Model used to represent a single email thread."""

    thread_id: str
    participants: list[EmailContact]
    account_name: str


class EmailAttachmentConfig(BaseModel):
    """Model for an email attachment."""

    filename: str
    mime_type: str
    attachment_id: str
    size: int
    content_id: str | None = None


class EmailModel(BaseModel):
    """Config for a single email."""

    timestamp: int
    id: str
    thread_id: str
    label_ids: list[str]
    mime_type: str
    content_type: str
    sender: EmailContact
    to: list[EmailContact]
    cc: list[EmailContact] = []
    bcc: list[EmailContact] = []
    subject: str | None = None
    body: str | None = None
    attachments: list[EmailAttachmentConfig] = []
    account_name: str | None = None


class GmailClassificationLabelFieldValues(BaseModel):
    """Model for ClassificationLabelFieldValue.

    https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#classificationlabelfieldvalue
    """

    fieldId: str
    selection: str


class GmailClassificationLabelValues(BaseModel):
    """Model for ClassificationLabelValues.

    https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#Message.ClassificationLabelValue
    """

    labelId: str
    fields: list[GmailClassificationLabelFieldValues]


class GmailMessageHeader(BaseModel):
    """Model for a message header.

    https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#Message.Header
    """

    name: str
    value: str


class GmailMessagePartBody(BaseModel):
    """Model for MessagePartBody.

    https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages.attachments#MessagePartBody
    """

    attachmentId: str | None = None
    size: int
    data: bytes | None = None


class GmailMessagePart(BaseModel):
    """Model for a message part.

    https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#Message.MessagePart
    """

    partId: str
    mimeType: str
    filename: str
    headers: list[GmailMessageHeader]
    body: GmailMessagePartBody
    parts: "list[GmailMessagePart] | None" = None


class GmailMessage(BaseModel):
    """Model for an email message.

    https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#Message
    """

    id: str
    threadId: str
    labelIds: list[str]
    snippet: str
    historyId: str
    internalDate: str
    payload: GmailMessagePart
    sizeEstimate: int
    raw: bytes | None = None
    classificationLabelValues: GmailClassificationLabelValues | None = None


class MessageIdentifier(BaseModel):
    """Message identifier stub from calling messages.list."""

    id: str
    threadId: str


class ListMessagesResponse(BaseModel):
    """Model representing the response from calling messages.list."""

    messages: list[MessageIdentifier]
    nextPageToken: str | None = None
    resultSizeEstimate: int


class FailedItemModel(BaseModel, arbitrary_types_allowed=True):
    """Model for a failed email item."""

    reason: str | None = None
    exception: Exception
    item: Any
