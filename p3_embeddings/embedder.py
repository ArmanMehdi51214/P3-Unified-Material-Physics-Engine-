from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer


class MiniLMEmbedder:
    """
    Central embedding engine for Project P3.

    Uses sentence-transformers/all-MiniLM-L6-v2
    to convert text into dense vector embeddings.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize: bool = True,
        batch_size: int = 32,
    ):
        """
        Parameters
        ----------
        model_name : str
            HuggingFace model name.
        normalize : bool
            Whether to L2-normalize embeddings (recommended for cosine similarity).
        batch_size : int
            Batch size for embedding large datasets.
        """
        self.model_name = model_name
        self.normalize = normalize
        self.batch_size = batch_size

        # Load model once
        self.model = SentenceTransformer(model_name)

    def embed(
        self,
        texts: Union[str, List[str]],
    ) -> np.ndarray:
        """
        Generate embeddings for a single string or list of strings.

        Parameters
        ----------
        texts : str or List[str]
            Input text(s) to embed.

        Returns
        -------
        np.ndarray
            Embedding vector(s) with shape:
            - (dim,) for single string
            - (n, dim) for list
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
            show_progress_bar=False,
        )

        return np.asarray(embeddings)

    def embedding_dim(self) -> int:
        """
        Returns embedding dimensionality.
        """
        return self.model.get_sentence_embedding_dimension()
