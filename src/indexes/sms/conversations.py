"""Conversation functions."""

import json
import logging
from pathlib import Path

from defusedxml import ElementTree

from src.util.contacts import is_phone_number, parse_phone_number

from .models import (
    ConversationModel,
    SMSConfig,
    XMLAddrModel,
    XMLMMSFullModel,
    XMLRCSFullModel,
    XMLSMSModel,
)
from .util import generate_conversation_id

logger = logging.getLogger(__name__)


class ExportSMSConversations:
    """Export conversations from an SMS Backup & Restore XML file."""

    def __init__(
        self,
        sms_config: SMSConfig,
    ) -> None:
        """Initialize class."""
        self._sms_config = sms_config
        self._parsed_personal_number = parse_phone_number(
            sms_config.personal_phone_numer,
            sms_config.region,
        )
        self._region = sms_config.region
        self._region_code = sms_config.region_code

    def safe_parse_address(self, address: str) -> str:
        """Return parsed phone number if address is a phone number. Otherwise, return address."""
        if is_phone_number(address, self._region):
            return parse_phone_number(address, self._region)
        return address

    def parse_sms_message_converation(self, xml_model: XMLSMSModel) -> ConversationModel:
        """Parse a SMS message to create the conversation element."""
        address = self.safe_parse_address(xml_model.address)
        recips = {address, self._parsed_personal_number}
        conv_id = generate_conversation_id(recips)
        return ConversationModel(recipients=list(recips), conversation_id=conv_id)

    def parse_mms_message_converation(
        self,
        xml_model: list[XMLAddrModel],
    ) -> ConversationModel | None:
        """Parse an MMS message to create the conversation element."""
        if not xml_model:
            logger.info(msg="parse_mms_message_conversation: No addresses found. Returning.")
            return None
        recips = {self._parsed_personal_number}
        for address in xml_model:
            addr = address.address
            if addr:
                recips.add(self.safe_parse_address(addr))
        conv_id = generate_conversation_id(recips)
        return ConversationModel(recipients=list(recips), conversation_id=conv_id)

    def parse_message_conversation(
        self,
        xml_model: XMLSMSModel | XMLMMSFullModel | XMLRCSFullModel,
    ) -> ConversationModel | None:
        """Parse individual message to determine conversation."""
        if xml_model.tag == "sms":
            return self.parse_sms_message_converation(xml_model)
        return self.parse_mms_message_converation(xml_model.addrs)

    def parse_conversations(
        self,
        messages_xml_path: str | Path,
    ) -> list[ConversationModel]:
        """Parse all messages for distinct conversations."""
        conversations = []
        context = ElementTree.iterparse(messages_xml_path, events=("end",))
        for _event, elem in context:
            conv = self.parse_message_conversation(elem)
            if conv and conv not in conversations:
                msg = "Exporting conversation {conv}"
                logger.info(msg)
                conversations.append(conv)
        return conversations

    def export_conversations(
        self,
        messages_xml_path: str | Path,
        output_file_path: str | Path,
    ) -> None:
        """Export conversations."""
        logger.info("Exporting conversations")
        conversations = self.parse_conversations(messages_xml_path)
        dumped = [conv.model_dump() for conv in conversations]
        with open(output_file_path, "w") as f:
            f.write(json.dumps(dumped, indent=4))
        logger.info("Conversations exported.")
