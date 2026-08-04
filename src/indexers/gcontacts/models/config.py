"""Config models for Google Contacts."""

from typing import Literal

from pydantic import BaseModel, FilePath

from src.const import DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES, DEFAULT_PROCESS_CONTENT_TYPES
from src.models.indexers import BaseIndexerConfigModel


class GoogleContactsAccountConfig(BaseModel):
    """Config model for a single account."""

    credentials_path: FilePath
    account_name: str


class GoogleContactsConfigModel(BaseIndexerConfigModel):
    """Config model for Google Contacts indexer."""

    type: Literal["google_contacts"]
    accounts: list[GoogleContactsAccountConfig]
    save_attachment_types: list[str] = DEFAULT_PROCESS_CONTENT_TYPES
    save_attachment_type_prefixes: list[str] = DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES
