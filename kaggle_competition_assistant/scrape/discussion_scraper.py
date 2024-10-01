import re
import time
import html2text
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tenacity import retry, stop_after_attempt, wait_fixed
from tqdm.auto import tqdm

from ..logger import get_logger
from ..scrape.constants import PAGE_LOADING_WAIT_TIME, RETRY_ATTEMPTS, WAIT_BETWEEN_ATTEMPTS, \
    WAIT_THROTTLING
from ..scrape.utils import clean_blank_lines_in_md_blocks, \
    is_too_many_requests


logger = get_logger(__name__)


def parse_discussion_html(html_text: str) -> str:
    text = html2text.html2text(html_text)

    # text cleaning
    cleaned_text = []
    lines = text.split('\n')
    noisy_line_markers = [
        '_arrow_drop_up_',
        'more_vert',
        'This post earned',
        'Follow',
        '*  _notifications_',
        '*  _create_new_folder_',
        'Add to Collection',
        '*  _bookmark_border_',
        '*  _format_quote_',
        '*  _link_',
        'Copy Permalink',
        '/static/media/community/reactions/',
        'add_reaction',
        'You do not currently have permissions to reply on this topic.',
        '_arrow_drop_up_',
        '*  _reply_',
        '_comment_',
        '![](/static/media/discussion/high-five-illo.svg)',
        '## Appreciation (',
        '[_emoji_people_]',
    ]
    noisy_lines = [
        'Quote',
        'Reply',
        'Bookmark',
        'Hotness',
        '###',
        'Topic Author',
        'This comment has been deleted.',
        'Competition Host',
        'ago',
        'months ago',
    ]
    i = 0
    while i < len(lines):
        if (
            any(marker in lines[i] for marker in noisy_line_markers) or
            any(marker == lines[i].strip() for marker in noisy_lines) or
            (lines[i].startswith('Posted ') and (lines[i].endswith(' ago'))) or
            (lines[i] and lines[i][0].isdigit() and lines[i].endswith(' in this Competition')) or
            (lines[i].startswith('· ') and lines[i].lower().endswith(' in this competition')) or
            (lines[i].startswith('[](/') and lines[i].endswith(')'))
        ):
            # skip noise lines
            i += 2
        elif lines[i].endswith('#appreciation)'):
            # skip mention about number of appreciation comments
            i += 2
            cleaned_text = cleaned_text[:-2]
        elif ((len(cleaned_text) > 1) and
              cleaned_text[-1].startswith('### [') and
              cleaned_text[-1].endswith(')') and
              lines[i].strip() == ''):
            # skip empty line between author name and start of her comment
            i += 1
        else:
            # add extra newline between separate comments
            if lines[i].startswith('### [') and lines[i].endswith(')'):
                cleaned_text.append('\n')
            cleaned_text.append(lines[i])

            if lines[i].startswith('### [') and lines[i].endswith(')'):
                # skip extra empty line between author name and start of her comment
                i += 2
            else:
                i += 1

    cleaned_text = '\n'.join(cleaned_text).replace('\n\n\n\n', '\n\n\n')
    return cleaned_text


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(WAIT_BETWEEN_ATTEMPTS))
def scrape_single_discussion_page(driver: WebDriver, discussion_metadata: dict) -> str:
    # load page
    while True:
        # kaggle throttles discussion data - extra waiting time

        if is_too_many_requests(driver):
            logger.info(f'Sleeping a bit ({WAIT_THROTTLING}s)...')
            time.sleep(WAIT_THROTTLING)

        driver.get(discussion_metadata['url'])
        time.sleep(PAGE_LOADING_WAIT_TIME)

        # wait for the discussion content to be loaded
        discussion_css_selector = '[data-testid="discussion-detail-render-tid"]'
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, discussion_css_selector))
        )

        if driver.find_element(By.CSS_SELECTOR, discussion_css_selector).text != '':
            break

    
    # expand all "x more replies" threads
    while True:
        more_replies_elements = driver.find_elements(
            By.XPATH, "//span[contains(text(), 'more replies')]"
        )
        pattern = re.compile(r'^\d+ more replies$')
        more_replies_buttons = [b for b in more_replies_elements
                                if (not b.text.startswith('Hide replies')) and pattern.match(b.text.strip())]
        # logger.info(f'Found {len(more_replies_buttons)} more replies buttons for page {discussion_metadata["url"]}')
        if len(more_replies_buttons) == 0:
            break
        else:
            for b in more_replies_buttons:
                driver.execute_script("arguments[0].click();", b)

    # get part of the page with main post + comments
    discussion_html = driver.find_element(By.CSS_SELECTOR, discussion_css_selector).get_attribute('innerHTML')

    discussion_parsed = parse_discussion_html(discussion_html)

    # health check if discussion is empty
    # if empty - most probably scraping failed because of throttling
    if discussion_parsed.strip() == '':
        logger.warning(f'Empty discussion on page {discussion_metadata["url"]}')

    return discussion_parsed


# Function to scrape a single page of discussions
def scrape_discussions_page(driver: WebDriver, page_number: int) -> tuple[list[dict], list[str]]:
    # Get HTML elements for discussion threads
    discussions = driver.find_elements(By.CLASS_NAME,'MuiListItem-divider')

    # parsing metadata
    discussions_metadata_list = []
    for discussion in discussions:
        title = discussion.find_element(By.XPATH, './/div/a/div/div[2]/div/div').text
        url = discussion.find_element(By.TAG_NAME, 'a').get_attribute('href')
        author_name = discussion.find_element(By.CLASS_NAME, 'discussions-item-avatar').get_attribute('aria-label')
        num_upvotes = int(discussion.find_element(By.XPATH, './/div/div/div/div[1]/span').text)
        discussions_metadata_list.append({
            'title': title,
            'author_name': author_name,
            'url': url,
            'num_upvotes': num_upvotes,
            'page_number': page_number
        })

    # parse individual discussions
    discussions_parsed = []
    for d_metadata in tqdm(discussions_metadata_list, desc=f'Scraping discussions from page {page_number}'):
        d_parsed = scrape_single_discussion_page(driver, d_metadata)
        d_parsed = clean_blank_lines_in_md_blocks(d_parsed)
        discussions_parsed.append(d_parsed)

    return discussions_metadata_list, discussions_parsed


@retry(stop=stop_after_attempt(RETRY_ATTEMPTS), wait=wait_fixed(WAIT_BETWEEN_ATTEMPTS))
def get_competition_discussions(driver: WebDriver, competition_slug: str) -> tuple[list[dict], list[str]]:
    logger.info(f'Starting scraping discussions for {competition_slug}...')
    
    base_url = f'https://www.kaggle.com/competitions/{competition_slug}/discussion'

    page_progress_bar = tqdm(desc='Scraping discussion pages')
    discussions_metadata, discussions = [], []
    page_number = 1
    while True:
        # get next discussions page
        page_url = f'{base_url}?page={page_number}'
        driver.get(page_url)
        time.sleep(PAGE_LOADING_WAIT_TIME)

        # scrape current page
        metadata, page_discussions = scrape_discussions_page(driver, page_number)
        discussions_metadata.extend(metadata)
        discussions.extend(page_discussions)
        page_number += 1
        page_progress_bar.update(1)

        # return to the current page to get the next page button
        driver.get(page_url)
        time.sleep(PAGE_LOADING_WAIT_TIME)

        # find the next page button and click it (or terminate if finished)
        next_page_button = driver.find_elements(By.CLASS_NAME, 'MuiButtonBase-root')[-1]
        if next_page_button.get_attribute('aria-label') == 'Go to next page':
            # logger.info('Found next page button')
            driver.execute_script("arguments[0].click();", next_page_button)
        else:
            break
    
    logger.info(f'Finished scraping discussions for {competition_slug}.')

    return discussions_metadata, discussions
