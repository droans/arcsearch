"""Internal models."""

from pydantic import BaseModel

from src.indexers.gcontacts.models.gcontacts_api import E164NumberType


class GoogleContactModel(BaseModel):
    """Model for a single contact."""

    account_name: str
    resource_name: str


class GoogleContactEmailAddressModel(BaseModel):
    """Model for a Google Contact email address record."""

    resource_name: str
    unique_id: str
    value: str
    type: str | None = None


class GoogleContactNameModel(BaseModel):
    """Model for a Google Contact name record."""

    resource_name: str
    unique_id: str
    display_name: str
    family_name: str | None = None
    given_name: str | None = None
    last_first_name: str
    unstructured_name: str


class GoogleContactNicknameModel(BaseModel):
    """Model for a Google Contact nickname record."""

    resource_name: str
    unique_id: str
    nickname: str


class GoogleContactPhoneNumberModel(BaseModel):
    """Model for a Google Contact phone number record."""

    resource_name: str
    unique_id: str
    value: str
    canonical: E164NumberType | None = None
    type: str


class GoogleContactPhotoModel(BaseModel):
    """Model for a Google Contact photo record."""

    resource_name: str
    unique_id: str
    url: str
    default: bool = False


class GoogleContactURLModel(BaseModel):
    """Model for a Google Contact URL record."""

    resource_name: str
    unique_id: str
    value: str
    type: str
