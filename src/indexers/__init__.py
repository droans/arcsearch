"""Data parsers."""

import os
from pathlib import Path

import yaml

from src.models.indexers import IndexerManifest
from src.models.indexers.manifest import RegisteredManifest


def get_all_manifests() -> list[RegisteredManifest]:
    """Return a list of all manifests for the indexers."""
    indexers = []
    for indexer_dir, _subdirs, indexer_files in os.walk(__path__[0]):
        if "manifest.yaml" in indexer_files:
            manifest = load_manifest(Path(indexer_dir, "manifest.yaml"))
            module_name = determine_module_name(Path(indexer_dir))
            indexers.append(
                RegisteredManifest(
                    module_path=indexer_dir,
                    module_name=module_name,
                    **manifest.model_dump(),
                ),
            )
    return indexers


def load_manifest(manifest_path: Path) -> IndexerManifest:
    """Load a manifest from the YAML file."""
    assert manifest_path.exists()
    assert manifest_path.is_file()
    assert manifest_path.suffix in (".yaml", ".yml")

    with open(manifest_path) as f:
        raw_manifest = yaml.safe_load(f.read())
    return IndexerManifest.model_validate(raw_manifest)


def determine_module_name(module_path: Path) -> str:
    """Determine the module name for importing."""
    indexers_module = __name__
    indexer_module = module_path.name
    return f"{indexers_module}.{indexer_module}"
