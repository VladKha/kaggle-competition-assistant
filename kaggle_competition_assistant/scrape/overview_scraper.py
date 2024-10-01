import re
import time

import html2text
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from tenacity import retry, stop_after_attempt, wait_fixed

from ..logger import get_logger
from .constants import RETRY_ATTEMPTS, WAIT_BETWEEN_ATTEMPTS, PAGE_LOADING_WAIT_TIME
from .utils import clean_blank_lines_in_md_blocks
# from llama_parse import LlamaParse
# from scrapegraphai.graphs import SmartScraperGraph

logger = get_logger(__name__)

def parse_overview_html(html_text: str) -> str:
    text = html2text.html2text(html_text)

    # text cleaning
    cleaned_text = []
    lines = text.split('\n')
    noisy_line_markers = [
    ]
    noisy_lines = [
        'Late Submission',
        'more_horiz',
        'link',
        'keyboard_arrow_up',
        'content_copy',
        'collapse_all',
        'Cite',
        'Join Competition',
        'ago',
    ]
    i = 0
    while i < len(lines):
        if (
            any(marker in lines[i] for marker in noisy_line_markers) or
            any(marker == lines[i].strip() for marker in noisy_lines) or
            (lines[i].startswith('![](/competitions/') and lines[i].endswith('/media/header)'))
        ):
            # skip noise lines
            i += 2
        else:
            cleaned_text.append(lines[i].strip())
            i += 1

    cleaned_text = '\n'.join(cleaned_text)

    # remove extra navigational links at the top
    words = ['Overview', 'Data', 'Code', 'Models', 'Discussion', 'Leaderboard', 'Rules']
    for w in words:
        pattern = f'\[{w}\]\(/competitions/([a-zA-Z0-9-]|\s)+/{w.lower()}\)'
        cleaned_text = re.sub(pattern, '', cleaned_text)

    # remove table of contents
    cleaned_text = cleaned_text[:cleaned_text.rfind('Table of Contents')]

    # remove tags section
    cleaned_text = cleaned_text[:cleaned_text.rfind('## Tags')]

    cleaned_text = cleaned_text.replace('\n\n\n\n', '\n')

    return cleaned_text


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(WAIT_BETWEEN_ATTEMPTS))
def get_competition_overview(driver: WebDriver, competition_slug: str) -> str:
    logger.info(f"Starting scraping overview for {competition_slug}...")
    url = f"https://www.kaggle.com/competitions/{competition_slug}/overview"

    logger.info(f"Retrieving HTML from {url}...")
    driver.get(url)
    time.sleep(PAGE_LOADING_WAIT_TIME)

    html_page = driver.find_element(
        By.CSS_SELECTOR, '[data-testid="competition-detail-render-tid"]'
    ).get_attribute('innerHTML')
    overview_text = parse_overview_html(html_page)

    logger.info(f"HTML from {url} retrieved successfully.")

    overview_text = clean_blank_lines_in_md_blocks(overview_text)

    logger.info(f'Finished scraping overview for {competition_slug}.')
    return overview_text

# alternative 1
# def get_competition_overview(driver: webdriver.Chrome,
#                              llama_parse_client: LlamaParse,competition_name: str) -> str:
#     logger.info(f"Starting retrieval of overview for {competition_name}...")
#     overview_url = f"https://www.kaggle.com/competitions/{competition_name}/overview"
#
#     html_page = get_html_page(driver, overview_url, element_class_name='sc-btLlPF')
#
#     if not html_page:
#         return ''
#
#     overview_text = ''
#     try:
#         # Save the HTML to a temporary file
#         # with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
#         #     temp_file.write(html_page)
#         #     temp_file_path = temp_file.name
#         #     logger.info(f"HTML saved to temporary file: {temp_file_path}")
#         with open('overview_page.html', 'w') as temp_file:
#             temp_file.write(html_page)
#         temp_file_path = 'overview_page.html'
#
#         documents = llama_parse_client.load_data(temp_file_path)
#
#         for d in documents:#[1:]:
#             overview_text += d.text
#
#     except Exception as e:
#         logger.error(f'Error processing overview for {competition_name}: {e}')
#
#     logger.info(f'Finished retrieval of overview for {competition_name}...')
#     return overview_text


# alternative 2 (less generic implementation)
# def get_competition_overview(competition_name: str) -> str:
#     logger.info(f"Starting retrieval of overview for {competition_name}...")
#     overview_url = f"https://www.kaggle.com/competitions/{competition_name}/overview"
#
#     html_text = get_html_page(overview_url)
#
#     if not html_text:
#         return ''
#
#     try:
#         graph_config = {
#             "llm": {
#                 "model": "ollama/llama3.1",
#                 "temperature": 0,  # 1
#                 "format": "json",  # Ollama needs the format to be specified explicitly
#                 "model_tokens": 2000,  # depending on the model set context length
#                 "base_url": "http://localhost:11434", # set ollama URL of the local host (YOU CAN CHANGE IT, if you have a different endpoint
#             },
#         }
#
#         prompt = """
# You are a professional information extraction assistant.
# Your task is to extract the following information about Kaggle competition while preserving as much of the original content as possible.
#
# Data to extract:
# - Competition name - name of the Kaggle competition
# - One line description - one-line description of the competition at the top of the page
# - Overview - overview section about the competition
# - Description - longer motivational description about the competition
# - Evaluation - details about the evaluation, possible metrics
#     - Evaluation overview
#     - Evaluation metrics
# - Submission details - details about the submission
#     - Submission guidelines
#     - Details about format of the submission file, submission file example
# - Prizes & awards - detailed information about prizes and awards:
#     - Total prizes - total sum of all prizes
#     - Per place prizes - per place prizes
#     - Medals - does competition award medals
# - Timeline - timeline of the competition: start date, end date, first submission and team mergers
# - Host - who is hosting the competition
# - Participation details - details about the participation:
#     - Number of entrants - number of entrants in the competition
#     - Number of participants - number of participants in the competition
#     - Number of teams - number of teams in the competition
#     - Number of submissions - number of submissions in the competition
#         """.strip()
#
#         smart_scraper_graph = SmartScraperGraph(
#             prompt=prompt,
#             source=html_text,
#             config=graph_config
#         )
#
#         extracted_info = smart_scraper_graph.run()
#         logger.info(json.dumps(extracted_info, indent=4))
#         overview_text = dict_to_markdown(extracted_info)
#
#     except Exception as e:
#         logger.info(f'Error processing overview for {competition_name}: {e}')
#         overview_text = ''
#
#     logger.info(f'Finished retrieval of overview for {competition_name}')
#     return overview_text