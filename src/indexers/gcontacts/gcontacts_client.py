"""Google Contacts API Client."""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient._apis.people.v1.resources import PeopleServiceResource
from googleapiclient.discovery import build

from src.indexers.gcontacts.const import (
    FIELD_EMAIL_ADDRESSES,
    FIELD_NAMES,
    FIELD_NICKNAMES,
    FIELD_NONE,
    FIELD_PHONE_NUMBERS,
    FIELD_PHOTOS,
    FIELD_URLS,
)
from src.indexers.gcontacts.models.config import GoogleContactsAccountConfig, GoogleContactsConfigModel
from src.indexers.gcontacts.models.gcontacts_api import GContactsApiAnyConnectionsModel, GContactsApiAnyModel
from src.indexers.gcontacts.models.gcontacts_internal import (
    GoogleContactEmailAddressModel,
    GoogleContactModel,
    GoogleContactNameModel,
    GoogleContactNicknameModel,
    GoogleContactPhoneNumberModel,
    GoogleContactPhotoModel,
    GoogleContactURLModel,
)
from src.models.arcsearch import AppModel, RuntimeData


class GoogleContactsAPIClient:
    """API Client for Google Contacts."""

    def __init__(
        self,
        app: AppModel,
        runtime_data: RuntimeData,
    ) -> None:
        """Initialize class."""
        self.app = app
        self.runtime_data = runtime_data

    def _create_client(self, account_name: str) -> PeopleServiceResource | None:
        """Create client for account."""
        account = self.get_account_by_name(account_name=account_name)
        if not account:
            return None
        creds = Credentials.from_authorized_user_file(filename=account.credentials_path)
        if creds.expired:
            creds.refresh(Request())
            with open(account.credentials_path, "w") as f:
                f.write(creds.to_json())
        return build(
            serviceName="people",
            version="v1",
            credentials=creds,
        )

    def get_account_by_name(self, account_name: str) -> GoogleContactsAccountConfig | None:
        """Get an account by the account name."""
        assert isinstance(self.runtime_data.config, GoogleContactsConfigModel)
        accounts = self.runtime_data.config.accounts
        for account in accounts:
            if account.account_name == account_name:
                return account
        return None

    def get_contacts_page(
        self,
        client: PeopleServiceResource,
        field: str,
        page_token: str | None = None,
    ) -> GContactsApiAnyModel:
        """Return a single page of data for a single field."""
        response = (
            client.people()
            .connections()
            .list(
                resourceName="people/me",
                personFields=field,
                pageToken=page_token,
            )
            .execute()
        )
        return GContactsApiAnyModel.model_validate(response)

    def get_all_contacts_for_field(
        self,
        client: PeopleServiceResource,
        field: str,
    ) -> list[GContactsApiAnyConnectionsModel]:
        """Get all contacts for a single field."""
        next_page_token = None
        result: list[GContactsApiAnyConnectionsModel] = []
        while True:
            tmp = self.get_contacts_page(
                client=client,
                field=field,
                page_token=next_page_token,
            )
            result.extend(tmp.connections)
            next_page_token = tmp.nextPageToken
            if not next_page_token:
                break
        return result

    def get_all_contacts_for_account(self, account_name: str) -> list[GoogleContactModel]:
        """Return the base contacts model for all contacts with an account."""
        client = self._create_client(account_name)
        assert client
        all_contacts = self.get_all_contacts_for_field(
            client=client,
            field=FIELD_NONE,
        )
        return [
            GoogleContactModel(account_name=account_name, resource_name=contact.resourceName)
            for contact in all_contacts
        ]

    def get_all_contact_email_addresses_for_account(self, account_name: str) -> list[GoogleContactEmailAddressModel]:
        """Get all contact email addresses for an account."""
        client = self._create_client(account_name=account_name)
        assert client
        all_contacts = self.get_all_contacts_for_field(
            client=client,
            field=FIELD_EMAIL_ADDRESSES,
        )
        result = []
        for contact in all_contacts:
            resource_name = contact.resourceName
            addrs = contact.emailAddresses
            for addr in addrs:
                source_id = addr.metadata.source.id
                address = addr.value
                addr_type = addr.type
                result.append(
                    GoogleContactEmailAddressModel(
                        resource_name=resource_name,
                        unique_id=source_id,
                        value=address,
                        type=addr_type,
                    ),
                )
        return result

    def get_all_contact_phone_numbers_for_account(self, account_name: str) -> list[GoogleContactPhoneNumberModel]:
        """Get all contact phone numbers for an account."""
        client = self._create_client(account_name=account_name)
        assert client
        all_contacts = self.get_all_contacts_for_field(
            client=client,
            field=FIELD_PHONE_NUMBERS,
        )
        result = []
        for contact in all_contacts:
            resource_name = contact.resourceName
            phone_numbers = contact.phoneNumbers
            for phone_number in phone_numbers:
                number = phone_number.value
                canonical = phone_number.canonicalForm
                num_type = phone_number.type
                unique_id = phone_number.metadata.source.id
                result.append(
                    GoogleContactPhoneNumberModel(
                        unique_id=unique_id,
                        resource_name=resource_name,
                        value=number,
                        canonical=canonical,
                        type=num_type,
                    ),
                )
        return result

    def get_all_contact_names_for_account(self, account_name: str) -> list[GoogleContactNameModel]:
        """Get all contact names for an account."""
        client = self._create_client(account_name=account_name)
        assert client
        all_contacts = self.get_all_contacts_for_field(
            client=client,
            field=FIELD_NAMES,
        )
        result = []
        for contact in all_contacts:
            resource_name = contact.resourceName
            names = contact.names
            for name in names:
                unique_id = name.metadata.source.id
                result.append(
                    GoogleContactNameModel(
                        resource_name=resource_name,
                        unique_id=unique_id,
                        display_name=name.displayName,
                        family_name=name.familyName,
                        given_name=name.givenName,
                        last_first_name=name.displayNameLastFirst,
                        unstructured_name=name.unstructuredName,
                    ),
                )
        return result

    def get_all_contact_nicknames_for_account(self, account_name: str) -> list[GoogleContactNicknameModel]:
        """Get all contact nicknames for an account."""
        client = self._create_client(account_name=account_name)
        assert client
        all_contacts = self.get_all_contacts_for_field(
            client=client,
            field=FIELD_NICKNAMES,
        )
        result = []
        for contact in all_contacts:
            resource_name = contact.resourceName
            for nickname in contact.nicknames:
                unique_id = nickname.metadata.source.id
                result.append(
                    GoogleContactNicknameModel(
                        resource_name=resource_name,
                        unique_id=unique_id,
                        nickname=nickname.value,
                    ),
                )
        return result

    def get_all_contact_photos_for_account(self, account_name: str) -> list[GoogleContactPhotoModel]:
        """Get all contact photos for an account."""
        client = self._create_client(account_name=account_name)
        assert client
        all_contacts = self.get_all_contacts_for_field(
            client=client,
            field=FIELD_PHOTOS,
        )
        result = []
        for contact in all_contacts:
            resource_name = contact.resourceName
            for photo in contact.photos:
                unique_id = photo.metadata.source.id
                result.append(
                    GoogleContactPhotoModel(
                        resource_name=resource_name,
                        unique_id=unique_id,
                        url=photo.url,
                        default=photo.default or False,
                    ),
                )
        return result

    def get_all_contact_urls_for_account(self, account_name: str) -> list[GoogleContactURLModel]:
        """Get all contact URLs for an account."""
        client = self._create_client(account_name=account_name)
        assert client
        all_contacts = self.get_all_contacts_for_field(
            client=client,
            field=FIELD_URLS,
        )
        result = []
        for contact in all_contacts:
            resource_name = contact.resourceName
            for url in contact.urls:
                unique_id = url.metadata.source.id
                result.append(
                    GoogleContactURLModel(
                        resource_name=resource_name,
                        unique_id=unique_id,
                        value=url.value,
                        type=url.type,
                    ),
                )
        return result
