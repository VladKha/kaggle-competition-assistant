import logging
import joblib

from dotenv import load_dotenv
load_dotenv()

from db import init_db
from kaggle_competition_assistant import KaggleCompetitionAssistant

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__file__)


competition_slugs = ['llm-zoomcamp-2024-competition', 'rohlik-orders-forecasting-challenge', 'arc-prize-2024']

def init_assistants():
    assistants = {}
    for competition_slug in competition_slugs:
        assistants[competition_slug] = KaggleCompetitionAssistant(competition_slug,
                                                                  competition_data_path=f'data/{competition_slug}',
                                                                  index_type='opensearch')
    return assistants

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized.")

    logger.info("Initializing assistants...")
    assistants = init_assistants()
    joblib.dump(assistants, 'assistants.pkl')
    logger.info("Assistants initialized.")
