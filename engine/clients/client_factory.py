from abc import ABC
from typing import List, Type

from engine.base_client.client import (
    BaseClient,
    BaseConfigurator,
    BaseSearcher,
    BaseUploader,
)
from engine.clients.elasticsearch.configure import ElasticConfigurator
from engine.clients.elasticsearch.search import ElasticSearcher
from engine.clients.elasticsearch.upload import ElasticUploader
from engine.clients.milvus import MilvusConfigurator, MilvusSearcher, MilvusUploader
from engine.clients.opensearch.configure import OpenSearchConfigurator
from engine.clients.opensearch.search import OpenSearchSearcher
from engine.clients.opensearch.upload import OpenSearchUploader
from engine.clients.qdrant import QdrantConfigurator, QdrantSearcher, QdrantUploader
from engine.clients.redis.configure import RedisConfigurator
from engine.clients.redis.search import RedisSearcher
from engine.clients.redis.upload import RedisUploader
from engine.clients.weaviate import (
    WeaviateConfigurator,
    WeaviateSearcher,
    WeaviateUploader,
)

ENGINE_CONFIGURATORS = {
    "qdrant": QdrantConfigurator,
    "weaviate": WeaviateConfigurator,
    "milvus": MilvusConfigurator,
    "elastic": ElasticConfigurator,
    "opensearch": OpenSearchConfigurator,
    "redis": RedisConfigurator,
}

ENGINE_UPLOADERS = {
    "qdrant": QdrantUploader,
    "weaviate": WeaviateUploader,
    "milvus": MilvusUploader,
    "elastic": ElasticUploader,
    "opensearch": OpenSearchUploader,
    "redis": RedisUploader,
}

ENGINE_SEARCHERS = {
    "qdrant": QdrantSearcher,
    "weaviate": WeaviateSearcher,
    "milvus": MilvusSearcher,
    "elastic": ElasticSearcher,
    "opensearch": OpenSearchSearcher,
    "redis": RedisSearcher,
}


class ClientFactory(ABC):
    def __init__(self, host):
        self.host = host

    def _create_configurator(self, experiment) -> BaseConfigurator:
        engine_configurator_class = ENGINE_CONFIGURATORS[experiment["engine"]]
        engine_configurator = engine_configurator_class(
            self.host,
            collection_params={**experiment.get("collection_params", {})},
            connection_params={**experiment.get("connection_params", {})},
        )
        return engine_configurator

    def _create_uploader(self, experiment) -> BaseUploader:
        engine_uploader_class = ENGINE_UPLOADERS[experiment["engine"]]
        engine_uploader = engine_uploader_class(
            self.host,
            connection_params={**experiment.get("connection_params", {})},
            upload_params={**experiment.get("upload_params", {})},
        )
        return engine_uploader

    def _create_searchers(self, experiment) -> List[BaseSearcher]:
        engine_searcher_class: Type[BaseSearcher] = ENGINE_SEARCHERS[
            experiment["engine"]
        ]

        engine_searchers = [
            engine_searcher_class(
                self.host,
                connection_params={**experiment.get("connection_params", {})},
                search_params=search_params,
            )
            for search_params in experiment.get("search_params", [{}])
        ]

        return engine_searchers

    def build_client(self, experiment):
        return BaseClient(
            name=experiment["name"],
            configurator=self._create_configurator(experiment),
            uploader=self._create_uploader(experiment),
            searchers=self._create_searchers(experiment),
        )
