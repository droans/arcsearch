"""Functions related to contacts."""

import json
import logging
from pathlib import Path

import vobject

from .models import ContactInfo

logger = logging.getLogger(__name__)


def parse_contacts(file_path: str | Path) -> list[ContactInfo]:
    """Return all contacts."""
    with open(file_path) as f:
        data = f.read()

    vcard_contacts = vobject.readComponents(data)
    unique_numbers = set()
    contacts = []

    for contact in vcard_contacts:
        contents = contact.contents
        name = contents.get("fn", [None])[0]
        if name:
            name = name.value
        phone_numbers = contents.get("tel", [])
        if not name:
            msg = f"Skipping {phone_numbers} because no name provided."
            logger.info(msg)
            continue
        if not phone_numbers:
            msg = f"Skipping {name} because no phone number provided."
            logger.info(msg)
            continue
        for phone_number in phone_numbers:
            _number = phone_number.value[-12:]
            if _number in unique_numbers:
                msg = f"Skipping duplicate {_number} ({phone_number}) with name {name}."
                logger.info(msg)
                continue
            unique_numbers.add(_number)
            contacts.append(ContactInfo(name=name, phone_number=_number))
    return contacts


def export_contacts(vcard_path: str | Path, export_path: str | Path) -> None:
    """Export all contacts from a Google Contacts VCArd file."""
    logger.info("Exporting contacts")
    contacts = parse_contacts(vcard_path)
    dumped = [contact.model_dump() for contact in contacts]
    with open(export_path, "w") as f:
        f.write(json.dumps(dumped, indent=4))
    logger.info("Contacts exported.")
