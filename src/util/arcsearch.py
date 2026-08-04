"""ArcSearch utility functions."""

import yaml

from src.const import CONFIG_PATH
from src.models import ConfigModel


def load_config() -> ConfigModel:
    """Load the ArcSearch config."""
    with open(CONFIG_PATH) as f:
        loaded = yaml.safe_load(f)
    return ConfigModel.model_validate(loaded)
