import time
import os
import weave
from typing import Optional

import google.generativeai as genai
from tenacity import retry, wait_fixed

from kaggle_competition_assistant.logger import get_logger


logger = get_logger(__name__)

# OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')


def build_rag_prompt(query: str, search_results: list[dict], prompt_template: Optional[str] = None) -> str:
    # old prompt, to delete
#     default_prompt_template = """
# You are a Kaggle competition assistant. Answer the QUESTION based on the CONTEXT from the web page content.
# Use only the facts from the CONTEXT when answering the QUESTION.
#
# QUESTION: {question}
#
# CONTEXT:
# {context}
# """.strip()
    default_prompt_template = """
You are a Kaggle competition assistant.
Answer the QUESTION based on the CONTEXT from the web page about the competition.
Use only the facts from the CONTEXT when answering the QUESTION.
Be concise and to the point.

QUESTION: {question}

CONTEXT:
{context}
    """.strip()

    if not prompt_template:
        prompt_template = default_prompt_template

    context = "\n\n".join(
        [
            f"source: {doc['source']}\nsection: {doc['section']}\ntext: {doc['text']}"
            for doc in search_results
        ]
    )
    return prompt_template.format(question=query, context=context).strip()


@weave.op()
@retry(wait=wait_fixed(60))
def llm(prompt: str, model_choice: str = 'google/gemini-1.5-flash-latest') -> tuple[str, dict, float]:
    logger.info(f'Starting LLM request to {model_choice}...')
    start_time = time.time()

    model_provider, model_name = model_choice.split('/')

    # if model_provider == 'ollama':
    #     response = ollama_client.chat.completions.create(
    #         model=model_name,
    #         messages=[{"role": "user", "content": prompt}]
    #     )
    #     answer = response.choices[0].message.content
    #     tokens = {
    #         'prompt_tokens': response.usage.prompt_tokens,
    #         'completion_tokens': response.usage.completion_tokens,
    #         'total_tokens': response.usage.total_tokens
    #     }
    if model_provider == 'google':
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(model_name)
        response = gemini_model.generate_content(prompt)
        answer = response.text
        token_stats = {
            'prompt_tokens': response.usage_metadata.prompt_token_count,
            'completion_tokens': response.usage_metadata.candidates_token_count,
            'total_tokens': response.usage_metadata.total_token_count
        }
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")

    end_time = time.time()
    response_time = end_time - start_time

    logger.info(f'LLM request successfully finished in {response_time:.2f} seconds.')

    return answer, token_stats, response_time
