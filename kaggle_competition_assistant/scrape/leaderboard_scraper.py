import pandas as pd

from ..logger import get_logger


logger = get_logger(__name__)


def get_competition_leaderboard(kaggle_api_client: 'KaggleApi', competition_name: str) -> str:
    logger.info(f"Starting getting leaderboard for {competition_name}...")

    leaderboard = []
    for r in kaggle_api_client.competition_leaderboard_view(competition=competition_name):
        leaderboard.append([r.teamName, r.submissionDate, r.scoreNullable])
    leaderboard = pd.DataFrame(leaderboard, columns=['team_name', 'submission_date', 'score'])
    leaderboard.index = leaderboard.index + 1
    leaderboard.index.name = 'place'
    leaderboard_text = leaderboard.to_csv(index=True, header=True)

    logger.info(f'Finished scraping overview for {competition_name}.')
    return leaderboard_text
