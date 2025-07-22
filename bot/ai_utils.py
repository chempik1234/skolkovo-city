import numpy as np


def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    return embedding.tobytes()


def embedding_from_bytes(embedding: bytes, dtype=np.float64) -> np.ndarray:
    return np.frombuffer(embedding, dtype=dtype)
