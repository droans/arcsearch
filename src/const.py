"""Constants."""

from enum import StrEnum
from pathlib import Path

CONFIG_PATH = Path(".", "config.yaml")
BASE_DATA_DIR = Path("data")
SAVE_FILE_DIR = BASE_DATA_DIR.joinpath("files")

DEFAULT_PROCESS_CONTENT_TYPES = []
DEFAULT_PROCESS_CONTENT_TYPE_PREFIXES = [
    "image",
    "text",
    "video",
    "audio",
]

DEFAULT_STOP_WORDS = [
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
]


class IndexerRegistrationStatus(StrEnum):
    """Registration statuses."""

    NOT_LOADED = "not_loaded"
    IN_PROGRESS = "in_progress"
    SETUP_ERROR = "setup_error"
    LOADED = "loaded"


class IndexSetupStatus(StrEnum):
    """Status for setting up an index."""

    OK = "ok"
    ALREADY_EXISTS = "already_exists"
    INVALID_INDEX_PREFIX_FOR_DOMAIN = "invalid_index_prefix_for_domain"


class IndexEmbedderSetupStatus(StrEnum):
    """Status for setting up an index embedder."""

    OK = "ok"
    ALREADY_SETUP = "already_setup"
    INVALID_INDEX_PREFIX_FOR_DOMAIN = "invalid_index_prefix_for_domain"
