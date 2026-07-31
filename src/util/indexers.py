"""Utility functions for indexers."""

from pathlib import Path

from src.models.indexers import IndexerManifest


def load_index_manifest(manifest_path: Path | str) -> IndexerManifest:
    """Load an index manifest."""
    with open(manifest_path) as f:
        data = f.read()
    return IndexerManifest.model_validate_json(data)
