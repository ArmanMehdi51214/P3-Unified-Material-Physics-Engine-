from dataclasses import dataclass


@dataclass
class MatchResult:
    wikidata_id: str
    cdda_id: str
    confidence_score: float
    review_needed: bool
