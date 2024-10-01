# TODO

1. Ingestion
   1. Add differentiation between private and public leaderboard.
   2. Speed up: use proxies / more advanced scrapping solutions to overcome Kaggle throttling and parallelize scraping
   3. Better structure of discussions - preserve parent/children relationship between comments (currently ignored)
   4. Add kernels (code) + comments
      - code via kaggle API: https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md
      - comments - scrapping?
   5. Use [Meta Kaggle](https://www.kaggle.com/datasets/kaggle/meta-kaggle/data) & [Meta Kaggle Code](https://www.kaggle.com/datasets/kaggle/meta-kaggle-code) data when possible (covers only finished, not community-based competitions)
   6. Filter out not-informative comments before ingestion (e.g. "Thanks", "Thank you", "I appreciate it", etc.)
   7. Include embedded images in all texts (currently ignored)
   8. Add full competition dataset. Maybe separate regime / index / skill
2. Retrieval
   1. Experiment with different embedding models, potentially:
      - nomic (https://huggingface.co/nomic-ai/nomic-embed-text-v1)
      - `multi-qa-MiniLM-L6-cos-v1`
   2. Different retrieval approach: ColBERT/RAGatouille
   3. Multiple retrievers with retrieval routing / query analysis [LangChain example](https://python.langchain.com/docs/how_to/query_multiple_retrievers/)
3. LLM
   1. Add ollama support for LLM model
4. UI (optional)
   1. move most of the heavyweight stuff to backend and make UI a bit more responsive
5. Evaluation
   1. More advanced evaluation techniques
   2. Use existing libraries like RAGAS, evidently, etc.
   3. Move evaluation from jupyter notebooks to scripts / part of library 
6. Advanced assistant functionality
   1. Conversation mode - long-form chat, multiple turns
   2. Code completion conditioned by context from competition (e.g. all kernel notebooks, or best kernels, etc.)
   3. Skills & tool use
      - connect with existing Kaggle API
      - see also [fastkaggle](https://github.com/fastai/fastkaggle/tree/master/)
      - add new skills (e.g. "find similar past competitions", "do EDA of the dataset", "build a baseline model", etc.)
   4. use whole platform data
      - all competitions
      - platform docs https://www.kaggle.com/docs/
7. Tests
   1. Library level
