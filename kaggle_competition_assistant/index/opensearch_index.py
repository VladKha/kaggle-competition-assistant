import os
import random
import string
from typing import Literal, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk
from tqdm.auto import tqdm

from .embedders import Embedder
from .index_base import IndexBase
from ..logger import get_logger

logger = get_logger(__name__)


OPENSEARCH_HOST = os.environ.get('OPENSEARCH_HOST', 'localhost')
OPENSEARCH_PORT = os.environ.get('OPENSEARCH_PORT', 9200)
OPENSEARCH_USER = os.environ.get('OPENSEARCH_USER', 'admin')
OPENSEARCH_PASSWORD = os.environ.get('OPENSEARCH_PASSWORD', 'admin')


def generate_index_name(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def compute_rrf(rank, k=60):
    """Implementation of Reciprocal rank fusion score."""
    return 1 / (k + rank)

class OpenSearchIndex(IndexBase):
    def __init__(self, text_fields: list[str], keyword_fields: list[str],
                 index_name: Optional[str] = None,
                 host: str = OPENSEARCH_HOST, port: int = OPENSEARCH_PORT,
                 user: str = OPENSEARCH_USER, password: str = OPENSEARCH_PASSWORD,
                 embedder_model_name: Optional[str] = None,
                 embedder_device: Optional[str] = None, **kwargs):
        super().__init__(text_fields, keyword_fields, **kwargs)

        if index_name is None:
            index_name = generate_index_name(20)
        self.index_name = index_name
        self._client = self._get_opensearch(host, port, user, password)

        self._embedder = Embedder(model_name=embedder_model_name, device=embedder_device)
        self._create_index()

    def _get_opensearch(self, host: str, port: int,
                        user: str, password: str) -> OpenSearch:
        """
        Creates an OpenSearch client.

        Args:
            host: Name of OpenSearch host
            port: Port number to use for OpenSearch connection
            user: Username to use for OpenSearch connection
            password: Password to use for OpenSearch connection

        Returns:
            OpenSearch client
        """
        return OpenSearch(
            hosts=[{"host": host, "port": port}],
            connection_class=RequestsHttpConnection,
            http_compress=True,
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

    def _create_index(self) -> None:
        """Create OpenSearch index"""
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "index.knn": True
            },
            "mappings": {
                "properties": {
                    **{f: {"type": "text"} for f in self.text_fields},
                    **{f: {"type": "keyword"} for f in self.keyword_fields},
                    **{'doc_embedding':
                           {
                               'type': 'knn_vector',
                               'dimension': self._embedder.embedding_size,
                               'similarity': 'cosine'
                           }
                    }
                }
            }
        }

        self._client.indices.delete(index=self.index_name, ignore_unavailable=True)
        self._client.indices.create(index=self.index_name, body=index_settings)


    def index(self, documents: list[dict]) -> None:
        """
        Indexes the given list of documents into the OpenSearch index.

        Args:
            documents (list[dict]): List of documents to index. Each document is a dictionary.

        Returns:
            None
        """
        docs_to_index = []

        # embed documents
        batch_size = 32
        i = 0
        pbar = tqdm(range(0, len(documents)), total=len(documents), desc="Creating document embeddings")
        while i < len(documents):
            batch_docs = documents[i:i+batch_size]
            batch_texts = []
            for d in batch_docs:
                d = d.copy()
                doc_s = ''
                if d['source']:
                    doc_s += f'source: {d["source"]}\n'
                if d['section']:
                    doc_s += f'section: {d["section"]}\n'
                if d['text']:
                    doc_s += f'text: \n{d["text"]}'

                batch_texts.append(doc_s)

            embeddings = self._embedder.embed(batch_texts)

            for d, embedding in zip(batch_docs, embeddings):
                d['doc_embedding'] = embedding
                d['_index'] = self.index_name
                docs_to_index.append(d)

            i += batch_size
            pbar.update(batch_size)

        # index docs in OpenSearch
        bulk(self._client, docs_to_index, index=self.index_name)
        self._client.indices.refresh(index=self.index_name)

    def search(self, query: str, filter_dict: dict = {}, boost_dict: dict[str, float] = {}, num_results: int = 5,
               search_type: Literal['lexical', 'semantic', 'hybrid_rff'] = 'hybrid_rff',
               hybrid_rff_k: int = 60,
               **kwargs) -> list[dict]:
        """
        Searches the index with the given query, filters, and boost parameters.

        Args:
            query (str): The search query string.
            filter_dict (dict): Dictionary of keyword fields to filter by.
                                Keys are field names and values are the values to filter by.
            boost_dict (dict[str, float]): Dictionary of boost scores for text fields.
                                Keys are field names and values are the boost scores.
            num_results (int): The number of top results to return. Defaults to 10.
            search_type (Literal['lexical', 'semantic', 'hybrid_rff']): The type of search to perform.
                                Defaults to 'lexical'.
            hybrid_rff_k (int): The constant k for reciprocal rank fusion formula
                                (see more https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html).
                                Used with 'hybrid_rff' search. Defaults to 60.

        Returns:
            list[dict]: List of documents matching the search criteria, ranked by relevance.
        """

        logger.info('Searching OpenSearch. \n' +
                    'Parameters: \n' + 
                    f'\tfilter_dict={filter_dict}\n' + 
                    f'\tboost_dict={boost_dict}\n' + 
                    f'\tnum_results={num_results}\n' + 
                    f'\tsearch_type={search_type}\n' +
                    f'\thybrid_rff_k={hybrid_rff_k}')

        fields = [f'{field}^{boost_dict[field]}' if field in boost_dict else field
                  for field in self.text_fields]

        # lexical search
        if search_type in ['lexical', 'hybrid_rff']:
            keyword_query = {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": fields,
                            "type": "best_fields",
                        }
                    }
                }
            }
            if filter_dict:
                keyword_query["bool"]["filter"] = [{"term": {k: v}}
                                                   for k, v in filter_dict.items()]

            keyword_results = self._client.search(
                index=self.index_name,
                body={
                    "_source": {
                        "exclude": [
                            "doc_embedding"
                        ]
                    },
                    "query": keyword_query,
                    "size": num_results * 2, # get more results for reranking
                }
            )['hits']['hits']

        # semantic search
        if search_type in ['semantic', 'hybrid_rff']:
            query_vector = self._embedder.embed([query])[0]
            knn_query = {
                'knn': {
                    'doc_embedding': {
                        'vector': query_vector,
                        'k': num_results * 2,
                    }
                }
            }
            if filter_dict:
                knn_query['filter'] = [{"term": {k: v}}
                                       for k, v in filter_dict.items()]

            knn_results = self._client.search(
                index=self.index_name,
                body={
                    "_source": {
                        "exclude": [
                            "doc_embedding"
                        ]
                    },
                    "query": knn_query,
                    "size": num_results * 2, # get more results for reranking
                }
            )['hits']['hits']

        # get final results
        if search_type == 'lexical':
            final_results = [hit['_source'] for hit in keyword_results[:num_results]]
        elif search_type == 'semantic':
            final_results = [hit['_source'] for hit in knn_results[:num_results]]
        elif search_type == 'hybrid_rff':
            # Reranking using reciprocal rank fusion https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html
            rrf_scores = {}

            # Calculate RRF using vector search results
            for rank, hit in enumerate(knn_results):
                doc_id = hit['_id']
                rrf_scores[doc_id] = compute_rrf(rank + 1, hybrid_rff_k)

            # Adding keyword search result scores
            for rank, hit in enumerate(keyword_results):
                doc_id = hit['_id']
                if doc_id in rrf_scores:
                    rrf_scores[doc_id] += compute_rrf(rank + 1, hybrid_rff_k)
                else:
                    rrf_scores[doc_id] = compute_rrf(rank + 1, hybrid_rff_k)

            # Sort RRF scores in descending order
            reranked_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

            results = reranked_docs

        else:
            raise ValueError(f'Invalid search type: {search_type}.')

        # Get top-K documents by final score after hybrid reranking
        if search_type.startswith('hybrid'):
            final_results = []
            for doc_id, score in results[:num_results]:
                doc = self._client.get(index=self.index_name, id=doc_id)
                final_results.append(doc['_source'])

        logger.info(f'Search successful. Found {len(final_results)} results.')
        
        return final_results
