# Simple search index using TF-IDF and cosine similarity
# Adapted with minor changes from https://github.com/alexeygrigorev/minsearch
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from kaggle_competition_assistant.index.index_base import IndexBase


class MinSearchIndex(IndexBase):
    """
    A simple search index using TF-IDF and cosine similarity for text fields and exact matching for keyword fields.

    Attributes:
        text_fields (list): List of text field names to index.
        keyword_fields (list): List of keyword field names to index.
        _vectorizers (dict): Dictionary of TfidfVectorizer instances for each text field.
        _keyword_df (pd.DataFrame): DataFrame containing keyword field data.
        _text_matrices (dict): Dictionary of TF-IDF matrices for each text field.
        _docs (list): List of documents indexed.
    """

    def __init__(self, text_fields: list[str], keyword_fields: list[str], vectorizer_params: dict = {}, **kwargs):
        """
        Initializes the Index with specified text and keyword fields.

        Args:
            text_fields (list): List of text field names to index.
            keyword_fields (list): List of keyword field names to index.
            vectorizer_params (dict): Optional parameters to pass to TfidfVectorizer.
        """
        super().__init__(text_fields, keyword_fields, **kwargs)

        self._vectorizers = {field: TfidfVectorizer(**vectorizer_params) for field in text_fields}
        self._keyword_df = None
        self._text_matrices = {}
        self._docs = []

    def index(self, docs: list[dict]):
        """
        Creates the index with the provided documents.

        Args:
            docs (list of dict): List of documents to index. Each document is a dictionary.
        """
        self._docs = docs
        keyword_data = {field: [] for field in self.keyword_fields}

        for field in self.text_fields:
            texts = [doc.get(field, '') for doc in docs]
            self._text_matrices[field] = self._vectorizers[field].fit_transform(texts)

        for doc in docs:
            for field in self.keyword_fields:
                keyword_data[field].append(doc.get(field, ''))

        self._keyword_df = pd.DataFrame(keyword_data)

        return self

    def search(self, query: str, filter_dict: dict = {}, boost_dict: dict[str, float] = {}, num_results: int = 10, **kwargs) -> list[dict]:
        """
        Searches the index with the given query, filters, and boost parameters.

        Args:
            query (str): The search query string.
            filter_dict (dict): Dictionary of keyword fields to filter by. Keys are field names and values are the values to filter by.
            boost_dict (dict): Dictionary of boost scores for text fields. Keys are field names and values are the boost scores.
            num_results (int): The number of top results to return. Defaults to 10.

        Returns:
            list of dict: List of documents matching the search criteria, ranked by relevance.
        """
        query_vecs = {field: self._vectorizers[field].transform([query]) for field in self.text_fields}
        scores = np.zeros(len(self._docs))

        # Compute cosine similarity for each text field and apply boost
        for field, query_vec in query_vecs.items():
            sim = cosine_similarity(query_vec, self._text_matrices[field]).flatten()
            boost = boost_dict.get(field, 1)
            scores += sim * boost

        # Apply keyword filters
        for field, value in filter_dict.items():
            if field in self.keyword_fields:
                mask = self._keyword_df[field] == value
                scores = scores * mask.to_numpy()

        # Use argpartition to get top num_results indices
        top_indices = np.argpartition(scores, -num_results)[-num_results:]
        top_indices = top_indices[np.argsort(-scores[top_indices])]

        # Filter out zero-score results
        top_docs = [self._docs[i] for i in top_indices if scores[i] > 0]

        return top_docs
