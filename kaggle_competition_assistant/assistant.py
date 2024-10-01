import json
import time
from pathlib import Path
from typing import Optional, Union

import weave
from tenacity import stop_after_attempt, retry

from .index.minsearch import MinSearchIndex
from .index.opensearch_index import OpenSearchIndex
from .llm import build_rag_prompt, llm
from .logger import get_logger
from .scrape import scrape_competition_data
from .utils import create_documents

logger = get_logger(__name__)

class KaggleCompetitionAssistant:
    def __init__(self, competition_slug: str, competition_data_path: Optional[Union[str, Path]] = None,
                 index_type: str = 'minsearch', index_configs: Optional[dict] = None):
        self.competition_slug = competition_slug
        self.index_type = index_type
        self._index_configs = index_configs or {}

        if competition_data_path:
            self.competition_data_path = Path(competition_data_path)
        else:
            cur_dir = Path.cwd()
            self.competition_data_path = self._scrape_competition_data(cur_dir)

        self._ingest_competition_data()


    def _scrape_competition_data(self, save_path: Union[str, Path]) -> Union[str, Path]:
        logger.info(f'Starting scraping competition for {self.competition_slug}...')
        competition_data_path = scrape_competition_data(self.competition_slug, save_path)
        self.competition_data_path = competition_data_path
        logger.info(f'Competition data scraped: {competition_data_path}')
        return competition_data_path
    
    def _ingest_competition_data(self):
        logger.info(f'Starting ingesting competition data for {self.competition_slug}...')

        documents = create_documents(self.competition_slug, self.competition_data_path)
        if self.index_type == 'minsearch':
            self._index = MinSearchIndex(text_fields=['source', 'section', 'text'], keyword_fields=['url', 'id'])
            self._index.index(documents)
        elif self.index_type == 'opensearch':
            self._index = OpenSearchIndex(text_fields=['source', 'section', 'text'], keyword_fields=['url', 'id'], **self._index_configs)
            self._index.index(documents)
        else:
            raise ValueError(f'Invalid index type: {self.index_type}')

        logger.info(f'Competition data successfully ingested to {self.index_type}.')

    @weave.op()
    @retry(stop=stop_after_attempt(2))
    def _query_rewriting_retrieval(self, query: str, num_results: int = 10,
                                   retrieval_configs: Optional[dict] = None,
                                   llm_model: str = 'google/gemini-1.5-flash-latest') -> list[dict]:
        # using example from https://colab.research.google.com/drive/1-NT0_mmyoSnaDQJ1Zuo0XX613TG5lzjZ?usp=sharing#scrollTo=UU_Sx0Luw-J_
        prompt = f"""
You are a helpful assistant that generates multiple search queries based on a single input query.

Perform query expansion. If there are multiple common ways of phrasing a user question 
or common synonyms for key words in the question, make sure to return multiple versions
of the query with the different phrasings.

If there are acronyms or words you are not familiar with, do not try to rephrase them.

Return 3 different versions of the question.

User's question: {query}

Please analyze the question and provide your additional questions in parsable JSON without using code blocks:
{{
    "question 1": "provided by you question 1",
    "question 2": "provided by you question 2",
    "question 3": "provided by you question 3"
}}""".strip()
        answer, tokens, response_time = llm(prompt, model_choice=llm_model)

        # additional scrubbing of json code blocks to make sure
        answer = answer.removeprefix("```json").removesuffix("```")
        answer_json = json.loads(answer)

        queries = list(answer_json.values())
        queries = [query] + queries

        retrieval_results = []
        retrieval_results_set = set()
        for q in queries:
            r = self._index.search(
                query=q,
                num_results=num_results // 2,
                **retrieval_configs
            )

            # make sure we don't have duplicate docs
            for doc in r:
                if doc['id'] not in retrieval_results_set:
                    retrieval_results_set.add(doc['id'])
                    retrieval_results.append(doc)

        return retrieval_results

    @weave.op()
    def query(self, query: str,
              retrieval_n_results: int = 10, retrieval_configs: Optional[dict] = None,
              query_rewriting=True,
              generation_llm_prompt: Optional[str] = None,
              generation_llm_model: str = 'google/gemini-1.5-flash-latest') -> tuple[str, dict, float]:
        logger.info('Starting querying competition data...')
        logger.info(f'Query: {query}')

        start = time.time()

        # 1. Retrieve
        logger.info(f'Retrieving results from {self.index_type} index' +
                    (f' with query rewriting' if query_rewriting else '') + '...')
        query_rewriting_failed = False
        if query_rewriting:
            try:
                retrieval_results = self._query_rewriting_retrieval(query,
                                                                    num_results=retrieval_n_results,
                                                                    retrieval_configs=retrieval_configs,
                                                                    llm_model=generation_llm_model)
            except Exception as e:
                logger.warning(f'Query rewriting failed: {e}\nFalling back to regular retrieval...')
                query_rewriting_failed = False

        if (not query_rewriting) or query_rewriting_failed:
            logger.info(f'Retrieving {retrieval_n_results} results from {self.index_type} index...')
            retrieval_results = self._index.search(
                query=query,
                num_results=retrieval_n_results,
                **retrieval_configs
            )
        retrieval_time = time.time() - start
        logger.info(f'Retrieved {len(retrieval_results)} results for query in {retrieval_time:.2f} seconds.')

        # 2. Augment
        prompt = build_rag_prompt(query, retrieval_results, prompt_template=generation_llm_prompt)

        # 3. Generate
        answer, token_stats, response_time = llm(prompt, model_choice=generation_llm_model)

        end = time.time()
        query_time = end - start

        logger.info('Successfully finished querying competition data.')
        return answer.strip(), token_stats, query_time
