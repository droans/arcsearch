"""Process emails."""

import base64
import re
from email.utils import getaddresses
from typing import TYPE_CHECKING

from src.indexers.gmail.models import (
    EmailAttachmentConfig,
    EmailContact,
    EmailModel,
    GmailMessage,
    GmailMessageHeader,
    GmailMessagePart,
)

if TYPE_CHECKING:
    from googleapiclient._apis.gmail.v1.resources import GmailResource

"""
HAVE:
    sender: EmailStr
    to: list[EmailStr]
    cc: list[EmailStr]
    bcc: list[EmailStr]
    timestamp: int
    id: str
    thread_id: str
    label_ids: list[str]
    content_type: str

NEED:
    subject: str
    body: str
    attachments: str
"""


def _create_header_dict(headers: list[GmailMessageHeader]) -> dict[str, str]:
    """Create dictionary for headers from the header name."""
    return {hdr.name.lower(): hdr.value for hdr in headers}


def _process_address(addr: str) -> list[EmailContact]:
    """Process a string representing an address."""
    parsed = getaddresses([addr])[0]
    result = []
    for name, email_address in parsed:
        _nm = name
        if _nm == "":
            _nm = None
        result.append(EmailContact(name=_nm, email_address=email_address))
    return result


def _get_content_id(part: GmailMessagePart) -> str | None:
    """Get the content ID from a message part."""
    headers = _create_header_dict(part.headers)
    cid = headers.get("content-id")
    return cid.strip("<>") if cid else None


def _get_text_charset_from_part(part: GmailMessagePart) -> str | None:
    """Get the charset for text content from a message part."""
    headers = _create_header_dict(part.headers)
    ct = headers.get("content-type")
    if not ct:
        return None
    ct_data = ct.split("; ")
    charset_str = [data for data in ct_data if data.startswith("charset")]
    if not charset_str:
        return None
    return charset_str[0].split("=")[-1]


def _process_payload_for_body_and_attachments(
    part: GmailMessagePart,
) -> tuple[dict[str, str], list[EmailAttachmentConfig]]:
    """Recursively process payload to combine body and attachment data."""
    if part.parts:
        text_parts: dict[str, str] = {}
        attachments: list[EmailAttachmentConfig] = []
        for child in part.parts:
            child_text, child_attachments = _process_payload_for_body_and_attachments(child)
            text_parts.update(child_text)
            attachments.extend(child_attachments)
        return text_parts, attachments

    if part.body.attachmentId:
        attachment = EmailAttachmentConfig(
            filename=part.filename,
            mime_type=part.mimeType,
            attachment_id=part.body.attachmentId,
            size=part.body.size,
            content_id=_get_content_id(part),
        )
        return {}, [attachment]
    if part.body.data and part.mimeType in ("text/plain", "text/html"):
        charset = _get_text_charset_from_part(part) or "utf-8"
        body = part.body.data.decode(charset, errors="replace")
        return {part.mimeType: body}, []
    return {}, []


def _rewrite_cids(html: str, message_id: str, attachments: list[EmailAttachmentConfig]) -> str:
    """
    Rewrite CIDs.

    Point cid: references at a resolvable attachment locator instead of a raw
    Content-ID, and mark the corresponding AttachmentInfo as truly inline.
    A content_id only "counts" as inline if it's actually used in the HTML —
    Gmail sometimes stamps Content-ID on ordinary (non-inline) attachments too.
    """
    by_cid = {a.content_id: a for a in attachments if a.content_id}

    def replace(match: re.Match) -> str:
        cid = match.group(1)
        attachment = by_cid.get(cid)
        if attachment is None:
            return match.group(0)  # Unknown CID, leave untouched
        return f"cid:{message_id}/{attachment.attachment_id}"

    rewritten = re.sub(r'cid:([^"\'\s)]+)', replace, html)
    referenced_cids = set(re.findall(r'cid:[^/]+/([^"\'\s)]+)', rewritten))
    for attachment in attachments:
        if attachment.content_id and attachment.content_id not in referenced_cids:
            attachment.content_id = None
    return rewritten


def process_email(raw_email: dict) -> EmailModel:
    """Processes a raw email returned from the gmail API and returns it as a model."""
    message_model = GmailMessage.model_validate(raw_email)

    headers = _create_header_dict(message_model.payload.headers)

    msg_to = _process_address(headers.get("to", ""))
    msg_from = _process_address(headers.get("from", ""))[0]
    msg_cc = _process_address(headers.get("cc", ""))
    msg_bcc = _process_address(headers.get("bcc", ""))
    timestamp = int(int(message_model.internalDate) / 1000)
    msg_id = message_model.id
    thread_id = message_model.threadId
    label_ids = message_model.labelIds
    mime_type = message_model.payload.mimeType
    subject = headers.get("subject", "")

    text_parts, attachments = _process_payload_for_body_and_attachments(message_model.payload)

    if "text/html" in text_parts:
        content_type = "text/html"
        body = _rewrite_cids(text_parts["text/html"], message_model.id, attachments)
    elif "text/plain" in text_parts:
        content_type = "text/plain"
        body = text_parts["text/plain"]
    else:
        content_type = "text/plain"
        body = ""

    return EmailModel(
        timestamp=timestamp,
        id=msg_id,
        thread_id=thread_id,
        label_ids=label_ids,
        mime_type=mime_type,
        sender=msg_from,
        to=msg_to,
        cc=msg_cc,
        bcc=msg_bcc,
        subject=subject,
        body=body,
        content_type=content_type,
        attachments=attachments,
    )


def fetch_attachment(
    client: "GmailResource",
    message_id: str,
    attachment: EmailAttachmentConfig,
) -> bytes:
    """Download an attachment and return the bytes."""
    resp = (
        client.users()
        .messages()
        .attachments()
        .get(
            userId="me",
            messageId=message_id,
            id=attachment.attachment_id,
        )
        .execute()
    )
    data = resp["data"]
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded)
