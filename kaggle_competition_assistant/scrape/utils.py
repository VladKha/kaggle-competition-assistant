from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from ..logger import get_logger

logger = get_logger(__name__)


def initialize_kaggle_api() -> 'KaggleApi':
    """Initialize and authenticate the Kaggle API _client."""
    from kaggle.api import KaggleApi

    api = KaggleApi()
    api.authenticate()
    return api


def get_selenium_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")  # Use headless mode for running in the background

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15)
    return driver


def is_too_many_requests(driver: WebDriver) -> bool:
    alert_elements = driver.find_elements(By.XPATH, "//*[@role='alert']")
    for alert in alert_elements:
        if "too many requests" in alert.text.lower():
            logger.warning("Too many requests detected")
            return True
    return False


# def is_loading_circle_present(driver: WebDriver) -> bool:
#     """Kaggle throttles the API - if the loading circle is detected, then the API has been throttled"""
#     loading_circles = driver.find_elements(By.CLASS_NAME, 'rmwc-circular-progress__circle')
#     loading_circles = [c for c in loading_circles if c.is_displayed()]
#     print('Loading circle detected')
#     return len(loading_circles) > 0


def clean_blank_lines_in_md_blocks(text: str) -> str:
    """Clean extra blank lines in top-level Markdown blocks"""

    tmp_1 = []
    block_splitter = '\n## '
    for block in text.split(block_splitter):
        block = block.replace('\n\n', '\n')
        tmp_1.append(block)
    tmp_2 = ('\n' + block_splitter).join(tmp_1)

    # clean blank lines in lower level blocks
    block_splitter = '\n### '
    result = tmp_2.split(block_splitter)
    result = ('\n' + block_splitter).join(result)
    return result
