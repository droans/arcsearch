"""Parse messages and conversations."""

import json
import logging
import uuid
from pathlib import Path
from typing import cast

import defusedxml.ElementTree

from .const import (
    CONTENT_TYPE_MESSAGE,
    AddressType,
    MessageType,
    SMSType,
)
from .conversations import ExportSMSConversations
from .model_transform import create_message_model
from .models import (
    ConversationModel,
    MMSAttachmentModel,
    MMSModel,
    RCSModel,
    SMSConfig,
    SMSModel,
    XMLAddrModel,
    XMLMMSFullModel,
    XMLPartModel,
    XMLRCSFullModel,
    XMLSMSModel,
)
from .util import generate_conversation_id, save_attachment

logger = logging.getLogger(__name__)


class ExportSMSMessages:
    """Export messages from an SMS Backup & Restore XML file."""

    def __init__(
        self,
        sms_config: SMSConfig,
    ) -> None:
        """Initialize class."""
        self._sms_config = sms_config
        self._personal_number = sms_config.personal_phone_numer
        self._region = sms_config.region
        self._region_code = sms_config.region_code
        self._conv_parser = ExportSMSConversations(sms_config)

    def parse_parts_and_save_imgs(
        self,
        attachment_save_dir: str | Path,
        xml_parts: list[XMLPartModel],
    ) -> tuple[list[MMSAttachmentModel], str | None]:
        """Parse the parts, save images, and return the message and attachments."""
        process_content_types = self._sms_config.save_attachment_types
        process_content_type_prefixes = self._sms_config.save_attachment_type_prefixes
        attachments = []
        msg = None
        for part in xml_parts:
            content_type = part.ct
            if content_type == CONTENT_TYPE_MESSAGE:
                msg = part.text
                continue
            type_matched = content_type in process_content_types
            type_prefix_matched = content_type.startswith(tuple(process_content_type_prefixes))
            if type_matched or type_prefix_matched:
                attachment = save_attachment(attachment_save_dir, part)
                if attachment:
                    attachments.append(attachment)
        return attachments, msg

    def parse_mms_rcs_message(
        self,
        conv_id: int,
        attachment_save_dir: str | Path,
        xml_model: XMLMMSFullModel | XMLRCSFullModel,
    ) -> MMSModel | RCSModel | None:
        """Create MMS model from XML model."""
        timestamp = xml_model.date
        if xml_model.m_cls is None:
            direction = "received"
            sender = cast("str", self.find_group_msg_sender(xml_model.addrs) or "")
        else:
            direction = "sent"
            sender = self._personal_number.replace("+1", "")
        attachments, message = self.parse_parts_and_save_imgs(
            attachment_save_dir=attachment_save_dir,
            xml_parts=xml_model.parts,
        )
        model_cls = MMSModel if xml_model.tag == MessageType.MMS else RCSModel
        readable_date = xml_model.readable_date
        message_id = uuid.uuid4().hex
        return model_cls(
            sender=sender,
            conversation_id=conv_id,
            timestamp=timestamp,
            message=message,
            readable_date=readable_date,
            direction=direction,
            images=attachments,
            message_id=message_id,
        )

    def parse_sms_message(
        self,
        conv_id: int,
        xml_model: XMLSMSModel,
    ) -> SMSModel | None:
        """Create SMS model from XML model."""
        timestamp = xml_model.date
        msg_type = xml_model.type
        if msg_type == SMSType.Received:
            sender = xml_model.address.replace("1+", "")
            direction = "received"
        else:
            sender = self._personal_number.replace("+1", "")
            direction = "sent"
        message = xml_model.body
        date = xml_model.readable_date
        message_id = uuid.uuid4().hex

        if not message:
            logger.info("SMS: No message. Returning")
            return None
        return SMSModel(
            sender=sender,
            conversation_id=conv_id,
            timestamp=timestamp,
            message=message,
            readable_date=date,
            direction=direction,
            message_id=message_id,
        )

    def parse_message_models(
        self,
        conv_id: int,
        attachment_save_dir: str | Path,
        xml_models: list[XMLSMSModel | XMLMMSFullModel | XMLRCSFullModel],
    ) -> list[SMSModel | MMSModel | RCSModel]:
        """Parse a list of conversations."""
        result = []
        for xml_model in xml_models:
            if isinstance(xml_model, XMLSMSModel):
                participants = {self._personal_number.replace("+1", ""), xml_model.address}
                conv_id = generate_conversation_id(participants)
                parsed_model = self.parse_sms_message(
                    conv_id=conv_id,
                    xml_model=xml_model,
                )
            else:
                participants = parse_mms_participants(xml_model.addrs)
                conv_id = generate_conversation_id(participants)
                parsed_model = self.parse_mms_rcs_message(
                    conv_id=conv_id,
                    attachment_save_dir=attachment_save_dir,
                    xml_model=xml_model,
                )
            if parsed_model:
                result.append(parsed_model)
        return result

    def export_messages_and_conversations(
        self,
        messages_xml_path: str | Path,
        messages_save_path: str | Path,
        conversations_save_path: str | Path,
        attachment_save_dir: str | Path,
    ) -> tuple[list[SMSModel | MMSModel | RCSModel], list[ConversationModel]]:
        """Export messages, attachments, and conversations to provided paths."""
        conversations = []
        messages = []
        context = defusedxml.ElementTree.iterparse(messages_xml_path, events=("end",))
        for _event, elem in context:
            tag = elem.tag
            if tag not in ("sms", "mms"):
                msg = f"Skipping tag {tag}, not SMS/MMS ({elem})"
                logger.debug(msg)
                continue

            model = create_message_model(elem)
            if model is None:
                logger.info("Couldn't create message model, skipping.")
                continue

            conv = self._conv_parser.parse_message_conversation(model)
            if conv is None:
                logger.info("Can't get conversation, skipping.")
                continue
            conv_id = conv.conversation_id
            if isinstance(model, XMLSMSModel):
                logger.debug("Processing SMS message")
                parsed = self.parse_sms_message(
                    conv_id=conv_id,
                    xml_model=model,
                )
            else:
                logger.debug("Processing MMS message")
                parsed = self.parse_mms_rcs_message(
                    conv_id=conv_id,
                    attachment_save_dir=attachment_save_dir,
                    xml_model=model,
                )
            if parsed:
                logger.debug("Adding message/conversation")
                if conv not in conversations:
                    conversations.append(conv)
                messages.append(parsed)
        logger.info("Finished parsing messages.")
        logger.info("Saving messages...")

        dumped_messages = [message.model_dump() for message in messages]
        with open(messages_save_path, "w") as f:
            f.write(json.dumps(dumped_messages, indent=4))
        logger.info("Saved messages.")
        logger.info("Saving conversations...")

        dumped_conversations = [conversation.model_dump() for conversation in conversations]
        with open(conversations_save_path, "w") as f:
            f.write(json.dumps(list(dumped_conversations), indent=4))
        logger.info("Saved conversations.")
        return messages, conversations

    def find_group_msg_sender(self, addrs: list[XMLAddrModel]) -> str | None:
        """Find the sender in a group message."""
        for addr in addrs:
            if addr.type == AddressType.From:
                return addr.address
        return None


def generate_message_unique_id(xml_model: XMLSMSModel | XMLRCSFullModel | XMLMMSFullModel) -> int:
    """Generate a unique ID for a message."""
    if isinstance(xml_model, XMLSMSModel):
        val = f"{xml_model.date}-{xml_model.body}-{xml_model.address}"
    else:
        msg_type = "rcs" if isinstance(xml_model, XMLRCSFullModel) else "mms"
        val = f"{msg_type}-{xml_model._id}"  # noqa: SLF001
    return hash(val)


def parse_mms_participants(xml_addrs: list[XMLAddrModel]) -> set[str]:
    """Return a set of all participants in a message."""
    return {xml_addr.address for xml_addr in xml_addrs}
