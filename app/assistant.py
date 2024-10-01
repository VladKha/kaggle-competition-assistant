import json
import logging

from kaggle_competition_assistant.llm import llm


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)

# def speech_to_text(audio: pydub.AudioSegment):
#     import pydub
#     logger.info('Translating speech to text...')
#     sound = audio.export().read()
#     text, token_stats, _ = llm([
#         "Please transcribe this recording:",
#         {
#             "mime_type": "audio/mp3",
#             "data": sound
#         }
#     ])
#     logger.info('Speech to text completed')
#     return text


def evaluate_relevance(question, answer):
    prompt_template = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to a given question.
Based on the relevance of the generated answer, you will classify it as "NON_RELEVANT", "PARTIALLY_RELEVANT", or "RELEVANT".

The context of the question and answer relate to a Kaggle competition.
Avoid:
- trying to determine the correctness of the answer. Just focus on generic relevance of answer to the topic of the question.
- trying to reason about the specificity of the answer or additional context. Just focus on generic relevance of answer to the topic of the question.

Here is the data for evaluation:
Question: {question}
Generated answer: {answer_assistant}

Please analyze the content of the generated answer in relation to the question and provide your evaluation in parsable JSON without using any code blocks:
{{
  "relevance": "NON_RELEVANT" | "PARTIALLY_RELEVANT" | "RELEVANT",
  "explanation": "[Provide a brief explanation for your evaluation]"
}}""".strip()

    prompt = prompt_template.format(question=question, answer_assistant=answer)
    evaluation, token_stats, _ = llm(prompt, 'google/gemini-1.5-flash-latest')

    # still some scrubbing of code blocks required
    evaluation = evaluation.removeprefix("```json").removesuffix("```")

    try:
        json_eval = json.loads(evaluation)
        return json_eval['relevance'], json_eval['explanation'], token_stats
    except json.JSONDecodeError:
        return "UNKNOWN", "Failed to parse evaluation", token_stats


def calculate_llm_cost(model_choice, tokens):
    # https://ai.google.dev/pricing
    if model_choice == 'google/gemini-1.5-flash-latest':
        cost = (tokens['prompt_tokens'] * 0.075 + tokens['completion_tokens'] * 0.30) / 1_000_000
    elif model_choice == 'google/gemini-1.5-pro-latest':
        cost = (tokens['prompt_tokens'] * 3.5 + tokens['completion_tokens'] * 10.5) / 1_000_000
    else:
        raise ValueError(f"Unknown model choice: {model_choice}")

    return cost


def ask_assistant(question, assistant, search_type, retrieval_n_results,
                  assistant_llm_name='google/gemini-1.5-pro-latest', relevance_llm_name='google/gemini-1.5-flash-latest'):
    answer, token_stats, query_time = assistant.query(
        question,
        retrieval_configs={
            'search_type': search_type,
            'boost_dict': {"source": 8, "section": 9, "text": 3}
        },
        retrieval_n_results=retrieval_n_results,
        generation_llm_model=assistant_llm_name
    )

    relevance, explanation, eval_tokens = evaluate_relevance(question, answer)
    llm_cost_assistant = calculate_llm_cost(assistant_llm_name, token_stats)
    llm_cost_relevance = calculate_llm_cost(relevance_llm_name, eval_tokens)
    llm_cost = llm_cost_assistant + llm_cost_relevance

    result = {
        'answer': answer,
        'response_time': query_time,

        'relevance': relevance,
        'relevance_explanation': explanation,

        'assistant_model': assistant_llm_name,
        'relevance_model': relevance_llm_name,

        'prompt_tokens': token_stats['prompt_tokens'],
        'completion_tokens': token_stats['completion_tokens'],
        'total_tokens': token_stats['total_tokens'],

        'relevance_prompt_tokens': eval_tokens['prompt_tokens'],
        'relevance_completion_tokens': eval_tokens['completion_tokens'],
        'relevance_total_tokens': eval_tokens['total_tokens'],

        'llm_cost': llm_cost
    }

    return result
