"""GMail Models."""

import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, EmailStr, FilePath

from src.models.indices import BaseIndexerConfigModel, BaseMessageWithAttachmentConfig
from src.models.rag import EmbedderSettings


def _str_to_list(val: str) -> list[str]:
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


class EmailFilter(BaseModel):
    """Include/Exclude rules for managing emails."""

    include: EmailFiltersRule | None = None
    exclude: EmailFiltersRule | None = None


class GMailAccountConfig(
    BaseModel,
    arbitrary_types_allowed=True,
):
    """Model for the configuration for a single gmail account."""

    type: Literal["gmail"]
    credentials_path: FilePath
    account_name: str | None = None
    embedder: EmbedderSettings | None = None
    save_attachment_types: list[str] | None = None
    save_attachment_type_prefixes: list[str] | None = None


class GMailConfig(BaseMessageWithAttachmentConfig, BaseIndexerConfigModel):
    """Model for gmail configuration."""

    accounts: list[GMailAccountConfig]


class EmailContact(BaseModel):
    """Model for an email contact."""

    email_address: EmailStr | None
    name: str | None = None


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
    cc: list[EmailContact]
    bcc: list[EmailContact]
    subject: str
    body: str
    attachments: list[EmailAttachmentConfig] = []


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
