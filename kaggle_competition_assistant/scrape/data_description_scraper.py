import time

import html2text
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from tenacity import retry, stop_after_attempt, wait_fixed

from ..logger import get_logger
from ..scrape.constants import PAGE_LOADING_WAIT_TIME, RETRY_ATTEMPTS, WAIT_BETWEEN_ATTEMPTS
from ..scrape.utils import clean_blank_lines_in_md_blocks

logger = get_logger(__name__)

@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(WAIT_BETWEEN_ATTEMPTS))
def parse_data_description_html(html_text: str) -> str:
    text = html2text.html2text(html_text)

    # text cleaning
    cleaned_text = []
    lines = text.split('\n')
    noisy_line_markers = []
    noisy_lines = [
        '*  _calendar_view_week_',
        '_calendar_view_week_',
        '_arrow_right_',
        '_folder_',
        '_get_app_ Download All',
        '*  _arrow_right_',
    ]
    i = 0
    while i < len(lines):
        if (
            any(marker in lines[i] for marker in noisy_line_markers) or
            any(marker == lines[i].strip() for marker in noisy_lines)
        ):
            # skip noise lines
            i += 2
        else:
            cleaned_text.append(lines[i].strip())
            i += 1

    cleaned_text = '\n'.join(cleaned_text)

    return cleaned_text


def get_competition_data_description(driver: WebDriver, competition_slug: str) -> str:
    logger.info(f"Starting scraping data description for {competition_slug}...")
    url = f"https://www.kaggle.com/competitions/{competition_slug}/data"

    logger.info(f"Retrieving HTML from {url}...")
    driver.get(url)
    time.sleep(PAGE_LOADING_WAIT_TIME)
    main_dataset_description_html = driver.find_element(
        By.XPATH, '//*[@id="site-content"]/div[2]/div/div/div[6]/div[1]/div[1]'
    ).get_attribute('innerHTML')

    driver.get(url)
    time.sleep(PAGE_LOADING_WAIT_TIME)
    sidebar_description_html = driver.find_element(
        By.XPATH, '//*[@id="site-content"]/div[2]/div/div/div[6]/div[1]/div[2]'
    ).get_attribute('innerHTML')

    driver.get(url)
    time.sleep(PAGE_LOADING_WAIT_TIME)
    data_explorer_html = driver.find_element(
        By.XPATH, '//*[@id="site-content"]/div[2]/div/div/div[6]/div[2]/div[1]/div/div[2]'
    ).get_attribute('innerHTML')

    logger.info(f"HTML from {url} retrieved successfully.")

    main_dataset_description = parse_data_description_html(main_dataset_description_html)
    sidebar_description = parse_data_description_html(sidebar_description_html)
    data_explorer_description = parse_data_description_html(data_explorer_html)

    data_description = main_dataset_description + '\n' + sidebar_description + '\n' + data_explorer_description

    # alternative option if XPATH starts breaking
    # html_page = driver.find_element(
    #     By.CSS_SELECTOR, '[data-testid="competition-detail-render-tid"]'
    # ).get_attribute('innerHTML')
    # data_description = parse_data_description_html(html_page)

    data_description = clean_blank_lines_in_md_blocks(data_description)

    logger.info(f'Finished scraping data description for {competition_slug}.')
    return data_description
