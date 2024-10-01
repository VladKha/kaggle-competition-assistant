import hashlib
import os
from pathlib import Path
from typing import Union

import pandas as pd

from .data_description_scraper import get_competition_data_description
from .discussion_scraper import get_competition_discussions
from .overview_scraper import get_competition_overview
from .leaderboard_scraper import get_competition_leaderboard
from .utils import get_selenium_driver, initialize_kaggle_api
from ..logger import get_logger
from ..utils import save_to_file
# from llama_parse import LlamaParse


logger = get_logger(__name__)

def scrape_competition_data(competition_slug: str, path: Union[str, Path]) -> Union[Path, str]:
    logger.info(f'Starting scraping competition {competition_slug}...')

    kaggle_api_client = initialize_kaggle_api()
    # llama_parse_client = LlamaParse(result_type='markdown')
    driver = get_selenium_driver()

    # Create a dedicated folder for the competition
    competition_folder_path = Path(path) / Path(f'{competition_slug}')
    os.makedirs(competition_folder_path, exist_ok=True)

    # 1. Download competition information
    overview = get_competition_overview(driver, competition_slug)
    overview_file_path = competition_folder_path / 'overview.md'
    save_to_file(overview, overview_file_path)

    # 2. Download dataset information
    data_description = get_competition_data_description(driver, competition_slug)
    data_description_file_path = competition_folder_path / 'data_description.md'
    save_to_file(data_description, data_description_file_path)

    # 3. Download discussions
    driver = get_selenium_driver()
    discussions_metadata, discussions = get_competition_discussions(driver, competition_slug)

    # 3.1 Save discussions metadata to a file
    d_metadata_text = pd.DataFrame(discussions_metadata)
    d_metadata_file_path = competition_folder_path / 'discussion_metadata.csv'
    d_metadata_text.to_csv(d_metadata_file_path, index=False)

    # 3.2 save each discussion into a separate file
    discussions_folder_path = competition_folder_path / 'discussions'
    os.makedirs(discussions_folder_path, exist_ok=True)
    for d_metadata, d in zip(discussions_metadata, discussions):
        title = d_metadata['title']
        id = d_metadata['url'].split('/')[-1]
        output_file = f'{id}_{title}.txt'

        # sanitize output file name not contain "/" - breaks saving to file
        # (maybe use https://github.com/thombashi/pathvalidate as a more advanced solution?)
        output_file = output_file.replace('/', '-')
        save_to_file(d, discussions_folder_path / output_file)

    # 4. Download leaderboard information
    leaderboard = get_competition_leaderboard(kaggle_api_client, competition_slug)
    leaderboard_file_path = competition_folder_path / 'leaderboard.csv'
    save_to_file(leaderboard, leaderboard_file_path)

    # 5. Download kernels + comments information
    # TODO
    # kaggle kernels pull (no comments)

    # cleanup
    driver.quit()

    logger.info(f"All information for the '{competition_slug}' competition has been downloaded to the '{competition_folder_path}' folder.")
    return competition_folder_path
