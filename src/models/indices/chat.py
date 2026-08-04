"""Index setup chat config model."""

from typing import Literal

from pydantic import BaseModel, Field


class IndexChatSearchParametersConfig(BaseModel):
    """Model for search parameters."""

    semantic_ratio: float | None = None
    limit: int | None = None
    sort: list[str]
    distinct: list[str]
    matching_strategy: Literal["last", "all", "frequency"] | None = None
    search_attributes: list[str] | None
    ranking_score_threshold: float | None = Field(default=None, ge=0, le=1)


class IndexChatConfig(BaseModel):
    """Model for the chat config for an index."""

    description: str
    default_document_template: str | None = None
    search_parameters: IndexChatSearchParametersConfig | None = None
