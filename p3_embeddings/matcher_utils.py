import numpy as np
from typing import List, Tuple


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    """
    if vec_a is None or vec_b is None:
        return 0.0

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def cosine_similarity_matrix(
    source_embeddings: List[np.ndarray],
    target_embeddings: List[np.ndarray],
) -> np.ndarray:
    """
    Compute full cosine similarity matrix:
    shape = (len(source), len(target))
    """
    source = np.stack(source_embeddings)
    target = np.stack(target_embeddings)

    source_norm = source / np.linalg.norm(source, axis=1, keepdims=True)
    target_norm = target / np.linalg.norm(target, axis=1, keepdims=True)

    return np.dot(source_norm, target_norm.T)


def top_k_similar(
    query_embedding: np.ndarray,
    candidates: List[Tuple[str, np.ndarray]],
    k: int = 5,
    threshold: float = 0.0,
) -> List[Tuple[str, float]]:
    """
    Return top-k most similar candidates above threshold.
    candidates = [(id, embedding), ...]
    """
    scores = []

    for cid, emb in candidates:
        score = cosine_similarity(query_embedding, emb)
        if score >= threshold:
            scores.append((cid, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:k]
