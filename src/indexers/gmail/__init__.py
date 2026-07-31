"""Email indexer functions."""

from src.indexers.gmail.gmail_email import GmailEmailIndexer
from src.indexers.gmail.models import EmailFilter, GMailConfig
from src.models.indexers import AddDocumentsKwargField, IndexerRegistryEntry
from src.util.indexers import load_index_manifest


def register_indexer() -> IndexerRegistryEntry:
    """Register index."""
    manifest = load_index_manifest("manifest.yaml")

    add_documents_kwargs = {
        "account_names": AddDocumentsKwargField(
            type=str | list[str] | None,
            example_value="myemail@gmail.com",
            description="Accounts to select for processing.",
        ),
        "filters": AddDocumentsKwargField(
            type=list[EmailFilter] | None,
            example_value="myemail@gmail.com",
            description="Filters to apply to processing.",
        ),
        "reprocess": AddDocumentsKwargField(
            type=bool,
            example_value=False,
            default_value=False,
            description="Process all emails, including those from previous passes.",
        ),
    }
    return IndexerRegistryEntry(
        manifest=manifest,
        indexer_class=GmailEmailIndexer,
        add_documents_kwargs=add_documents_kwargs,
        config_schema=GMailConfig,
    )
