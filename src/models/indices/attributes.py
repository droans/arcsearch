"""Index setup attributes config."""

from typing import Literal

from pydantic import BaseModel


class FilterableAttributesConfig(BaseModel):
    """Advanced configuration for filterable attributes."""

    attribute_patterns: list[str]
    enable_facet_search: bool | None = None
    enable_equality_filter: bool | None = None
    enable_comparison_filter: bool | None = None
    max_values_per_facet: int | None = None
    sort_facet_values_by: dict[str, Literal["alpha", "count"]] | None = None


class IndexAttributesConfig(BaseModel):
    """Config for index attributes."""

    # Attributes that can be filtered.
    filterable_attributes: list[str] | None = None

    # Attributes that can be checked.
    searchable_attributes: list[str] | None = None

    # Attributes that can be sorted.
    sortable_attributes: list[str] | None = None

    # Attributes that can be returned.
    displayed_attributes: list[str] | None = None

    # When set, if multiple items share the same distinct attribute,
    #  only one of them will be returned.
    distinct_attribute: str | None = None


class IndexAttributesForeignKeyConfig(BaseModel):
    """Config for foreign key settings for an index."""

    foreign_key_uid: str
    field_name: str
