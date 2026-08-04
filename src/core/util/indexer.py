"""Indexer utility functions."""

from typing import TYPE_CHECKING

from meilisearch.models.embedders import RestEmbedder

from src.models.rag import EmbedderSettings
from src.util.meilisearch import index_exists

if TYPE_CHECKING:
    from meilisearch import Client


def get_configs_for_index_embedders(
    client: "Client",
    index_uid: str,
) -> list[EmbedderSettings] | None:
    """Generate an EmbedderSettings model from existing embedding config if present."""
    assert index_exists(client=client, index_uid=index_uid)
    idx = client.index(index_uid)
    settings = idx.get_settings()
    embed_conf = settings.get("embedders")
    if not embed_conf or not isinstance(embed_conf, dict):
        return None
    result = []
    for k, v in embed_conf.items():
        assert isinstance(k, str)
        assert isinstance(v, RestEmbedder)
        result.append(_generate_embedder_settings_for_indexer(embedder_name=k, embedder_settings=v))
    return result


def _generate_embedder_settings_for_indexer(embedder_name: str, embedder_settings: RestEmbedder) -> EmbedderSettings:
    """Generate the embedder settings model from a RestEmbedder config."""
    return EmbedderSettings(
        model_name=embedder_name,
        url=embedder_settings.url,
        api_key=embedder_settings.api_key,
        dimensions=embedder_settings.dimensions or 0,
        request=embedder_settings.request,
        response=embedder_settings.response,
        document_template=embedder_settings.document_template,
    )


def compare_embedder_settings(
    embedder_settings: EmbedderSettings,
    compare_settings: EmbedderSettings,
    compare_key: bool = False,
    compare_request: bool = True,
    compare_response: bool = True,
) -> bool:
    """Compare two embedder settings."""
    name_match = embedder_settings.model_name == compare_settings.model_name
    url_match = embedder_settings.model_name == compare_settings.model_name
    api_key_match = embedder_settings.model_name == compare_settings.model_name
    dim_match = embedder_settings.model_name == compare_settings.model_name
    request_match = embedder_settings.model_name == compare_settings.model_name
    response_match = embedder_settings.model_name == compare_settings.model_name
    template_match = embedder_settings.model_name == compare_settings.model_name

    result = name_match and url_match and dim_match and template_match
    if compare_key:
        result = result and api_key_match
    if compare_request:
        result = result and request_match
    if compare_response:
        result = result and response_match
    return result
