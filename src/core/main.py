"""ArcSearch."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn import Config, Server

from src.const import ATTACHMENT_ENDPOINT, SAVE_FILE_PATH
from src.core.registry.indexer import IndexerRegistry
from src.models import ConfigModel
from src.models.arcsearch import AppModel
from src.models.indexers import BaseIndexerConfigModel
from src.util.arcsearch import load_config
from src.util.meilisearch import create_client_from_config


class ArcSearch:
    """ArcSearch main class."""

    def __init__(
        self,
        fastapi_app: "FastAPI",
        config: ConfigModel,
    ) -> None:
        """Initialize class."""
        meilisearch_client = create_client_from_config(config.meilisearch)
        self.app = AppModel(
            fastapi_app=fastapi_app,
            config=config,
            meilisearch_client=meilisearch_client,
        )
        self._indexer_registry = IndexerRegistry(app=self.app)

    def start(self) -> None:
        """Start ArcSearch."""
        self._indexer_registry.register_manifests()
        self.setup_indexers()
        app = self.app.fastapi_app
        api_conf = self.app.config.api
        loop = asyncio.new_event_loop()
        uvicorn_config = Config(
            loop=loop,  # ty: ignore[invalid-argument-type]
            app=app,
            host=api_conf.host,
            port=api_conf.port,
        )
        server = Server(config=uvicorn_config)
        app.mount(
            path=ATTACHMENT_ENDPOINT,
            app=StaticFiles(directory=SAVE_FILE_PATH),
        )
        loop.run_until_complete(server.serve())

    def setup_indexers(self) -> None:
        """Setup all indexers."""
        indexers = self.app.config.indexers
        for indexer in indexers:
            self.setup_indexer(indexer_config=indexer)

    def setup_indexer(self, indexer_config: BaseIndexerConfigModel) -> None:
        """Setup a single indexer."""
        self._indexer_registry.setup_indexer(indexer_config=indexer_config)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, ARG001
    """Tasks run before/after setup."""
    yield


def serve_arcsearch() -> None:
    """Main function."""
    config = load_config()
    fastapi_app = FastAPI(lifespan=lifespan)
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    arcsearch = ArcSearch(fastapi_app=fastapi_app, config=config)
    arcsearch.start()
