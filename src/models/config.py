"""Config Models."""

from googleapiclient.model import BaseModel

from src.indexes.sms.models import SMSConfig
from src.models.rag import MeilisearchConfig


class ConfigModel(BaseModel):
    """ArcSearch configuration model."""

    meilisearch: MeilisearchConfig
    text_messages: SMSConfig
