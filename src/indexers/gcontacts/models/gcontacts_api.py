"""Google Contacts API models."""

import datetime
from typing import Annotated, Any

import phonenumbers
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

E164NumberType = Annotated[str | phonenumbers.PhoneNumber, PhoneNumberValidator(number_format="E164")]


class GContactsApiSourceModel(BaseModel):
    """Representation of the source schema for a Google Contacts API response.

    https://developers.google.com/people/api/rest/v1/people#Person.Source
    """

    type: str
    id: str
    etag: str | None = None
    updateTime: datetime.datetime | None = None
    profileMetadata: Any | None = None


class GContactsApiFieldMetadataModel(BaseModel):
    """Representation of the FieldMetadata schema for a Google Contacts API response.

    https://developers.google.com/people/api/rest/v1/people#Person.FieldMetadata
    """

    primary: bool | None = None
    sourcePrimary: bool | None = None
    verified: bool | None = None
    source: GContactsApiSourceModel


class GContactsApiContactGroupMembershipModel(BaseModel):
    """Representation of the ContactGroupMembership schema for a Google Contacts API response.

    https://developers.google.com/people/api/rest/v1/people#Person.ContactGroupMembership
    """

    contactGroupId: str
    contactGroupResourceName: str


class GContactsApiDomainMembershipModel(BaseModel):
    """Representation of the DomainMembership schema for a Google Contacts API response.

    https://developers.google.com/people/api/rest/v1/people#Person.DomainMembership
    """

    inViewerDomain: bool


class GContactsApiBaseModel(BaseModel):
    """Base model for a single contact's data."""

    resourceName: str
    etag: str


class GContactsApiEmailAddressStubModel(BaseModel):
    """Stub model for the response of a single contact's email address pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.EmailAddress
    """

    metadata: GContactsApiFieldMetadataModel
    value: str
    type: str | None = None
    formattedType: str | None = None
    displayName: str | None = None


class GContactsApiEmailAddressModel(GContactsApiBaseModel):
    """Model for the response of a single contact's email address pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.EmailAddress
    """

    emailAddresses: list[GContactsApiEmailAddressStubModel]


class GContactsApiMembershipStubModel(BaseModel):
    """Stub model for the response of a single contact's membership pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Membership
    """

    metadata: GContactsApiFieldMetadataModel
    contactGroupMembership: GContactsApiContactGroupMembershipModel
    domainMembership: GContactsApiDomainMembershipModel | None = None


class GContactsApiMembershipModel(GContactsApiBaseModel):
    """Model for the response of a single contact's membership pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Membership
    """

    memberships: list[GContactsApiMembershipStubModel]


class GContactsApiPersonMetadataStubModel(BaseModel):
    """Stub model for the response of a single contact's metadata pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Name
    """

    sources: list[GContactsApiSourceModel]
    previousResourceNames: list[str] | None = None
    linkedPeopleResourceNames: list[str] | None = None
    deleted: bool | None = False
    objectType: str | None = None


class GContactsApiPersonMetadataModel(GContactsApiBaseModel):
    """Model for the response of a single contact's metadata pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Name
    """

    metadata: GContactsApiPersonMetadataStubModel


class GContactsApiNameStubModel(BaseModel):
    """Stub model for the response of a single contact's name pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Name
    """

    metadata: GContactsApiFieldMetadataModel
    displayName: str
    displayNameLastFirst: str
    unstructuredName: str
    familyName: str | None = None
    givenName: str | None = None
    middleName: str | None = None
    honorificPrefix: str | None = None
    honorificSuffix: str | None = None
    phoneticFullName: str | None = None
    phoneticFamilyName: str | None = None
    phoneticGivenName: str | None = None
    phoneticMiddleName: str | None = None
    phoneticHonorificPrefix: str | None = None
    phoneticHonorificSuffix: str | None = None


class GContactsApiNameModel(GContactsApiBaseModel):
    """Model for the response of a single contact's name pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Name
    """

    names: list[GContactsApiNameStubModel]


class GContactsApiNicknameStubModel(BaseModel):
    """Stub model for the response of a single contact's nick name pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Nickname
    """

    metadata: GContactsApiFieldMetadataModel
    value: str
    type: str | None = None


class GContactsApiNicknameModel(GContactsApiBaseModel):
    """Model for the response of a single contact's nick name pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Nickname
    """

    nicknames: list[GContactsApiNicknameStubModel]


class GContactsApiPhoneNumberStubModel(BaseModel):
    """Stub model for the response of a single contact's phone number pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.PhoneNumber
    """

    metadata: GContactsApiFieldMetadataModel
    value: str
    canonicalForm: E164NumberType | None = None
    type: str
    formattedType: str


class GContactsApiPhoneNumberModel(GContactsApiBaseModel):
    """Model for the response of a single contact's phone number pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.PhoneNumber
    """

    phoneNumbers: list[GContactsApiPhoneNumberStubModel]


class GContactsApiPhotoStubModel(BaseModel):
    """Stub model for the response of a single contact's photo pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Photo
    """

    metadata: GContactsApiFieldMetadataModel
    url: str
    default: bool | None = None


class GContactsApiPhotoModel(GContactsApiBaseModel):
    """Model for the response of a single contact's photo pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Photo
    """

    photos: list[GContactsApiPhotoStubModel]


class GContactsApiURLStubModel(BaseModel):
    """Stub model for the response of a single contact's URL pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Url
    """

    metadata: GContactsApiFieldMetadataModel
    value: str
    type: str
    formattedType: str


class GContactsApiURLModel(GContactsApiBaseModel):
    """Model for the response of a single contact's URL pulled from the GContacts API.

    https://developers.google.com/people/api/rest/v1/people#Person.Url
    """

    urls: list[GContactsApiURLStubModel]


class GContactsApiAnyConnectionsModel(GContactsApiBaseModel):
    """Model for the connections response of any field from single contact pulled from the GContacts API."""

    emailAddresses: list[GContactsApiEmailAddressStubModel] = []
    memberships: list[GContactsApiMembershipStubModel] = []
    names: list[GContactsApiNameStubModel] = []
    nicknames: list[GContactsApiNicknameStubModel] = []
    phoneNumbers: list[GContactsApiPhoneNumberStubModel] = []
    photos: list[GContactsApiPhotoStubModel] = []
    urls: list[GContactsApiURLStubModel] = []


class GContactsApiAnyModel(BaseModel):
    """Model for the response of any field from single contact pulled from the GContacts API."""

    connections: list[GContactsApiAnyConnectionsModel]
    nextPageToken: str | None = None
    totalPeople: int
    totalItems: int
