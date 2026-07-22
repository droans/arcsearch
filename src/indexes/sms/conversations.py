"""Conversation functions."""

import json
import logging
from pathlib import Path

from defusedxml import ElementTree

from .models import ConversationModel, XMLAddrModel, XMLMMSFullModel, XMLRCSFullModel, XMLSMSModel
from .util import generate_conversation_id

logger = logging.getLogger(__name__)


def parse_sms_message_converation(
    xml_model: XMLSMSModel,
    personal_number: str,
) -> ConversationModel:
    """Parse a SMS message to create the conversation element."""
    address = xml_model.address.replace("+1", "")
    recips = {address, personal_number.replace("+1", "")}
    conv_id = generate_conversation_id(recips)
    return ConversationModel(recipients=list(recips), conversation_id=conv_id)


def parse_mms_message_converation(
    xml_model: list[XMLAddrModel],
    personal_number: str,
) -> ConversationModel | None:
    """Parse an MMS message to create the conversation element."""
    if not xml_model:
        logger.info(msg="parse_mms_message_conversation: No addresses found. Returning.")
        return None
    recips = {personal_number.replace("+1", "")}
    for address in xml_model:
        addr = address.address
        if addr:
            addr = addr.replace("+1", "")
            recips.add(addr)
    conv_id = generate_conversation_id(recips)
    return ConversationModel(recipients=list(recips), conversation_id=conv_id)


def parse_message_conversation(
    xml_model: XMLSMSModel | XMLMMSFullModel | XMLRCSFullModel,
    personal_phone_number: str,
) -> ConversationModel | None:
    """Parse individual message to determine conversation."""
    if xml_model.tag == "sms":
        return parse_sms_message_converation(xml_model, personal_phone_number)
    return parse_mms_message_converation(xml_model.addrs, personal_phone_number)


def parse_conversations(
    messages_xml_path: str | Path,
    personal_phone_number: str,
) -> list[ConversationModel]:
    """Parse all messages for distinct conversations."""
    conversations = []
    context = ElementTree.iterparse(messages_xml_path, events=("end",))
    for _event, elem in context:
        conv = parse_message_conversation(elem, personal_phone_number)
        if conv and conv not in conversations:
            msg = "Exporting conversation {conv}"
            logger.info(msg)
            conversations.append(conv)
    return conversations


def export_conversations(
    messages_xml_path: str | Path,
    output_file_path: str | Path,
    personal_number: str,
) -> None:
    """Export conversations."""
    logger.info("Exporting conversations")
    conversations = parse_conversations(messages_xml_path, personal_number)
    dumped = [conv.model_dump() for conv in conversations]
    with open(output_file_path, "w") as f:
        f.write(json.dumps(dumped, indent=4))
    logger.info("Conversations exported.")
