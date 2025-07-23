from typing import Iterable, Any

import numpy as np
import requests
import structlog

from models.ai_chat import Question
from .base import QuestionLookupRepositoryBase

logger = structlog.get_logger("yandex_embedding")


class QuestionLookupRepository(QuestionLookupRepositoryBase):
    def __init__(self, folder_id: str, token: str):
        self.folder_id = folder_id
        self.token = token

        self.doc_uri = f"emb://{self.folder_id}/text-search-doc/latest"
        self.query_uri = f"emb://{self.folder_id}/text-search-query/latest"
        self.embed_url = "https://llm.api.cloud.yandex.net:443/foundationModels/v1/textEmbedding"
        self.headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}",
                        "x-folder-id": f"{self.folder_id}"}

    async def get_related_question(self, question: str, questions: Iterable[str]) -> str:
        raise NotImplementedError()

    async def get_embedding(self, question: str) -> np.ndarray:
        return self._get_embedding(question)

    def _get_embedding(self, text: str, text_type: str = "doc") -> np.array:
        query_data = {
            "modelUri": self.doc_uri if text_type == "doc" else self.query_uri,
            "text": text,
        }

        response_json = requests.post(self.embed_url, json=query_data, headers=self.headers).json()
        return np.array(
            response_json["embedding"]
        )