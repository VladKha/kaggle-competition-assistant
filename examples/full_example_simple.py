import logging
from dotenv import load_dotenv
load_dotenv()

from kaggle_competition_assistant import KaggleCompetitionAssistant
from kaggle_competition_assistant import scrape_competition_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')



competition_slug = 'rohlik-orders-forecasting-challenge'

# scrape_competition_data(competition_slug, 'data')

assistant = KaggleCompetitionAssistant(competition_slug, competition_data_path=f'../data/{competition_slug}')

queries = [
    'What is the description of the competition?',
    'What are competition prizes?',
    'Who is competition host?',
    'How many participants are in the competition?',
    'Who is on place 1 in the leaderboard?',
    'Who are top 3 places in the leaderboard?'
]
for q in queries:
    print(f'Competition: {competition_slug}')
    print(f'Query: {q}')
    result = assistant.query(q, retrieval_configs={'search_type': 'semantic'})
    print(result[0])
    print('-' * 100)
