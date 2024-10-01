# Evaluation

## Ground truth datasets
For evaluation purposes, a synthetic dataset with questions-answer pairs was generated using Google Gemini models.   
Each question-answer pair was generated based on specific text snippet from the competition data.   
`gemini-1.5-flash-latest` and `gemini-1.5-pro-latest` LLMs were used for generation.   
A "smarter" pro-model was used on most of the discussion-based generation, since those texts are usually larger and more complex.

Many of the generated question-answer pairs were manually reviewed after generation and are mostly of high quality, but definitely not 100% ideal.

Datasets sizes:
- `llm-zoomcamp-2024` - 45 question-answer pairs
- `rohlik-orders-forecasting-challenge` - 115 question-answer pairs

See more details in [notebooks](../notebooks) folder:
1. [evaluation-data-generation.ipynb](../notebooks/evaluation-data-generation.ipynb): generating ground truth dataset for evaluation.
2. [rag-retrieval-evaluation.ipynb](../notebooks/rag-retrieval-evaluation.ipynb): evaluation of retrieval only part of the RAG.
3. [rag-end2end-evaluation.ipynb](../notebooks/rag-end2end-evaluation.ipynb): evaluation of the whole RAG pipeline.
4. generated datasets and results in [evaluation](../data/evaluation) folder.

## Retrieval evaluation
Results after tuning boosting hyperparameters of search:

1. `llm-zoomcamp-2024` dataset

    | search type  | num results | boost parameters                                | hit rate | mrr    |
    |:-------------|:------------|:------------------------------------------------|:---------|:-------|
    | lexical      | 5           | {"source": 6.98, "section": 3.40, "text": 1.55} | 0.6889   | 0.5248 |
    | lexical      | 10          | {"source": 0.25, "section": 7.37, "text": 3.32} | 0.7778   | 0.5372 |
    | hybrid + rff | 5           | {"source": 4.94, "section": 0.80, "text": 0.40} | 0.8444   | 0.6556 |
    | semantic     | 5           | -                                               | 0.8444   | 0.6670 |
    | semantic     | 10          | -                                               | 0.9333   | 0.6797 |
    | hybrid + rff | 10          | {"source": 9.15, "section": 2.21, "text": 0.63} | 0.9556   | 0.7055 |

2. `rohlik-orders-forecasting-challenge` dataset

    | search type  | num results | boost parameters                                 | hit\_rate | mrr    |
    |:-------------|:------------|:-------------------------------------------------|:----------|:-------|
    | lexical      | 5           | {"source": 3.38, "section": 5.88, "text": 2.30}  | 0.6522    | 0.5204 |
    | lexical      | 10          | {"source": 6.69, "section": 5.64, "text": 2.18}  | 0.7391    | 0.5334 |
    | hybrid + rff | 5           | {"source": 5.08, "section": 8.21, "text": 2.82}  | 0.8174    | 0.6800 |
    | hybrid + rff | 10          | {"source": 8.24, "section": 9.09, "text": 3.022} | 0.8870    | 0.6851 |
    | semantic     | 5           | -                                                | 0.8087    | 0.6942 |
    | semantic     | 10          | -                                                | 0.8870    | 0.7065 |


## RAG end2end evaluation
Evaluations consisted of:
1. cosine similarity of generated answer with the ground truth.
    - embedding mode `Lajavaness/bilingual-embedding-large` - best Semantic Textual Similarity model according to https://huggingface.co/spaces/mteb/leaderboard
2. LLM-as-a-judge evaluations of:
   - relevance of RAG-generated answer with the ground truth answer
   - relevance of RAG-generated answer to a question
   - using `gemini-1.5-flash-latest` LLM

end2end evaluations were done with 2 variations of prompts for each dataset.

### Cosine similarity evaluation results
1. `llm-zoomcamp-2024` dataset
   1. initial prompt
   
        |       | cosine similarity |
        |:------|:------------------|
        | count | 45                |
        | mean  | 0.660743          |
        | std   | 0.213638          |
        | min   | 0.006070          |
        | 25%   | 0.464731          |
        | 50%   | 0.679022          |
        | 75%   | 0.848746          |
        | max   | 1.000000          |      

   2. modified prompt
      
        |       | cosine\_similarity |
        |:------|:-------------------|
        | count | 45                 |
        | mean  | 0.830977           |
        | std   | 0.215939           |
        | min   | 0.035656           |
        | 25%   | 0.795087           |
        | 50%   | 0.902256           |
        | 75%   | 1.000000           |
        | max   | 1.000000           |

2. `rohlik-orders-forecasting-challenge` dataset 
   1. initial prompt

        |       | cosine similarity |
        |:------|:------------------|
        | count | 115               |
        | mean  | 0.681473          |
        | std   | 0.187289          |
        | min   | 0.109915          |
        | 25%   | 0.558338          |
        | 50%   | 0.722075          |
        | 75%   | 0.826727          |
        | max   | 0.992766          |

   2. modified prompt

        |       | cosine\_similarity |
        |:------|:-------------------|
        | count | 115                |
        | mean  | 0.756441           |
        | std   | 0.184881           |
        | min   | 0.067134           |
        | 25%   | 0.634209           |
        | 50%   | 0.771948           |
        | 75%   | 0.905124           |
        | max   | 1.000000           |



### LLM-as-a-judge evaluation results
1. `llm-zoomcamp-2024` dataset
   1. initial prompt 
      - relevance of RAG-generated answer with the ground truth answer
      
        | answer-answer relevance | count    | 
        |:------------------------|:---------|
        | RELEVANT                | 37 (82%) |
        | PARTIALLY_RELEVANT      | 4  (9%)  |
        | NON_RELEVANT            | 4  (9%)  |
      - relevance of RAG-generated answer to a question
        
        | answer-question relevance | count    |
        |:--------------------------|:---------|
        | RELEVANT                  | 39 (87%) |
        | PARTIALLY\_RELEVANT       | 4  (9%)  | 
        | NON_RELEVANT              | 2  (4%)  |

   2. modified prompt
      - relevance of RAG-generated answer with the ground truth answer

        | answer-answer relevance | count    |
        |:------------------------|:---------|
        | RELEVANT                | 35 (78%) |
        | PARTIALLY\_RELEVANT     | 5  (11%) |
        | NON\_RELEVANT           | 5  (11%) |

      - relevance of RAG-generated answer to a question

        | answer-question relevance | count    |
        |:--------------------------|:---------|
        | RELEVANT                  | 26 (58%) |
        | PARTIALLY\_RELEVANT       | 11 (24%) |
        | NON\_RELEVANT             | 8  (18%) |

2. `rohlik-orders-forecasting-challenge` dataset
   1. initial prompt 
      - relevance of RAG-generated answer with the ground truth answer

        | answer-answer relevance | count    |
        |:------------------------|:---------|
        | RELEVANT                | 61 (53%) |
        | PARTIALLY_RELEVANT      | 34 (30%) |
        | NON_RELEVANT            | 20 (17%) |

      - relevance of RAG-generated answer to a question

        | answer-question relevance | count    |
        |:--------------------------|:---------|
        | RELEVANT                  | 67 (58%) |
        | PARTIALLY_RELEVANT        | 34 (30%) |
        | NON_RELEVANT              | 14 (12%) |

   2. modified prompt
      - relevance of RAG-generated answer with the ground truth answer

        | answer-answer relevance | count    |
        |:------------------------|:---------|
        | RELEVANT                | 64 (56%) |
        | PARTIALLY_RELEVANT      | 38 (33%) |
        | NON_RELEVANT            | 13 (11%) |

      - relevance of RAG-generated answer to a question

        | answer-question relevance | count    |
        |:--------------------------|:---------|
        | RELEVANT                  | 57 (50%) |
        | PARTIALLY\_RELEVANT       | 48 (42%) |
        | NON\_RELEVANT             | 10 (8%)  |

### Summary of RAG end2end evaluation evaluation results
- modified prompt:
  - improved results for cosine similarity metric - most clearly visible by significantly increased mean score.
    One of the reasons probably is that new answers became more concise
  - most probably improved results according to LLM-as-a-judge evaluation of relevance of RAG-generated answer with the ground truth answer
  - but LLM-as-a-judge results for relevance of RAG-generated answer to a question are mixed. 
    After manual inspection of some reasoning behind predictions they feel not very correct.
    Probably requires more tweaks on the prompting side
