"""Utility functions for indexers."""

import os
from pathlib import Path

import magic

from src.const import ATTACHMENT_ENDPOINT, SAVE_FILE_PATH
from src.models.arcsearch import IndexFileModel
from src.models.indexers import IndexerManifest


def load_index_manifest(manifest_path: Path | str) -> IndexerManifest:
    """Load an index manifest."""
    with open(manifest_path) as f:
        data = f.read()
    return IndexerManifest.model_validate_json(data)


def attachment_exists(file_name: str) -> bool | IndexFileModel:
    """Check if attachment already exists."""
    files = os.listdir(SAVE_FILE_PATH)  # noqa: PTH208
    fp = Path(file_name)
    if not fp.suffix:
        split_files = (file.split(".") for file in files)
        return any(file for file in split_files if file[0] == file_name)
    return any(file for file in files if file == file_name)


def save_attachment(unique_id: str, data: str | bytes) -> IndexFileModel:
    """Save down a single attachment."""
    content_type = magic.from_buffer(data)
    mime = magic.from_buffer(data, mime=True)
    suffix = mime.split("/")[-1]
    fname = f"{unique_id}.{suffix}"
    if not SAVE_FILE_PATH.exists():
        SAVE_FILE_PATH.mkdir()
    file_path = SAVE_FILE_PATH.joinpath(fname)
    if not file_path.exists():
        open_mode = "wb" if isinstance(data, bytes) else "w"
        with open(fname, open_mode) as f:
            f.write(data)
    return IndexFileModel(
        file_name=fname,
        content_type=content_type,
        src=f"{ATTACHMENT_ENDPOINT}/{fname}",
    )
