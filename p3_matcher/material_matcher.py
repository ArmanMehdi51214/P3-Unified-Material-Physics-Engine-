from typing import List

from p3_core.types import WikidataMaterial, CddaItem
from p3_matcher.match_result import MatchResult
from p3_embeddings.matcher_utils import cosine_similarity


class MaterialMatcher:
    """
    Rosetta-Stone matcher between Wikidata materials and CDDA items
    using embedding similarity.
    """

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def match(
        self,
        wikidata_materials: List[WikidataMaterial],
        cdda_items: List[CddaItem],
    ) -> List[MatchResult]:

        results: List[MatchResult] = []

        for material in wikidata_materials:
            if material.embedding is None:
                continue

            best_score = 0.0
            best_item = None

            for item in cdda_items:
                if item.embedding is None:
                    continue

                score = cosine_similarity(material.embedding, item.embedding)

                if score > best_score:
                    best_score = score
                    best_item = item

            if best_item is None:
                continue

            results.append(
                MatchResult(
                    wikidata_id=material.qid,
                    cdda_id=best_item.id,
                    confidence_score=best_score,
                    review_needed=best_score < self.threshold,
                )
            )

        return results
