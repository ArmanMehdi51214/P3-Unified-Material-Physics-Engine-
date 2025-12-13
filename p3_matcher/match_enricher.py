from typing import Dict, List

from p3_core.types import CddaItem
from p3_matcher.match_result import MatchResult


class MatchEnricher:
    """
    Attaches physics data from CDDA items
    to existing match results.
    """

    def __init__(self, cdda_index: Dict[str, CddaItem]):
        """
        cdda_index: cdda_id -> CddaItem
        """
        self.cdda_index = cdda_index

    def enrich(
        self,
        matches: List[MatchResult],
    ) -> List[MatchResult]:
        """
        Adds physics to MatchResult.metadata
        """
        enriched: List[MatchResult] = []

        for match in matches:
            item = self.cdda_index.get(match.cdda_id)

            if not item or not item.physics:
                enriched.append(match)
                continue

            # attach physics safely
            match.metadata = match.metadata or {}
            match.metadata["physics"] = item.physics

            enriched.append(match)

        return enriched
