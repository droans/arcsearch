"""Message utilities."""

import base64
import logging
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from .const import RCS_CT_CLS
from .models import (
    MessageType,
    MMSAttachmentModel,
    XMLMMSModel,
    XMLPartModel,
    XMLSMSModel,
)

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def generate_conversation_id(recipients: set[str]) -> int:
    """Generate the conversation ID for a message."""
    recips = tuple(recipients)
    return hash(recips)


def get_message_type_from_model(xml_model: XMLSMSModel | XMLMMSModel) -> MessageType:
    """Determine message type from the XML model."""
    if isinstance(xml_model, XMLSMSModel):
        return MessageType.SMS
    msg_cls = xml_model.ct_cls
    if msg_cls == RCS_CT_CLS:
        return MessageType.RCS
    return MessageType.MMS


def get_message_type_from_element(elem: "ET.Element") -> MessageType:
    """Determine message type from the element."""
    tag = elem.tag
    if tag == "sms":
        return MessageType.SMS
    msg_cls = elem.get("ct_cls")
    if msg_cls == "135":
        return MessageType.RCS
    return MessageType.MMS


def get_img_path(save_dir: str | Path, file_name: str, content_type: str) -> Path:
    """Get path for image."""
    split_name = file_name.split(".")
    if len(split_name) < 2:  # noqa: PLR2004
        ext = content_type.rsplit("/", maxsplit=1)[-1]
        base_name = split_name[0]
    else:
        ext = split_name[-1]
        base_name = ".".join(split_name[:-1])
    used_name = f"{base_name}.{ext}"
    path = Path(save_dir, used_name)
    if path.exists():
        uid = uuid.uuid4().fields[0]
        used_name = f"{base_name}_{uid}.{ext}"
        path = Path(save_dir, used_name)
        msg = f"Path already existed for {used_name}"
        logger.info(msg)
        msg = f"(From:{base_name})"
        logger.info(msg)
    return path


def save_attachment(save_dir: str | Path, xml_model: XMLPartModel) -> MMSAttachmentModel | None:
    """Save the attachment."""
    ct = xml_model.ct
    cl = xml_model.cl
    name = xml_model.name
    file_name = name if name and name != "null" else cl
    data = xml_model.data
    if not ct or not file_name or not data:
        return None
    path = get_img_path(save_dir, file_name, ct)
    msg = f"Saving attachment to {path}"
    logger.debug(msg)
    decoded = base64.b64decode(data)
    with open(path, "wb") as f:
        f.write(decoded)
    return MMSAttachmentModel(
        filename=file_name,
        content_type=ct,
    )
