"""Transform XML ETrees into models."""

import logging
from typing import TYPE_CHECKING, Any

from .const import MessageType
from .models import (
    XMLAddrModel,
    XMLMMSFullModel,
    XMLPartModel,
    XMLRCSFullModel,
    XMLSMSModel,
)
from .util import get_message_type_from_element

if TYPE_CHECKING:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def create_part_xml_model(part_elem: "ET.Element | None") -> XMLPartModel | None:
    """Create part model from `part` Element."""
    if part_elem is None:
        return None
    data = dict(part_elem.items())
    return XMLPartModel.model_validate(data)


def create_parts_xml_model(parts_elem: "ET.Element | None") -> list[XMLPartModel]:
    """Create part models from `parts` Element."""
    if parts_elem is None:
        return []
    result = []
    for elem in parts_elem:
        model = create_part_xml_model(elem)
        if model:
            result.append(model)
    return result


def create_addr_xml_model(addr_elem: "ET.Element | None") -> XMLAddrModel | None:
    """Create addr model from `addr` Element."""
    if addr_elem is None:
        return None
    data = dict(addr_elem.items())
    return XMLAddrModel.model_validate(data)


def create_addrs_xml_model(addrs_elem: "ET.Element | None") -> list[XMLAddrModel]:
    """Create addr models from `addrs` Element."""
    if addrs_elem is None:
        return []
    result = []
    for elem in addrs_elem:
        model = create_addr_xml_model(elem)
        if model:
            result.append(model)
    return result


def create_sms_xml_model(sms_elem: "ET.Element | None") -> XMLSMSModel | None:
    """Create SMS model from `sms` Element."""
    if sms_elem is None:
        return None
    msg = f"Message data: {sms_elem.items()}"
    logger.debug(msg)
    data = dict(sms_elem.items())
    return XMLSMSModel.model_validate(data)


def create_rcs_mms_xml_model(
    mms_elem: "ET.Element | None",
) -> XMLMMSFullModel | XMLRCSFullModel | None:
    """Create MMS/RCS model from `mms` Element."""
    if mms_elem is None:
        return None
    data: dict[str, Any] = dict(mms_elem.items())
    msg_type = get_message_type_from_element(mms_elem)

    model_cls = XMLMMSFullModel if msg_type == MessageType.MMS else XMLRCSFullModel
    addrs_xml = mms_elem.find("addrs")
    parts_xml = mms_elem.find("parts")
    addrs_model = create_addrs_xml_model(addrs_xml)
    parts_model = create_parts_xml_model(parts_xml)
    data["addrs"] = addrs_model
    data["parts"] = parts_model
    return model_cls.model_validate(data)


def create_message_model(
    message_elem: "ET.Element | None",
) -> XMLMMSFullModel | XMLRCSFullModel | XMLSMSModel | None:
    """Create a message model."""
    if message_elem is None:
        msg = f"No message elem @ `{message_elem}`"
        logger.debug(msg)
        return None
    model_type = get_message_type_from_element(message_elem)
    msg = f"Creating model for type {model_type}"
    logger.debug(msg)
    if model_type == MessageType.SMS:
        return create_sms_xml_model(message_elem)
    return create_rcs_mms_xml_model(message_elem)
