from pathlib import Path
from typing import Union

import pandas as pd
import torch
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter

from kaggle_competition_assistant.logger import get_logger


logger = get_logger(__name__)


def save_to_file(text: str, file_path: Union[str, Path]):
    with open(file_path, 'w') as f:
        f.write(text)


def dict_to_markdown(d: dict, level=1):

    def parse_item(key, value, level):
        md = f"{'#' * level} {key.title()}\n"
        if isinstance(value, dict):
            md += "".join(parse_item(k, v, level + 1) for k, v in value.items())
        elif isinstance(value, list):
            md += "".join(f"- {item}\n" for item in value)
            md += "\n"
        else:
            value = str(value).replace('\n\n', '\n')
            md += f"{value}\n\n"
        return md

    result = "".join(parse_item(k, v, level) for k, v in d.items())
    return result


def create_documents(competition_slug: str, competition_data_path: Union[str,Path]) -> list[dict]:
    logger.info(f'Starting creating documents for {competition_slug}...')

    if type(competition_data_path) is str:
        competition_data_path = Path(competition_data_path)

    # transform each data part via chunking into a structured document
    # with fields: source, section, text, url
    documents = []

    # 1. overview
    overview_path = competition_data_path / 'overview.md'
    with open(overview_path, 'r') as f:
        overview = f.read()

    competition_name = [line for line in overview.split('\n') if line.startswith('#')][0]
    competition_name = competition_name.strip('#').strip()
    documents.append({
        'source': 'overview',
        'section': 'competition name',
        'text': competition_name,
        'url': f'https://www.kaggle.com/competitions/{competition_slug}/overview'
    })
    # TODO: convert to langchain _docs?

    headers_to_split_on = [
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
    for d in markdown_splitter.split_text(overview):
        documents.append({
            'source': 'overview',
            'section': d.metadata.get('Header 3') or d.metadata.get('Header 2') or '',
            'text': d.page_content,
            'url': f'https://www.kaggle.com/competitions/{competition_slug}/overview'
        })
    # TODO: convert to langchain _docs?

    # 2. data description
    data_description_path = competition_data_path / 'data_description.md'
    with open(data_description_path, 'r') as f:
        data_description = f.read()
    for d in markdown_splitter.split_text(data_description):
        documents.append({
            'source': 'data description',
            'section': d.metadata.get('Header 3') or d.metadata.get('Header 2') or '',
            'text': d.page_content,
            'url': f'https://www.kaggle.com/competitions/{competition_slug}/data'
        })
    # TODO: convert to langchain _docs?

    # 3. load leaderboard.md
    leaderboard_path = competition_data_path / 'leaderboard.csv'
    loader = CSVLoader(file_path=leaderboard_path)
    leaderboard_docs = loader.load()
    for d in leaderboard_docs:
        documents.append({
            'source': 'leaderboard',
            'section': '',
            'text': d.page_content,
            'url': f'https://www.kaggle.com/competitions/{competition_slug}/leaderboard'
        })
    # TODO: convert to langchain _docs?

    # 4. load discussions
    discussions_path = competition_data_path / 'discussions'
    discussions_metadata = pd.read_csv(competition_data_path / 'discussion_metadata.csv')
    for f_rel_path in discussions_path.glob('*.txt'):
        f_abs_path = Path.cwd() / f_rel_path
        id = f_rel_path.stem.split('_')[0]
        url = f'https://www.kaggle.com/competitions/{competition_slug}/discussion/{id}'
        title = discussions_metadata[discussions_metadata['url'] == url]['title'].values[0]

        with open(f_abs_path, 'r') as f:
            documents.append({
                'source': 'discussions',
                'section': title,
                'text': f.read(),
                'url': url
            })
    # TODO: convert to langchain _docs?
    # TODO: add semantic chunking for discussions

    for i,d in enumerate(documents):
        d['id'] = i

    logger.info(f'Documents created: {len(documents)}')
    return documents

def get_torch_device():
    device = 'cpu'
    if torch.cuda.is_available():
        device = 'cuda'
    elif torch.backends.mps.is_available():
        device = 'mps'

    return torch.device(device)

if __name__ == '__main__':
    # Example usage
    d = {
        "Name": "Rohlik Orders Forecasting Challenge",
        "One line description": "Use historical data to predict customer orders",
        "Overview": "Rohlik Group, a leading European e-grocery innovator, is revolutionising the food retail industry. We operate across 11 warehouses in Czech Republic, Germany, Austria, Hungary, and Romania.\n\nOur challenge focuses on predicting the number of orders (grocery deliveries) at selected warehouses for the next 60 days.",
        "Description": "Accurate order forecasts are crucial for planning process, impacting workforce allocation, delivery logistics, inventory management, and supply chain efficiency. By optimizing forecasts, we can minimize waste and streamline operations, making our e-grocery services more sustainable and efficient.\n\nYour participation in this challenge will directly contribute to Rohlik mission of sustainable and efficient e-grocery delivery. Your insights will help us enhance customer service and achieve a greener future.",
        "Evaluation": "Submissions are evaluated on Mean Absolute Percentage Error between the predicted orders and the actual orders",
        "Submission details": "For each ID in the test set, you must predict the number of orders. The file should contain a header and have the following format:\n\nID,ORDERS\nPrague_1_2024-03-16,5000\nPrague_1_2024-03-17,5000\nPrague_1_2024-03-18,5000\netc.",
        "Prizes & awards": {
            "Total prizes": "$12,000",
            "Per place prizes": {
                "1st place": "$5,000",
                "2nd place": "$5,000",
                "3rd place": "$2,000"
            },
            "Medals": "Does not award Points or Medals"
        },
        "Timeline": "August 9, 2024 - First Submission deadline. Your team must make its first submission by this deadline.\n\nAugust 9, 2024 - Team Merger deadline. This is the last day you may merge with another team.\n\nAugust 23, 2024 - Final submission deadline",
        "Host": "MichalKecera",
        "Participation details": {
            "Number of entrants": "2,928",
            "Number of participants": "1,119",
            "Number of teams": "1,017",
            "Number of submissions": "18,956"
        }
    }

    markdown_output = dict_to_markdown(d)
    print(markdown_output)
