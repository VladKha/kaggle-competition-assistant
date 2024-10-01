from abc import abstractmethod


class IndexBase:
    """
    Base class of Indexers for text and keyword fields.

    Attributes:
        text_fields (list): List of text field names to index.
        keyword_fields (list): List of keyword field names to index.
    """

    def __init__(self, text_fields, keyword_fields, **kwargs):
        """
        Initializes the Index with specified text and keyword fields.

        Args:
            text_fields (list): List of text field names to index.
            keyword_fields (list): List of keyword field names to index.
            kwargs (dict): Optional parameters for child classes
        """
        self.text_fields = text_fields
        self.keyword_fields = keyword_fields

    @abstractmethod
    def index(self, docs: list[dict]) -> None:
        """
        Creates the index with the provided documents.

        Args:
            docs (list of dict): List of documents to index. Each document is a dictionary.
        """
        pass

    @abstractmethod
    def search(self, query: str, filter_dict: dict = {}, boost_dict: dict[str,float] = {}, num_results: int = 10, **kwargs) -> list[dict]:
        """
        Searches the index with the given query, filters, and boost parameters.

        Args:
            query (str): The search query string.
            filter_dict (dict): Dictionary of keyword fields to filter by.
                                Keys are field names and values are the values to filter by.
            boost_dict (dict): Dictionary of boost scores for text fields.
                                Keys are field names and values are the boost scores.
            num_results (int): The number of top results to return. Defaults to 10.

            kwargs (dict): Optional parameters for child classes

        Returns:
            list of _docs (list[dict]): List of documents matching the search criteria, ranked by relevance.
        """
        pass
