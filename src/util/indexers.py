"""Utility functions for indexers."""

import uuid
from pathlib import Path

import magic

from src.models.arcsearch import IndexFileModel
from src.models.indexers import IndexerManifest


def load_index_manifest(manifest_path: Path | str) -> IndexerManifest:
    """Load an index manifest."""
    with open(manifest_path) as f:
        data = f.read()
    return IndexerManifest.model_validate_json(data)


def save_file(original_file_name: str | Path, data: str | bytes) -> IndexFileModel:
    """Save down a single file."""
    if not isinstance(original_file_name, Path):
        original_file_name = Path(original_file_name)
    suffix = original_file_name.suffix
    content_type = magic.from_buffer(data)
    if not suffix:
        mime = magic.from_buffer(data, mime=True)
        suffix = mime.split("/")[-1]
    fname = f"{uuid.uuid4()}.{suffix}"

    open_mode = "wb" if isinstance(data, bytes) else "w"
    with open(fname, open_mode) as f:
        f.write(data)

    return IndexFileModel(
        file_name=fname,
        content_type=content_type,
        src=fname,
    )
