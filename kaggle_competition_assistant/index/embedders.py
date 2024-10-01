from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from kaggle_competition_assistant.logger import get_logger
from kaggle_competition_assistant.utils import get_torch_device


logger = get_logger(__name__)

class Embedder:
    def __init__(self, model_name: Optional[str] = 'multi-qa-mpnet-base-cos-v1', device: Optional[str] = None):
        if not model_name:
            model_name = 'multi-qa-mpnet-base-cos-v1'

        logger.info(f'Initializing embedder with model name: {model_name}...')

        self.model_name = model_name
        self._device = device or get_torch_device()
        self._model = SentenceTransformer(model_name, trust_remote_code=True).to(device)
        
        self._embedding_size = self._model.get_sentence_embedding_dimension()
        logger.info(f'Embedding size: {self._embedding_size}')
        logger.info(f'Embedder initialized with model name: {model_name}.')

    def embed(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(texts)

    @property
    def embedding_size(self) -> int:
        return self._embedding_size
