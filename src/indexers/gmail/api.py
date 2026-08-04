"""API Endpoints for the GMail indexer."""

from fastapi import APIRouter
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient._apis.gmail.v1.resources import GmailResource
from googleapiclient.discovery import build

from src.indexers.gmail.models import GMailAccountConfig, GMailConfig
from src.indexers.gmail.process_email import fetch_attachment
from src.models.arcsearch import AppModel, RuntimeData
from src.util.indexers import save_attachment


class GMailIndexerApi:
    """API Client for the GMail Indexer."""

    def __init__(
        self,
        app: AppModel,
        runtime_data: RuntimeData,
    ) -> None:
        """Initialize class."""
        self.app = app
        self.runtime_data = runtime_data
        self.router = APIRouter(
            prefix="/gmail",
            tags=["gmail"],
        )

    def _create_client(self, account_name: str) -> GmailResource | None:
        """Create client for account."""
        account = self.get_account_by_name(account_name)
        if not account:
            return None
        creds = Credentials.from_authorized_user_file(filename=account.credentials_path)
        if creds.expired:
            creds.refresh(Request())

        return build(
            serviceName="gmail",
            version="v1",
            credentials=creds,
        )

    def get_account_by_name(self, account_name: str) -> GMailAccountConfig | None:
        """Get an account by the account name."""
        assert isinstance(self.runtime_data.config, GMailConfig)
        accounts = self.runtime_data.config.accounts
        for account in accounts:
            if account.account_name == account_name:
                return account
        return None

    def setup_api(self) -> None:
        """Setup API endpoints."""
        self.router.add_api_route(
            "/attachments/get_url",
            self.get_or_create_attachment_url,
            methods=["POST"],
        )

    def get_or_create_attachment_url(
        self,
        account_name: str,
        message_id: str,
        attachment_id: str,
    ) -> str:
        """Gets or creates the URL for an attachment."""
        client = self._create_client(account_name=account_name)
        assert client
        attachment = fetch_attachment(
            client=client,
            message_id=message_id,
            attachment_id=attachment_id,
        )
        saved_file = save_attachment(unique_id=attachment_id, data=attachment)
        return saved_file.src
